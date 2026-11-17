import os
import json
import logging
from typing import Dict, Any

# Configure simple logging
logger = logging.getLogger(__name__)

def generate_rewritten_resume(resume_text: str, job_description: str, metrics: Dict[str, Any], scoring: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a rewritten resume based on the original resume text and job description.
    Uses Gemini API if GEMINI_API_KEY is available in the environment,
    otherwise falls back to a realistic rule-based mock generator.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=api_key)
            
            prompt = f"""
            You are an expert ATS resume optimizer and career coach.
            Given the following resume text and a job description, rewrite the resume into structured JSON.
            Focus on quantifying achievements, incorporating the missing keywords, and enhancing readability.
            
            Job Description:
            {job_description}
            
            Original Resume Text:
            {resume_text}
            
            Missing Keywords to include if possible: {', '.join(scoring.get('missing_skills', []))}
            
            Please output ONLY a valid JSON object matching this structure:
            {{
                "summary": "A powerful 2-3 sentence professional summary tailored to the job.",
                "experience": [
                    {{
                        "role": "Job Title",
                        "company": "Company Name",
                        "bullets": [
                            "Bullet point 1 using action verbs and metrics.",
                            "Bullet point 2..."
                        ]
                    }}
                ],
                "skills": ["Skill 1", "Skill 2"]
            }}
            """
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            
            try:
                result = json.loads(response.text)
                return result
            except json.JSONDecodeError:
                logger.error("Failed to parse Gemini response as JSON. Falling back to mock.")
                # Fallthrough to mock
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}. Falling back to mock generator.")
            # Fallthrough to mock
            
    # Mock Generator Fallback
    missing = scoring.get("missing_skills", [])
    matched = scoring.get("matched_skills", [])
    
    summary = "Experienced professional with a proven track record of delivering high-quality results. "
    if job_description:
        summary += "Highly motivated to leverage my skills to contribute effectively to this role."
    else:
        summary += "Seeking a challenging position to utilize my expertise."
        
    mock_result = {
        "summary": summary,
        "experience": [
            {
                "role": "Senior Professional",
                "company": "Previous Company",
                "bullets": [
                    f"Spearheaded initiatives utilizing {matched[0] if matched else 'industry best practices'}, resulting in a 20% increase in efficiency.",
                    f"Collaborated with cross-functional teams to integrate {', '.join(missing[:2]) if missing else 'new methodologies'} into the core workflow.",
                    "Mentored junior team members and fostered a culture of continuous improvement."
                ]
            }
        ],
        "skills": matched + missing
    }
    
    return mock_result
