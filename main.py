"""
main.py — FastAPI Backend for Cataract Detection
Run with: uvicorn main:app --reload --port 8000
API docs: http://127.0.0.1:8000/docs
"""

from contextlib import asynccontextmanager
from io import BytesIO

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel

from database import (
    init_db,
    create_patient,
    get_all_patients,
    get_patient_by_id,
    search_patients,
    save_prediction,
    get_patient_history,
    get_all_predictions,
)
from predict import load_model, predict as run_predict

# ── Model state ───────────────────────────────────────────────────────────────
_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Init DB and load model on startup."""
    init_db()
    print("✅ Database initialised.")
    global _model
    _model = load_model("best_cataract_model.pth")
    print("✅ Model loaded and ready.")
    yield
    _model = None
    print("🛑 Model released.")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="EyeShield — Cataract Detection API",
    description=(
        "Upload a retinal fundus image and get a cataract prediction "
        "powered by a MobileNetV2 deep learning model. "
        "Predictions are stored per-patient for history tracking."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────────────────────
class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    contact: str = ""


class PredictionResponse(BaseModel):
    prediction_id: int
    patient_id: int
    label: str
    confidence: float
    probabilities: dict[str, float]


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "EyeShield API is running"}


@app.get("/health", tags=["Health"])
def health():
    return {"model_loaded": _model is not None}


# ── Patients ──────────────────────────────────────────────────────────────────
@app.post("/patients", tags=["Patients"])
def add_patient(data: PatientCreate):
    """Register a new patient."""
    patient_id = create_patient(data.name, data.age, data.gender, data.contact)
    return {"patient_id": patient_id, "message": f"Patient '{data.name}' registered."}


@app.get("/patients", tags=["Patients"])
def list_patients():
    """List all registered patients."""
    return get_all_patients()


@app.get("/patients/search", tags=["Patients"])
def search(query: str):
    """Search patients by name or contact number."""
    return search_patients(query)


@app.get("/patients/{patient_id}", tags=["Patients"])
def get_patient(patient_id: int):
    """Get a single patient's details."""
    patient = get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")
    return patient


@app.get("/patients/{patient_id}/history", tags=["Patients"])
def patient_history(patient_id: int):
    """Get full scan history for a patient."""
    patient = get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")
    history = get_patient_history(patient_id)
    return {"patient": patient, "scans": history, "total_scans": len(history)}


# ── Predictions ───────────────────────────────────────────────────────────────
@app.post("/patients/{patient_id}/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict(patient_id: int, file: UploadFile = File(...)):
    """
    Upload an eye image for a specific patient and get a cataract prediction.
    The result is saved to the database automatically.
    """
    if not get_patient_by_id(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found.")

    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Use JPG or PNG.",
        )

    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet.")

    contents = await file.read()
    try:
        image = Image.open(BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read image file.")

    result = run_predict(image, _model)
    pred_id = save_prediction(patient_id, result)

    return PredictionResponse(
        prediction_id=pred_id,
        patient_id=patient_id,
        **result,
    )


@app.get("/predictions", tags=["Predictions"])
def all_predictions():
    """Get all predictions across all patients."""
    return get_all_predictions()
