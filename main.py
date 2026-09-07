from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Form, UploadFile, File, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import aiofiles
from pathlib import Path

import models
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Livestock Health API")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/triage")
async def run_ai_triage(
    symptoms: str = Form(...), 
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    if image and image.filename:
        file_path = UPLOAD_DIR / image.filename
        async with aiofiles.open(file_path, "wb") as buffer:
            while content := await image.read(1024 * 1024): 
                await buffer.write(content)
                
    symptoms_lower = symptoms.lower()
    if "fever" in symptoms_lower or "lesion" in symptoms_lower or "blister" in symptoms_lower:
        diagnosis = "⚠️ High Probability of Foot-and-Mouth Disease (FMD)"
        action = "Isolate the animal immediately."
    else:
        diagnosis = "✅ No critical contagious symptoms detected."
        action = "Monitor for 24 hours. Ensure hydration."
        
    record = models.TriageRecord(
        symptoms=symptoms,
        diagnosis=diagnosis,
        recommended_action=action
    )
    db.add(record)
    db.commit()
    
    return {"diagnosis": diagnosis, "recommended_action": action}
@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    # Fetch all saved records from the database
    records = db.query(models.TriageRecord).all()
    return templates.TemplateResponse(request=request, name="admin.html", context={"records": records})

@app.get("/vaccines", response_class=HTMLResponse)
async def vaccine_dashboard(request: Request, db: Session = Depends(get_db)):
    schedules = db.query(models.VaccinationSchedule).all()
    return templates.TemplateResponse(request=request, name="vaccine.html", context={"schedules": schedules})

@app.post("/api/schedule")
async def generate_schedule(
    animal_tag: str = Form(...),
    birth_date: str = Form(...),
    db: Session = Depends(get_db)
):
    birth = datetime.strptime(birth_date, "%Y-%m-%d")
    
    # Calculate standard schedule dates
    v1 = models.VaccinationSchedule(
        animal_tag=animal_tag, 
        vaccine_name="Foot-and-Mouth Disease (FMD)", 
        scheduled_date=(birth + timedelta(days=120)).strftime("%Y-%m-%d")
    )
    v2 = models.VaccinationSchedule(
        animal_tag=animal_tag, 
        vaccine_name="Brucellosis", 
        scheduled_date=(birth + timedelta(days=180)).strftime("%Y-%m-%d")
    )
    
    db.add_all([v1, v2])
    db.commit()
    
    return {"message": "Success"}

@app.get("/tele-vet", response_class=HTMLResponse)
async def tele_vet_portal(request: Request, db: Session = Depends(get_db)):
    # Fetch all booked appointments
    appointments = db.query(models.VetAppointment).all()
    return templates.TemplateResponse(request=request, name="vet.html", context={"appointments": appointments})

@app.post("/api/book-vet")
async def book_appointment(
    farmer_name: str = Form(...),
    animal_tag: str = Form(...),
    appointment_date: str = Form(...),
    issue: str = Form(...),
    db: Session = Depends(get_db)
):
    appointment = models.VetAppointment(
        farmer_name=farmer_name,
        animal_tag=animal_tag,
        appointment_date=appointment_date,
        issue_description=issue
    )
    db.add(appointment)
    db.commit()
    return {"message": "Success"}
