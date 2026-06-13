<div align="center">

# 👁 EyeShield

### AI-Powered Cataract Detection & Patient Monitoring System

A full-stack deep learning application that screens retinal images for cataracts using a fine-tuned **MobileNetV2** model, tracks patient history, generates downloadable PDF reports, and ships with secure authentication — all wrapped in a sleek, custom-themed Streamlit dashboard.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.2.2-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-3FCF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](#-license)

</div>

---

## ✨ Features

- 🔬 **AI Cataract Screening** — Upload a retinal fundus image and get an instant prediction (Cataract / Normal) with confidence scores and class probabilities
- 🧠 **MobileNetV2 Deep Learning Model** — Lightweight, fine-tuned CNN with ~98% test accuracy
- 👤 **Patient Management** — Register new patients or search existing records by name/contact
- 📜 **Scan History & Timeline** — Every prediction is saved per-patient for longitudinal monitoring
- 📊 **Live Dashboard** — KPI cards for total patients, screenings, cataract cases, and detection rate
- 📄 **PDF Report Generation** — Download a clean, professional diagnostic report for any scan
- 🔐 **Secure Authentication** — Email/password login & registration powered by Supabase
- 🎨 **Custom Themed UI** — A distinctive lemon/lime/black "bioluminescent lab" aesthetic, fully built with custom CSS over Streamlit
- ⚡ **Decoupled Architecture** — FastAPI backend (model inference + database) + Streamlit frontend (UI)

---

## 🏗 Architecture

```
┌─────────────────────┐        REST API        ┌──────────────────────┐
│   Streamlit Frontend │ ◄─────────────────────► │   FastAPI Backend    │
│       (app.py)       │      JSON / multipart   │      (main.py)       │
└─────────┬────────────┘                         └──────────┬───────────┘
          │                                                  │
          │ auth (email/password)                           │ inference
          ▼                                                  ▼
┌─────────────────────┐                         ┌──────────────────────┐
│      Supabase        │                         │   predict.py          │
│  (auth + database)    │                         │  MobileNetV2 model     │
└─────────────────────┘                         │ (best_cataract_model.pth) │
                                                  └──────────────────────┘
```

---

## 📁 Project Structure

```
eyeshield/
├── app.py                     # Streamlit frontend — UI, auth, PDF reports
├── main.py                    # FastAPI backend — REST endpoints
├── predict.py                 # Model architecture + inference pipeline
├── database.py                # Database layer (Supabase queries)
├── best_cataract_model.pth    # Trained model weights
├── requirements.txt           # Python dependencies
├── .env                        # Environment variables (not committed)
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python **3.12**
- A [Supabase](https://supabase.com/) project (for auth + patient/scan storage)
- Trained model weights file: `best_cataract_model.pth`

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/eyeshield.git
cd eyeshield
```

### 2. Create a virtual environment

```bash
py -3.12 -m venv cataract_env

# Windows
cataract_env\Scripts\activate

# macOS / Linux
source cataract_env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_api_key
```

### 5. Run the application

**Terminal 1 — start the backend:**
```bash
uvicorn main:app --reload --port 8000
```

**Terminal 2 — start the frontend:**
```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**
API docs available at **http://127.0.0.1:8000/docs**

---

## 🧠 Model Details

| Property | Value |
|---|---|
| Architecture | MobileNetV2 (frozen backbone) + custom classifier head |
| Classifier Head | `Linear(1280, 500) → ReLU → Dropout(0.2) → Linear(500, 2)` |
| Input Size | 224 × 224 |
| Classes | `cataract`, `normal` |
| Normalization | ImageNet mean/std |
| Test Accuracy | ~98% |

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Check model load status |
| `POST` | `/patients` | Register a new patient |
| `GET` | `/patients` | List all patients |
| `GET` | `/patients/search?query=` | Search patients by name/contact |
| `GET` | `/patients/{id}` | Get patient details |
| `GET` | `/patients/{id}/history` | Get a patient's scan history |
| `POST` | `/patients/{id}/predict` | Upload an image & get a prediction |
| `GET` | `/predictions` | Get all predictions across patients |

Interactive Swagger docs are available at `/docs` once the backend is running.

---

## 🖥 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit + custom CSS |
| Backend | FastAPI, Uvicorn |
| ML Framework | PyTorch, Torchvision |
| Database & Auth | Supabase |
| PDF Reports | ReportLab |
| Image Processing | Pillow |
| Data Handling | Pandas, NumPy |

---

## ⚠️ Disclaimer

This project is intended for **educational and research purposes only**. It is **not a certified medical device** and must not be used as a substitute for professional medical diagnosis or advice. Always consult a qualified ophthalmologist for eye health concerns.

---

## 📜 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute with attribution.

---
## 👤 Authors

Vaishnavi Choudhari

Sanganna Jalade

<div align="center">

**Built with 🩺 PyTorch · FastAPI · Streamlit · Supabase**

</div>
