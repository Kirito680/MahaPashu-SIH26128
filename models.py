from sqlalchemy import Column, Integer, String, Text
from database import Base

class TriageRecord(Base):
    __tablename__ = "triage_records"
    id = Column(Integer, primary_key=True, index=True)
    symptoms = Column(Text, nullable=False)
    diagnosis = Column(String, nullable=False)
    recommended_action = Column(String, nullable=False)

class VaccinationSchedule(Base):
    __tablename__ = "vaccination_schedules"
    id = Column(Integer, primary_key=True, index=True)
    animal_tag = Column(String, index=True)
    vaccine_name = Column(String, nullable=False)
    scheduled_date = Column(String, nullable=False)
    status = Column(String, default="Pending")

class VetAppointment(Base):
    __tablename__ = "vet_appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_name = Column(String, nullable=False)
    animal_tag = Column(String, nullable=False)
    appointment_date = Column(String, nullable=False)
    issue_description = Column(Text, nullable=False)
    status = Column(String, default="Scheduled")