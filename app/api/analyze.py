from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlmodel import Session
import os
import uuid
import json
import shutil
from pydantic import BaseModel
from app.core.db import get_session
from app.core.deps import get_current_user
from app.models.domain import User, Resume, AnalysisReport
from app.services.resume_parser import parse_resume_file
from app.services.ats_scorer import calculate_score
from app.services.ai_service import generate_rewritten_resume

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class RescoreRequest(BaseModel):
    job_description: str

class GenerateRequest(BaseModel):
    job_description: str
    target_skills: list[str] = []

@router.post("")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(default=""),
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(400, "Only PDF and DOCX files are supported")
        
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    save_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    db_resume = Resume(user_id=user.id, filename=file.filename, file_path=save_path, file_type=ext)
    session.add(db_resume)
    session.commit()
    session.refresh(db_resume)
    
    # 1. Parse File
    extracted_text, raw_data = parse_resume_file(save_path)
    
    # 2. Analyze & Score
    score_data = calculate_score(extracted_text, job_description)
    
    # Combine results
    full_result = {
        "raw_text": extracted_text,
        "metrics": raw_data,
        "scoring": score_data
    }
    
    # 3. Save Report
    rebuilt_json_data = generate_rewritten_resume(
        resume_text=extracted_text, 
        job_description=job_description, 
        metrics=raw_data, 
        scoring=score_data
    )
    
    report = AnalysisReport(
        user_id=user.id,
        resume_id=db_resume.id,
        job_description=job_description,
        overall_score=score_data.get("overall_score", 0),
        result_json=json.dumps(full_result),
        rebuilt_json=json.dumps(rebuilt_json_data)
    )
    session.add(report)
    session.commit()
    session.refresh(report)
    
    return {"success": True, "analysis_id": report.id}

@router.get("/{analysis_id}")
async def get_analysis(analysis_id: str, session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    report = session.get(AnalysisReport, analysis_id)
    if not report or report.user_id != user.id:
        raise HTTPException(404, "Report not found")
        
    return {
        "success": True,
        "data": {
            "id": report.id,
            "resume": {"filename": report.resume.filename},
            "overall_score": report.overall_score,
            "job_description": report.job_description,
            "result": json.loads(report.result_json),
            "rebuilt": json.loads(report.rebuilt_json) if report.rebuilt_json else {}
        }
    }

class RebuiltData(BaseModel):
    rebuilt_json: dict

@router.put("/{analysis_id}/rebuilt")
async def save_rebuilt_resume(
    analysis_id: str, 
    data: RebuiltData,
    session: Session = Depends(get_session), 
    user: User = Depends(get_current_user)
):
    report = session.get(AnalysisReport, analysis_id)
    if not report or report.user_id != user.id:
        raise HTTPException(404, "Report not found")
        
    report.rebuilt_json = json.dumps(data.rebuilt_json)
    session.add(report)
    session.commit()
    
    return {"success": True}

@router.post("/{analysis_id}/rescore")
async def live_rescore_analysis(
    analysis_id: str,
    req: RescoreRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Real-time live re-scoring against custom or updated Job Description."""
    report = session.get(AnalysisReport, analysis_id)
    if not report or report.user_id != user.id:
        raise HTTPException(404, "Report not found")
        
    result_data = json.loads(report.result_json)
    raw_text = result_data.get("raw_text", "")
    
    # Recalculate score with new JD
    new_scoring = calculate_score(raw_text, req.job_description)
    
    # Update and persist
    result_data["scoring"] = new_scoring
    report.overall_score = new_scoring["overall_score"]
    report.job_description = req.job_description
    report.result_json = json.dumps(result_data)
    
    session.add(report)
    session.commit()
    
    return {
        "success": True,
        "overall_score": report.overall_score,
        "scoring": new_scoring
    }

@router.post("/{analysis_id}/tailor")
async def tailor_and_generate(
    analysis_id: str,
    req: GenerateRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user)
):
    """Regenerate tailored resume optimized specifically for the missing skills."""
    report = session.get(AnalysisReport, analysis_id)
    if not report or report.user_id != user.id:
        raise HTTPException(404, "Report not found")
        
    result_data = json.loads(report.result_json)
    raw_text = result_data.get("raw_text", "")
    scoring = calculate_score(raw_text, req.job_description)
    
    rebuilt_json = generate_rewritten_resume(
        resume_text=raw_text,
        job_description=req.job_description,
        metrics=result_data.get("metrics", {}),
        scoring=scoring
    )
    
    # Save newly tailored version
    report.rebuilt_json = json.dumps(rebuilt_json)
    report.overall_score = scoring["overall_score"]
    report.job_description = req.job_description
    result_data["scoring"] = scoring
    report.result_json = json.dumps(result_data)
    
    session.add(report)
    session.commit()
    
    return {
        "success": True,
        "rebuilt": rebuilt_json,
        "scoring": scoring
    }
