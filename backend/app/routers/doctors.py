"""
Doctors router for managing doctor information
"""
from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter()

class Doctor(BaseModel):
    id: int
    name: str
    specialty: str
    experience: str
    qualifications: str
    about: str

# Algerian Arabic doctor names
DOCTORS_DATA = [
    {
        "id": 1,
        "name": "د. أحمد بومدين",
        "specialty": "Cardiology",
        "experience": "15 years",
        "qualifications": "MD, FACC",
        "about": "Specialized in preventive cardiology and heart disease management with a focus on patient education."
    },
    {
        "id": 2,
        "name": "د. فاطمة الزهراء",
        "specialty": "Pediatrics",
        "experience": "12 years",
        "qualifications": "MD, FAAP",
        "about": "Dedicated to providing comprehensive care for children from infancy through adolescence."
    },
    {
        "id": 3,
        "name": "د. محمد بن علي",
        "specialty": "Dermatology",
        "experience": "10 years",
        "qualifications": "MD, FAAD",
        "about": "Expert in medical and cosmetic dermatology with advanced training in skin cancer treatment."
    },
    {
        "id": 4,
        "name": "د. خديجة مبارك",
        "specialty": "Orthopedics",
        "experience": "18 years",
        "qualifications": "MD, FAAOS",
        "about": "Specializes in sports medicine and minimally invasive orthopedic surgery."
    },
    {
        "id": 5,
        "name": "د. عمر طاهر",
        "specialty": "Internal Medicine",
        "experience": "14 years",
        "qualifications": "MD, FACP",
        "about": "Focused on adult medicine, chronic disease management, and preventive healthcare."
    },
    {
        "id": 6,
        "name": "د. آمنة سعيد",
        "specialty": "Neurology",
        "experience": "16 years",
        "qualifications": "MD, PhD, FAAN",
        "about": "Expert in treating neurological disorders including migraines, epilepsy, and movement disorders."
    },
    {
        "id": 7,
        "name": "د. يوسف قاسم",
        "specialty": "Obstetrics & Gynecology",
        "experience": "11 years",
        "qualifications": "MD, FACOG",
        "about": "Provides comprehensive women's healthcare including prenatal care and minimally invasive surgery."
    },
    {
        "id": 8,
        "name": "د. نور الهدى",
        "specialty": "Psychiatry",
        "experience": "13 years",
        "qualifications": "MD, FAPA",
        "about": "Specializes in mood disorders, anxiety, and integrative mental health treatment approaches."
    },
]

@router.get("/", response_model=List[Doctor])
async def get_doctors():
    """Get all doctors"""
    return DOCTORS_DATA

@router.get("/{doctor_id}", response_model=Doctor)
async def get_doctor(doctor_id: int):
    """Get a specific doctor by ID"""
    doctor = next((d for d in DOCTORS_DATA if d["id"] == doctor_id), None)
    if not doctor:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor



