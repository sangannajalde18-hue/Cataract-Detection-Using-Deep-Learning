"""
database.py — Supabase database operations
Tables: patients, predictions
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


# ── Init ──────────────────────────────────────────────────────────────────────
def init_db():
    """Verify Supabase connection. Tables are created via SQL editor."""
    try:
        get_client().table("patients").select("id").limit(1).execute()
        print("✅ Supabase connected successfully.")
    except Exception as e:
        print(f"⚠️  Supabase connection error: {e}")


# ── Patient operations ────────────────────────────────────────────────────────
def create_patient(name: str, age: int, gender: str, contact: str = "") -> int:
    """Insert a new patient and return their ID."""
    data = {
        "name": name,
        "age": age,
        "gender": gender,
        "contact": contact,
        "created_at": datetime.now().isoformat(),
    }
    response = get_client().table("patients").insert(data).execute()
    return response.data[0]["id"]


def get_all_patients() -> list[dict]:
    """Return all patients as a list of dicts."""
    response = get_client().table("patients").select("*").order("created_at", desc=True).execute()
    return response.data


def get_patient_by_id(patient_id: int) -> dict | None:
    """Return a single patient by ID."""
    response = get_client().table("patients").select("*").eq("id", patient_id).execute()
    return response.data[0] if response.data else None


def search_patients(query: str) -> list[dict]:
    """Search patients by name or contact."""
    client = get_client()
    by_name = client.table("patients").select("*").ilike("name", f"%{query}%").execute().data
    by_contact = client.table("patients").select("*").ilike("contact", f"%{query}%").execute().data

    # Merge and deduplicate by id
    seen = set()
    results = []
    for row in by_name + by_contact:
        if row["id"] not in seen:
            seen.add(row["id"])
            results.append(row)
    return results


# ── Prediction operations ─────────────────────────────────────────────────────
def save_prediction(patient_id: int, result: dict) -> int:
    """Save a prediction result linked to a patient."""
    data = {
        "patient_id": patient_id,
        "label": result["label"],
        "confidence": result["confidence"],
        "cataract_prob": result["probabilities"]["cataract"],
        "normal_prob": result["probabilities"]["normal"],
        "scanned_at": datetime.now().isoformat(),
    }
    response = get_client().table("predictions").insert(data).execute()
    return response.data[0]["id"]


def get_patient_history(patient_id: int) -> list[dict]:
    """Return all predictions for a patient, newest first."""
    response = (
        get_client()
        .table("predictions")
        .select("*")
        .eq("patient_id", patient_id)
        .order("scanned_at", desc=True)
        .execute()
    )
    return response.data


def get_all_predictions() -> list[dict]:
    """Return all predictions joined with patient info."""
    response = (
        get_client()
        .table("predictions")
        .select("*, patients(name, age, gender)")
        .order("scanned_at", desc=True)
        .execute()
    )
    # Flatten the nested patient data to match old SQLite format
    results = []
    for row in response.data:
        patient = row.pop("patients", {}) or {}
        row["patient_name"] = patient.get("name", "")
        row["age"] = patient.get("age", "")
        row["gender"] = patient.get("gender", "")
        results.append(row)
    return results
