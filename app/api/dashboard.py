from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, select
from app.core.db import get_session
from app.core.deps import get_current_user
from app.models.domain import User, Resume, AnalysisReport

router = APIRouter()

@router.get("/stats")
async def get_stats(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    analyses = session.exec(select(AnalysisReport).where(AnalysisReport.user_id == user.id)).all()
    
    total = len(analyses)
    avg_score = sum(a.overall_score for a in analyses) / total if total > 0 else 0
    latest = analyses[-1].overall_score if total > 0 else 0
    
    recent = []
    for a in sorted(analyses, key=lambda x: x.created_at, reverse=True)[:5]:
        recent.append({
            "id": a.id,
            "filename": a.resume.filename,
            "score": a.overall_score,
            "date": a.created_at.isoformat()
        })
        
    return {
        "total_scans": total,
        "avg_score": round(avg_score, 1),
        "latest_score": round(latest, 1),
        "recent": recent
    }
