from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select
from app.core.db import get_session
from app.core.deps import get_current_user
from app.models.domain import User, AnalysisReport
from pydantic import BaseModel
import re
import json
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class JDInput(BaseModel):
    resume_text: str = ""
    job_description: str = ""

def get_latest_context(input_data: JDInput, user: User, session: Session):
    # If the frontend sends the generic 'sample', pull from DB
    if input_data.resume_text == "sample" or not input_data.resume_text:
        # Get latest report
        report = session.exec(
            select(AnalysisReport)
            .where(AnalysisReport.user_id == user.id)
            .order_by(AnalysisReport.created_at.desc())
        ).first()
        
        if not report:
            raise HTTPException(400, "No resume analyzed yet. Please analyze a resume first.")
            
        try:
            result = json.loads(report.result_json)
            raw_text = result.get("raw_text", "")
            skills = result.get("scoring", {}).get("matched_skills", []) + result.get("scoring", {}).get("missing_skills", [])
        except:
            raw_text = ""
            skills = []
            
        return raw_text, report.job_description or "", skills
        
    return input_data.resume_text, input_data.job_description, []

def call_gemini(prompt: str, fallback_result: dict):
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return fallback_result
    return fallback_result


@router.post("/cover-letter")
async def generate_cover_letter(input_data: JDInput, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    resume_text, job_description, skills = get_latest_context(input_data, user, session)
    
    prompt = f"""
    You are an expert career coach. Write a professional, compelling cover letter for the following job description based on the candidate's resume.
    Job Description: {job_description}
    Resume Extract: {resume_text[:2000]}
    
    Output JSON:
    {{
        "draft": "The full cover letter text...",
        "note": "A short note about what to customize."
    }}
    """
    
    skill_str = ", ".join(skills[:5]) if skills else "my diverse background"
    fallback = {
        "draft": f"Dear Hiring Manager,\n\nI am thrilled to apply for the open position at your company. With my strong background and proven expertise in areas such as {skill_str}, I am confident in my ability to deliver immediate value to your team.\n\nMy attached resume outlines my professional achievements. I would welcome the opportunity to discuss how my specific skills align with your strategic goals.\n\nSincerely,\n{user.name}",
        "note": "This is a heuristic template based on your top skills. Add a Gemini API key for fully AI-generated letters."
    }
    
    return call_gemini(prompt, fallback)


@router.post("/interview-prep")
async def generate_interview_prep(input_data: JDInput, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    resume_text, job_description, skills = get_latest_context(input_data, user, session)
    
    prompt = f"""
    You are a technical recruiter. Based on the candidate's resume and target job, generate 5 highly specific behavioral and technical interview questions.
    Job Description: {job_description}
    Resume: {resume_text[:2000]}
    
    Output JSON:
    {{
        "questions": ["Q1...", "Q2...", "Q3...", "Q4...", "Q5..."],
        "note": "Brief advice on how to prepare."
    }}
    """
    
    skill = skills[0] if skills else "your field"
    fallback = {
        "questions": [
            f"1. Tell me about a time you used {skill} to solve a critical business problem.",
            "2. Can you walk me through the most complex project on your resume?",
            "3. How do you handle disagreements with stakeholders regarding technical decisions?",
            "4. Describe a situation where you had to quickly learn a new technology or domain.",
            "5. What makes you uniquely qualified for this specific position?"
        ],
        "note": "These are heuristic behavioral questions tailored to your primary skill. Add a Gemini API key for advanced JD-specific questions."
    }
    
    return call_gemini(prompt, fallback)


@router.post("/skill-gap")
async def generate_skill_gap(input_data: JDInput, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    resume_text, job_description, skills = get_latest_context(input_data, user, session)
    
    if not job_description:
        return {
            "questions": [
                "No Job Description provided.",
                "To run a skill gap analysis, you must upload your resume against a target job description."
            ],
            "note": "Missing JD context."
        }

    prompt = f"""
    You are an expert technical assessor. Compare this resume against the job description and identify exactly what skills the candidate is missing, and provide a 3-step action plan to bridge the gap.
    JD: {job_description}
    Resume: {resume_text[:2000]}
    
    Output JSON:
    {{
        "draft": "Summary of missing skills...",
        "questions": ["Action Step 1...", "Action Step 2...", "Action Step 3..."],
        "note": "Closing encouraging remark."
    }}
    """
    
    fallback = {
        "draft": "We detected some gaps between your profile and the JD requirements.",
        "questions": [
            "1. Review the required tech stack in the JD and identify exactly which tools you lack.",
            "2. Complete a quick crash course or build a small project using the primary missing tool.",
            "3. Update your resume to include this new project to demonstrate baseline competency."
        ],
        "note": "Heuristic gap analysis. Add a Gemini API key for deep semantic comparison."
    }
    
    return call_gemini(prompt, fallback)
