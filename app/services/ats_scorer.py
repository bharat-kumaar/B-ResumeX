import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except (ImportError, OSError):
    logger.warning("Spacy model 'en_core_web_sm' not available. Falling back to regex parser.")
    SPACY_AVAILABLE = False

# High-impact power action verbs commonly favored by enterprise ATS & recruiters
POWER_ACTION_VERBS = {
    "architected", "engineered", "championed", "orchestrated", "spearheaded",
    "implemented", "developed", "accelerated", "maximized", "streamlined",
    "scaled", "optimized", "delivered", "transformed", "pioneered",
    "designed", "reduced", "increased", "deployed", "automated",
    "managed", "led", "established", "formulated", "navigated"
}

# Common tech & domain taxonomy keywords
TECH_SKILLS_TAXONOMY = {
    "python", "javascript", "typescript", "react", "vue", "angular", "node", "nodejs",
    "fastapi", "django", "flask", "docker", "kubernetes", "aws", "azure", "gcp",
    "sql", "postgresql", "mysql", "mongodb", "redis", "graphql", "rest", "api", "apis",
    "ci/cd", "git", "github", "linux", "machine learning", "deep learning", "nlp",
    "pytorch", "tensorflow", "pandas", "numpy", "scikit-learn", "microservices",
    "distributed systems", "agile", "scrum", "devops", "cloud", "security", "terraform"
}

def extract_keywords(text: str) -> set:
    if not text:
        return set()
        
    text_lower = text.lower()
    keywords = set()

    if SPACY_AVAILABLE:
        doc = nlp(text_lower)
        for token in doc:
            if (token.pos_ in ["NOUN", "PROPN"] or token.text in TECH_SKILLS_TAXONOMY) and not token.is_stop and len(token.text) > 1:
                keywords.add(token.lemma_.lower() if token.lemma_ != "-PRON-" else token.text.lower())
    else:
        words = re.findall(r'\b[a-z]{3,}\b', text_lower)
        keywords = set(words)
        
    # Also capture recognized multi-word phrases or direct taxonomy matches
    for tech in TECH_SKILLS_TAXONOMY:
        if tech in text_lower:
            keywords.add(tech)
            
    return keywords

def calculate_score(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Advanced multi-vector ATS scoring algorithm:
    1. Hard Keywords Alignment (40%)
    2. Quantifiable Impact & Metrics (20%)
    3. Action Verb Power Index (20%)
    4. Structure & Section Completeness (10%)
    5. Readability & Formatting Density (10%)
    """
    resume_lower = (resume_text or "").lower()
    jd_lower = (job_description or "").lower()
    
    breakdown = {
        "keywords": 0,
        "impact_metrics": 0,
        "action_verbs": 0,
        "structure": 0,
        "readability": 0
    }
    
    # 1. Structure Check (Sections presence)
    sections = ["experience", "education", "skills", "summary", "projects"]
    found_sections = [s for s in sections if s in resume_lower]
    breakdown["structure"] = min(100, int((len(found_sections) / max(3, len(sections))) * 100))
    
    # 2. Readability & Word Count
    words = len(resume_text.split())
    if 250 <= words <= 900:
        breakdown["readability"] = 95
    elif 150 <= words < 250 or 900 < words <= 1200:
        breakdown["readability"] = 75
    else:
        breakdown["readability"] = 45

    # 3. Quantifiable Impact & Metrics Detector
    metric_matches = re.findall(r'(\b\d+[\d,.]*\s*(?:%|\+|k|m|million|billion|users|customers|queries|x|fps|ms|seconds|minutes|hours|days|dollars|\$)|(?:\$|€|£)\s*\d+[\d,.]*)', resume_lower)
    metric_count = len(metric_matches)
    if metric_count >= 6:
        breakdown["impact_metrics"] = 98
    elif metric_count >= 3:
        breakdown["impact_metrics"] = 80
    elif metric_count >= 1:
        breakdown["impact_metrics"] = 60
    else:
        breakdown["impact_metrics"] = 35

    # 4. Action Verb Power Index
    verb_matches = [v for v in POWER_ACTION_VERBS if re.search(r'\b' + v + r'\b', resume_lower)]
    verb_count = len(verb_matches)
    if verb_count >= 8:
        breakdown["action_verbs"] = 96
    elif verb_count >= 4:
        breakdown["action_verbs"] = 82
    elif verb_count >= 2:
        breakdown["action_verbs"] = 65
    else:
        breakdown["action_verbs"] = 40

    # 5. Keyword Alignment & Matcher
    matched_skills = []
    missing_skills = []
    
    if jd_lower.strip():
        jd_keywords = extract_keywords(jd_lower)
        res_keywords = extract_keywords(resume_lower)
        
        # Prioritize tech skills and distinct industry keywords
        jd_skills_priority = [k for k in jd_keywords if k in TECH_SKILLS_TAXONOMY]
        remaining_jd = [k for k in jd_keywords if k not in TECH_SKILLS_TAXONOMY and len(k) > 2]
        
        target_skills = list(dict.fromkeys(jd_skills_priority + remaining_jd))[:25]
        
        matched = [k for k in target_skills if k in res_keywords or k in resume_lower]
        missing = [k for k in target_skills if k not in matched]
        
        match_ratio = len(matched) / max(1, len(target_skills))
        breakdown["keywords"] = min(100, int(match_ratio * 100))
        matched_skills = matched
        missing_skills = missing
    else:
        # Default baseline if no JD supplied
        breakdown["keywords"] = 72
        res_keywords = extract_keywords(resume_lower)
        matched_skills = [k for k in res_keywords if k in TECH_SKILLS_TAXONOMY][:10]
        missing_skills = ["docker", "kubernetes", "ci/cd", "microservices"]

    # Compute Weighted Overall Score
    weighted_score = (
        (breakdown["keywords"] * 0.40) +
        (breakdown["impact_metrics"] * 0.20) +
        (breakdown["action_verbs"] * 0.20) +
        (breakdown["structure"] * 0.10) +
        (breakdown["readability"] * 0.10)
    )
    
    final_score = min(99, max(20, int(weighted_score)))
    
    # Generate proactive suggestions
    recommendations = []
    if missing_skills:
        top_missing = ", ".join(missing_skills[:4])
        recommendations.append(f"Incorporate high-priority target skills: {top_missing}.")
    if metric_count < 3:
        recommendations.append("Strengthen accomplishments with quantified metrics (e.g., 'reduced latency by 35%', 'scaled to 50k users').")
    if verb_count < 4:
        recommendations.append("Begin bullet points with power action verbs like 'Architected', 'Spearheaded', or 'Automated'.")
    if len(found_sections) < 4:
        recommendations.append("Ensure distinct section headers for Summary, Experience, Skills, and Projects.")

    return {
        "overall_score": final_score,
        "breakdown": breakdown,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "quantified_metrics_found": metric_count,
        "power_verbs_found": verb_matches[:8],
        "recommendations": recommendations
    }
