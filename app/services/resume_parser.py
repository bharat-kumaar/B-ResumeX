import pdfplumber
import docx2txt
import spacy
from typing import Tuple, Dict, Any

nlp = spacy.load("en_core_web_sm")

def extract_text(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text
    elif file_path.endswith(".docx"):
        return docx2txt.process(file_path)
    return ""

def parse_resume_file(file_path: str) -> Tuple[str, Dict[str, Any]]:
    text = extract_text(file_path)
    
    # Basic metrics
    word_count = len(text.split())
    
    # NLP extraction
    doc = nlp(text)
    entities = {}
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        entities[ent.label_].append(ent.text)
        
    metrics = {
        "word_count": word_count,
        "entities": entities
    }
    
    return text, metrics
