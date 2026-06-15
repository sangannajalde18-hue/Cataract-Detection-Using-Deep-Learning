"""
EyeShield — AI Cataract Detection
Palette: Lemon Yellow · Lime Green · Dark Yellow · Black

Run backend  : uvicorn main:app --reload --port 8000
Run frontend : streamlit run app.py
"""

import io
import os
import base64
from datetime import datetime

import requests
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from supabase import create_client, Client
from fpdf import FPDF, XPos, YPos

# ── Supabase auth client ──────────────────────────────────────────────────────
load_dotenv()
_supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY"),
)

BASE_URL = "https://eyeshield-api.onrender.com"

st.set_page_config(
    page_title="EyeShield — Cataract Detection",
    page_icon="👁",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

:root {
  --black:      #080900;
  --black2:     #0f1100;
  --black3:     #161800;
  --black4:     #1e2100;
  --lemon:      #E8FF00;
  --lime:       #A8E600;
  --green:      #2ECC40;
  --gold:       #C9A800;
  --gold-dim:   #7A6500;
  --lemon-dim:  rgba(232,255,0,0.08);
  --lime-dim:   rgba(168,230,0,0.08);
  --lemon-mid:  rgba(232,255,0,0.18);
  --text:       #E8FF00;
  --text-soft:  rgba(232,255,0,0.65);
  --muted:      rgba(232,255,0,0.28);
  --subtle:     rgba(232,255,0,0.08);
}

html, body, [class*="css"] {
  font-family: 'Space Grotesk', sans-serif;
  color: var(--text);
}

.stApp {
  background: var(--black);
  background-image:
    radial-gradient(ellipse 65% 45% at 10% 0%, rgba(168,230,0,0.07) 0%, transparent 60%),
    radial-gradient(ellipse 55% 40% at 90% 95%, rgba(232,255,0,0.05) 0%, transparent 55%),
    radial-gradient(ellipse 40% 30% at 50% 50%, rgba(46,204,64,0.03) 0%, transparent 70%);
}

.main .block-container {
  padding: 1.5rem 2.6rem 4rem;
  max-width: 1400px;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  background: var(--black2) !important;
  border-right: 1px solid rgba(168,230,0,0.12) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] hr { border-color: rgba(232,255,0,0.08) !important; }
[data-testid="stSidebar"] a { color: var(--lime) !important; }

/* ── TABS ── */
div[data-testid="stTabs"] [role="tablist"] {
  border-bottom: 1px solid rgba(168,230,0,0.15);
  gap: 2px;
}
div[data-testid="stTabs"] button {
  font-family: 'Space Mono', monospace !important;
  font-size: 0.68rem !important;
  letter-spacing: 0.1em !important;
  color: var(--muted) !important;
  background: transparent !important;
  border: none !important;
  padding: 10px 22px !important;
  border-radius: 4px 4px 0 0 !important;
  text-transform: uppercase !important;
  transition: all 0.2s !important;
}
div[data-testid="stTabs"] button:hover {
  color: var(--lemon) !important;
  background: var(--lemon-dim) !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--lemon) !important;
  background: var(--lemon-dim) !important;
  border-bottom: 2px solid var(--lemon) !important;
  text-shadow: 0 0 12px var(--lemon) !important;
}

/* ── INPUTS ── */
.stTextInput input, .stNumberInput input {
  background: var(--black3) !important;
  border: 1px solid rgba(168,230,0,0.2) !important;
  border-radius: 7px !important;
  color: var(--text) !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 0.9rem !important;
  transition: all 0.2s !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
  border-color: var(--lemon) !important;
  box-shadow: 0 0 0 2px rgba(232,255,0,0.1), 0 0 20px rgba(232,255,0,0.1) !important;
}
.stSelectbox > div > div {
  background: var(--black3) !important;
  border: 1px solid rgba(168,230,0,0.2) !important;
  border-radius: 7px !important;
  color: var(--text) !important;
}
[data-testid="stSelectbox"] svg { color: var(--lime) !important; }

/* ── BUTTONS ── */
.stButton > button {
  background: linear-gradient(135deg, #A8E600 0%, #E8FF00 100%) !important;
  color: var(--black) !important;
  border: none !important;
  border-radius: 7px !important;
  font-family: 'Space Mono', monospace !important;
  font-size: 0.72rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  padding: 0.6rem 1.8rem !important;
  box-shadow: 0 4px 20px rgba(168,230,0,0.25), 0 0 40px rgba(232,255,0,0.1) !important;
  transition: all 0.25s !important;
}
.stButton > button:hover {
  box-shadow: 0 6px 30px rgba(232,255,0,0.4), 0 0 60px rgba(168,230,0,0.2) !important;
  transform: translateY(-1px) !important;
}

/* ── FILE UPLOADER ── */
# [data-testid="stFileUploader"] {
#   background: var(--black3) !important;
#   border: 1px dashed rgba(168,230,0,0.25) !important;
#   border-radius: 10px !important;
#   transition: all 0.3s !important;
# }
# [data-testid="stFileUploader"]:hover {
#   border-color: var(--lemon) !important;
#   box-shadow: 0 0 25px rgba(232,255,0,0.1) !important;
# }
# [data-testid="stFileUploader"] * { color: var(--muted) !important; }
/* Browse files button */
[data-testid="stFileUploader"] button {
    background: #111111 !important;
    color: #a8e600 !important;
    border: 1px solid #333333 !important;
    border-radius: 8px !important;
}

/* Hover */
[data-testid="stFileUploader"] button:hover {
    background: #111111 !important;
    color: #a8e600 !important;
    border-color: var(--lemon) !important;
}
            
[data-testid="stFileUploader"] .stButton > button,
[data-testid="stFileUploader"] button[kind="secondary"] {
    background: #000 !important;
    color: #fff !important;
}

/* Focus */
[data-testid="stFileUploader"] button:focus {
    box-shadow: 0 0 0 2px rgba(232,255,0,0.3) !important;
}
/* ── PROGRESS ── */
.stProgress > div > div {
  background: rgba(232,255,0,0.08) !important;
  border-radius: 3px !important;
}
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--lime), var(--lemon)) !important;
  border-radius: 3px !important;
  box-shadow: 0 0 8px rgba(232,255,0,0.4) !important;
}

/* ── METRIC ── */
[data-testid="metric-container"] {
  background: var(--black3) !important;
  border: 1px solid rgba(168,230,0,0.18) !important;
  border-radius: 10px !important;
  padding: 1rem 1.2rem !important;
  position: relative;
  overflow: hidden;
}
[data-testid="metric-container"]::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--lime), var(--lemon), transparent);
}
[data-testid="metric-container"] label {
  color: var(--muted) !important;
  font-family: 'Space Mono', monospace !important;
  font-size: 0.6rem !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  color: var(--lemon) !important;
  font-family: 'Space Mono', monospace !important;
  font-size: 1.6rem !important;
  font-weight: 700 !important;
  text-shadow: 0 0 15px rgba(232,255,0,0.4) !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
  background: var(--black3) !important;
  border: 1px solid rgba(168,230,0,0.15) !important;
  border-radius: 8px !important;
}
[data-testid="stExpander"] summary { color: var(--text-soft) !important; }

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
  border: 1px solid rgba(168,230,0,0.15) !important;
  border-radius: 10px !important;
  overflow: hidden !important;
}
[data-testid="stDataFrame"] * { color: var(--text-soft) !important; }

/* ── FORM ── */
[data-testid="stForm"] {
  background: transparent !important;
  border: 1px solid rgba(168,230,0,0.18) !important;
  border-radius: 10px !important;
  padding: 1.2rem !important;
}

/* ── RADIO ── */
[data-testid="stRadio"] label { color: var(--text-soft) !important; font-size: 0.88rem !important; }

/* ── ALERTS ── */
.stSuccess {
  background: rgba(46,204,64,0.08) !important;
  border-color: rgba(46,204,64,0.4) !important;
  color: var(--green) !important;
  border-radius: 8px !important;
}
.stError {
  background: rgba(201,168,0,0.08) !important;
  border-color: rgba(201,168,0,0.4) !important;
  color: var(--gold) !important;
  border-radius: 8px !important;
}
.stInfo {
  background: var(--lemon-dim) !important;
  border-color: rgba(232,255,0,0.2) !important;
  color: var(--text-soft) !important;
  border-radius: 8px !important;
}
.stWarning {
  background: rgba(201,168,0,0.07) !important;
  border-color: rgba(201,168,0,0.3) !important;
  border-radius: 8px !important;
}

/* ── SPINNER ── */
.stSpinner > div { border-top-color: var(--lemon) !important; }

/* ── CAPTION ── */
.stCaption { color: var(--muted) !important; font-size: 0.74rem !important; font-family: 'Space Mono', monospace !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--black2); }
::-webkit-scrollbar-thumb { background: rgba(168,230,0,0.3); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--lemon); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def sec_label(text):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
      <div style="width:3px;height:14px;background:linear-gradient(180deg,var(--lime),var(--lemon));
                  border-radius:2px;flex-shrink:0;box-shadow:0 0 8px rgba(232,255,0,0.5);"></div>
      <span style="font-family:'Space Mono',monospace;font-size:0.62rem;font-weight:700;
                   letter-spacing:0.2em;color:var(--muted);text-transform:uppercase;">{text}</span>
    </div>""", unsafe_allow_html=True)


def kpi_box(icon, value, label):
    st.markdown(f"""
    <div style="background:var(--black3);border:1px solid rgba(168,230,0,0.18);
                border-radius:10px;padding:1.2rem 1.4rem;position:relative;overflow:hidden;
                box-shadow:0 4px 20px rgba(0,0,0,0.4);">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;
                  background:linear-gradient(90deg,var(--lime),var(--lemon),transparent);"></div>
      <div style="font-size:1.3rem;margin-bottom:6px;opacity:0.6;">{icon}</div>
      <div style="font-family:'Space Mono',monospace;font-size:1.8rem;font-weight:700;
                  color:var(--lemon);text-shadow:0 0 12px rgba(232,255,0,0.35);
                  line-height:1;margin-bottom:5px;">{value}</div>
      <div style="font-family:'Space Mono',monospace;font-size:0.58rem;letter-spacing:0.16em;
                  color:var(--muted);text-transform:uppercase;">{label}</div>
    </div>""", unsafe_allow_html=True)


def result_display(label, confidence, probs):
    is_cat = label == "cataract"

    if is_cat:
        border  = "rgba(201,168,0,0.45)"
        bg      = "rgba(201,168,0,0.06)"
        top     = "linear-gradient(90deg,var(--gold-dim),var(--gold),transparent)"
        vcolor  = "var(--gold)"
        vshadow = "0 0 18px rgba(201,168,0,0.45)"
        icon    = "⬡"
        verdict = "CATARACT DETECTED"
        note    = "Consult an ophthalmologist. This tool is for screening only."
        b_grad  = "linear-gradient(90deg,var(--gold-dim),var(--gold))"
        b_glow  = "0 0 8px rgba(201,168,0,0.4)"
    else:
        border  = "rgba(168,230,0,0.35)"
        bg      = "rgba(168,230,0,0.05)"
        top     = "linear-gradient(90deg,var(--lime),var(--lemon),transparent)"
        vcolor  = "var(--lime)"
        vshadow = "0 0 18px rgba(168,230,0,0.4)"
        icon    = "◉"
        verdict = "NO CATARACT — CLEAR"
        note    = "Eye appears healthy. Continue routine annual checkups."
        b_grad  = "linear-gradient(90deg,var(--lime),var(--lemon))"
        b_glow  = "0 0 8px rgba(232,255,0,0.4)"

    pct = confidence * 100

    st.markdown(f"""
    <div style="background:{bg};border:1px solid {border};border-radius:12px;
                padding:1.5rem 1.6rem;margin:0.8rem 0;position:relative;overflow:hidden;">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;background:{top};"></div>
      <div style="display:flex;align-items:flex-start;gap:14px;">
        <span style="font-size:2.2rem;color:{vcolor};text-shadow:{vshadow};
                     flex-shrink:0;line-height:1;margin-top:2px;">{icon}</span>
        <div>
          <div style="font-family:'Space Mono',monospace;font-size:1rem;font-weight:700;
                      letter-spacing:0.05em;color:{vcolor};text-shadow:{vshadow};">
            {verdict}
          </div>
          <div style="font-size:0.8rem;color:var(--muted);margin-top:4px;line-height:1.5;">
            {note}
          </div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
                margin:1rem 0 5px;">
      <span style="font-family:'Space Mono',monospace;font-size:0.6rem;letter-spacing:0.15em;
                   color:var(--muted);text-transform:uppercase;">Confidence</span>
      <span style="font-family:'Space Mono',monospace;font-size:0.9rem;font-weight:700;
                   color:var(--lemon);text-shadow:0 0 10px rgba(232,255,0,0.4);">{pct:.1f}%</span>
    </div>""", unsafe_allow_html=True)
    st.progress(confidence)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    for cls, prob in probs.items():
        w = prob * 100
        if cls == "cataract":
            cc = "var(--gold)";  cg = "linear-gradient(90deg,var(--gold-dim),var(--gold))";  csh = "0 0 8px rgba(201,168,0,0.4)"
        else:
            cc = "var(--lime)";  cg = "linear-gradient(90deg,var(--lime),var(--lemon))";     csh = "0 0 8px rgba(168,230,0,0.4)"

        st.markdown(f"""
        <div style="margin-bottom:10px;">
          <div style="display:flex;justify-content:space-between;margin-bottom:5px;
                      font-family:'Space Mono',monospace;font-size:0.6rem;letter-spacing:0.1em;">
            <span style="color:var(--muted);text-transform:uppercase;">{cls}</span>
            <span style="color:{cc};text-shadow:{csh};">{w:.2f}%</span>
          </div>
          <div style="height:4px;background:rgba(168,230,0,0.08);border-radius:2px;overflow:hidden;">
            <div style="height:100%;width:{w}%;background:{cg};border-radius:2px;
                        box-shadow:{csh};"></div>
          </div>
        </div>""", unsafe_allow_html=True)


def patient_banner(info, total=None):
    badge = f"""<span style="background:rgba(232,255,0,0.1);border:1px solid rgba(232,255,0,0.25);
                border-radius:4px;padding:2px 10px;font-family:'Space Mono',monospace;
                font-size:0.6rem;letter-spacing:0.1em;color:var(--lemon);
                margin-left:10px;">{total} SCANS</span>""" if total else ""
    contact = f"<span style='color:var(--muted);margin-left:10px;font-size:0.78rem;'>{info['contact']}</span>" if info.get("contact") else ""
    st.markdown(f"""
    <div style="border-left:3px solid var(--lime);padding:0.9rem 1.3rem;
                background:rgba(168,230,0,0.04);border-radius:0 10px 10px 0;
                margin-bottom:1rem;box-shadow:0 0 20px rgba(168,230,0,0.04);">
      <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:4px;">
        <span style="font-size:1rem;font-weight:600;color:var(--lemon);">{info['name']}</span>
        {badge}
      </div>
      <div style="font-size:0.78rem;color:var(--muted);">
        {info['age']} yrs · {info['gender']}{contact}
      </div>
    </div>""", unsafe_allow_html=True)


def scan_row(scan):
    is_cat = scan["label"] == "cataract"
    dot_c  = "var(--gold)" if is_cat else "var(--lime)"
    lbl_c  = "var(--gold)" if is_cat else "var(--lime)"
    glow   = "box-shadow:0 0 7px rgba(201,168,0,0.6);" if is_cat else "box-shadow:0 0 7px rgba(168,230,0,0.5);"
    ts     = scan["scanned_at"][:19].replace("T", " ")

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;padding:10px 14px;
                border:1px solid rgba(168,230,0,0.12);border-radius:8px;
                background:var(--black3);margin-bottom:6px;transition:all 0.2s;"
         onmouseover="this.style.borderColor='rgba(232,255,0,0.3)'"
         onmouseout="this.style.borderColor='rgba(168,230,0,0.12)'">
      <span style="width:8px;height:8px;border-radius:50%;background:{dot_c};
                   flex-shrink:0;display:inline-block;{glow}"></span>
      <div style="flex:1;">
        <div style="font-size:0.82rem;font-weight:600;color:{lbl_c};
                    letter-spacing:0.04em;text-transform:uppercase;">{scan['label']}</div>
        <div style="font-size:0.72rem;color:var(--muted);margin-top:1px;">{ts}</div>
      </div>
      <div style="font-family:'Space Mono',monospace;font-size:0.82rem;font-weight:700;
                  color:{lbl_c};">{scan['confidence']*100:.1f}%</div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PDF REPORT GENERATOR
# ─────────────────────────────────────────────

def generate_pdf_report(patient_info, label, confidence, probs):
    """Generate a styled PDF report using fpdf2 and return bytes."""
    is_cat = label == "cataract"

    # Colours (R, G, B)
    BG      = (8,   9,   0)
    DARK    = (30,  33,  0)
    LEMON   = (232, 255, 0)
    LIME    = (168, 230, 0)
    GOLD    = (201, 168, 0)
    WHITE   = (255, 255, 255)
    MUTED   = (107, 122, 0)
    accent  = GOLD if is_cat else LIME

    name    = str(patient_info.get("name",    "N/A"))
    age     = str(patient_info.get("age",     "N/A"))
    gender  = str(patient_info.get("gender",  "N/A"))
    contact = str(patient_info.get("contact", "-"))
    pid     = str(patient_info.get("id",      "-"))

    verdict_text = "CATARACT DETECTED" if is_cat else "NO CATARACT - CLEAR"
    conf_pct     = f"{confidence * 100:.1f}%"
    cat_pct      = f"{probs.get('cataract', 0) * 100:.2f}%"
    nor_pct      = f"{probs.get('normal',   0) * 100:.2f}%"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ── Background ────────────────────────────────────────────
    pdf.set_fill_color(*BG)
    pdf.rect(0, 0, 210, 297, "F")

    # ── Header bar ────────────────────────────────────────────
    pdf.set_fill_color(*DARK)
    pdf.rect(10, 10, 190, 18, "F")
    pdf.set_draw_color(*accent)
    pdf.set_line_width(0.8)
    pdf.line(10, 28, 200, 28)

    pdf.set_xy(14, 13)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*LEMON)
    pdf.cell(100, 8, "EYESHIELD - AI CATARACT REPORT", ln=0)

    pdf.set_xy(140, 14)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*MUTED)
    pdf.cell(60, 6, datetime.now().strftime("%d %b %Y, %H:%M"), ln=0, align="R")

    # ── Patient Information ───────────────────────────────────
    pdf.set_xy(10, 35)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*MUTED)
    pdf.cell(190, 5, "PATIENT INFORMATION", ln=True)

    pdf.set_fill_color(*DARK)
    pdf.rect(10, 41, 190, 30, "F")
    pdf.set_draw_color(42, 48, 0)
    pdf.set_line_width(0.3)
    pdf.rect(10, 41, 190, 30)

    rows = [
        ("Full Name", name,    "Patient ID", pid),
        ("Age",       age,     "Gender",     gender),
        ("Contact",   contact, "",           ""),
    ]
    y = 44
    for lbl1, val1, lbl2, val2 in rows:
        pdf.set_xy(14, y)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*MUTED)
        pdf.cell(25, 6, lbl1)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*WHITE)
        pdf.cell(65, 6, val1)
        if lbl2:
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(*MUTED)
            pdf.cell(25, 6, lbl2)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*WHITE)
            pdf.cell(65, 6, val2)
        y += 8

    # ── Verdict box ───────────────────────────────────────────
    pdf.set_fill_color(26, 30, 0)
    pdf.rect(10, 78, 190, 18, "F")
    pdf.set_draw_color(*accent)
    pdf.set_line_width(1.2)
    pdf.line(10, 78,  200, 78)
    pdf.line(10, 96,  200, 96)

    pdf.set_xy(10, 82)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*accent)
    pdf.cell(190, 8, verdict_text, align="C")

    # ── Probability table ─────────────────────────────────────
    pdf.set_xy(10, 103)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*MUTED)
    pdf.cell(190, 5, "SCAN RESULTS", ln=True)

    pdf.set_fill_color(*DARK)
    pdf.rect(10, 109, 190, 36, "F")
    pdf.set_draw_color(42, 48, 0)
    pdf.set_line_width(0.3)
    pdf.rect(10, 109, 190, 36)

    metrics = [
        ("Overall Confidence",   conf_pct),
        ("Cataract Probability", cat_pct),
        ("Normal Probability",   nor_pct),
    ]
    y = 112
    for metric, value in metrics:
        pdf.set_xy(14, y)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*WHITE)
        pdf.cell(130, 7, metric)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*accent)
        pdf.cell(56, 7, value, align="R")
        y += 10

    # ── Note ──────────────────────────────────────────────────
    pdf.set_xy(10, 152)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*MUTED)
    note = "Consult an ophthalmologist. This tool is for screening only." if is_cat else "Eye appears healthy. Continue routine annual checkups."
    pdf.cell(190, 6, note, align="C")

    # ── Footer ────────────────────────────────────────────────
    pdf.set_draw_color(42, 48, 0)
    pdf.set_line_width(0.3)
    pdf.line(10, 275, 200, 275)
    pdf.set_xy(10, 277)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(*MUTED)
    pdf.cell(190, 5,
             f"EyeShield v2.0  |  AI Cataract Detection  |  For research & educational use only  |  Generated {datetime.now().strftime('%d %b %Y at %H:%M')}",
             align="C")

    return bytes(pdf.output())

# ─────────────────────────────────────────────
# AUTH — Login / Sign Up page
# ─────────────────────────────────────────────

def show_auth_page():
    """Render the login/signup screen in the EyeShield theme."""
    st.markdown("""
    <div style="max-width:420px;margin:6vh auto 0;padding:0 1rem;">
      <div style="text-align:center;margin-bottom:2.4rem;">
        <div style="font-size:2.8rem;margin-bottom:0.6rem;">👁</div>
        <div style="font-family:'Space Mono',monospace;font-size:1.3rem;font-weight:700;
                    letter-spacing:0.06em;color:var(--lemon);
                    text-shadow:0 0 24px rgba(232,255,0,0.35);">EYESHIELD</div>
        <div style="font-family:'Space Mono',monospace;font-size:0.52rem;letter-spacing:0.22em;
                    color:rgba(168,230,0,0.35);text-transform:uppercase;margin-top:4px;">
          AI Cataract Detection
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Center the form
    _, col, _ = st.columns([1, 2, 1])
    with col:
        auth_tab = st.radio("", ["Sign In", "Sign Up", "Forgot Password"],
                            horizontal=True, label_visibility="collapsed")
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        if auth_tab == "Sign In":
            with st.form("login_form"):
                email    = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Sign In →", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please enter email and password.")
                else:
                    try:
                        res = _supabase.auth.sign_in_with_password(
                            {"email": email, "password": password}
                        )
                        st.session_state["user"] = {
                            "id":    res.user.id,
                            "email": res.user.email,
                        }
                        st.session_state["access_token"] = res.session.access_token
                        st.rerun()
                    except Exception as e:
                        st.error(f"Sign in failed: {e}")

        elif auth_tab == "Sign Up":
            with st.form("signup_form"):
                email    = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="Min 6 characters")
                confirm  = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Create Account →", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("Please fill in all fields.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    try:
                        _supabase.auth.sign_up({"email": email, "password": password})
                        st.success("Account created! Check your email to confirm, then sign in.")
                    except Exception as e:
                        st.error(f"Sign up failed: {e}")

        else:  # Forgot Password
            st.markdown("""
            <div style="font-size:0.8rem;color:var(--muted);margin-bottom:12px;line-height:1.6;">
              Enter your email and we'll send you a link to reset your password.
            </div>""", unsafe_allow_html=True)

            with st.form("forgot_form"):
                reset_email = st.text_input("Email", placeholder="you@example.com")
                submitted   = st.form_submit_button("Send Reset Link →", use_container_width=True)

            if submitted:
                if not reset_email:
                    st.error("Please enter your email address.")
                else:
                    try:
                        _supabase.auth.reset_password_email(reset_email)
                        st.success("Reset link sent! Check your inbox and follow the link to set a new password.")
                    except Exception as e:
                        st.error(f"Could not send reset email: {e}")

        st.markdown("""
        <div style="margin-top:2rem;text-align:center;font-family:'Space Mono',monospace;
                    font-size:0.52rem;letter-spacing:0.1em;color:rgba(232,255,0,0.12);
                    text-transform:uppercase;">
          EyeShield · AI Cataract Screening · For research use only
        </div>""", unsafe_allow_html=True)


# ── Auth gate — show login if not authenticated ───────────────────────────────
if "user" not in st.session_state:
    show_auth_page()
    st.stop()

# ─────────────────────────────────────────────
# User is authenticated — render the full dashboard
# ─────────────────────────────────────────────


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0.4rem 0 1.2rem;">
      <div style="font-family:'Space Mono',monospace;font-size:1.15rem;font-weight:700;
                  letter-spacing:0.06em;color:var(--lemon);
                  text-shadow:0 0 20px rgba(232,255,0,0.3);margin-bottom:4px;">
        👁 EYESHIELD
      </div>
      <div style="font-family:'Space Mono',monospace;font-size:0.55rem;letter-spacing:0.2em;
                  color:rgba(168,230,0,0.35);text-transform:uppercase;">
        AI Cataract Detection
      </div>
    </div>
    <div style="height:1px;background:linear-gradient(90deg,rgba(168,230,0,0.4),transparent);
                margin-bottom:1.2rem;"></div>
    """, unsafe_allow_html=True)

    for k, v, vc in [
        ("Model",    "MobileNetV2", "var(--lemon)"),
        ("Accuracy", "~98%",        "var(--lime)"),
        ("Backend",  "FastAPI",     "var(--muted)"),
        ("Storage",  "Supabase",    "var(--muted)"),
    ]:
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:7px 0;border-bottom:1px solid rgba(168,230,0,0.07);">
          <span style="font-size:0.78rem;color:var(--muted);">{k}</span>
          <span style="font-family:'Space Mono',monospace;font-size:0.7rem;
                       color:{vc};">{v}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("""<div style="height:1px;background:linear-gradient(90deg,rgba(168,230,0,0.2),transparent);
                margin:1.2rem 0;"></div>""", unsafe_allow_html=True)
    st.markdown("[API Docs →](https://eyeshield-api.onrender.com/docs)", unsafe_allow_html=True)
    st.markdown("""<div style="height:1px;background:linear-gradient(90deg,rgba(168,230,0,0.1),transparent);
                margin:1rem 0;"></div>
    <div style="font-family:'Space Mono',monospace;font-size:0.5rem;letter-spacing:0.1em;
                color:rgba(168,230,0,0.15);text-align:center;text-transform:uppercase;">
      PyTorch · FastAPI · Streamlit
    </div>""", unsafe_allow_html=True)

    # ── Admin Access — Hidden in deployment ──────────────────────────────────
    st.markdown("""
    <div style="height:1px;background:linear-gradient(90deg,rgba(168,230,0,0.08),transparent);
                margin:1.4rem 0 0.7rem;"></div>
    <div style="font-family:'Space Mono',monospace;font-size:0.46rem;letter-spacing:0.18em;
                color:rgba(232,255,0,0.1);text-transform:uppercase;text-align:center;
                margin-bottom:0.45rem;">Only Admins can Access</div>
    """, unsafe_allow_html=True)
    admin_password = st.sidebar.text_input(
        "Admin Access",
        type="password",
        label_visibility="collapsed",
        placeholder="••••••••",
    )
    ADMIN_ACCESS = admin_password == "eyeshield123"
    # ─────────────────────────────────────────────────────────────────────────

    # ── Signed-in user + Sign Out ─────────────────────────────────────────────
    st.markdown("""
    <div style="height:1px;background:linear-gradient(90deg,rgba(168,230,0,0.08),transparent);
                margin:1.2rem 0 0.8rem;"></div>
    """, unsafe_allow_html=True)

    user_email = st.session_state.get("user", {}).get("email", "")
    st.markdown(f"""
    <div style="padding:8px 10px;background:rgba(168,230,0,0.04);
                border:1px solid rgba(168,230,0,0.1);border-radius:7px;
                margin-bottom:8px;">
      <div style="font-family:'Space Mono',monospace;font-size:0.48rem;
                  letter-spacing:0.14em;color:rgba(168,230,0,0.3);
                  text-transform:uppercase;margin-bottom:3px;">Signed in as</div>
      <div style="font-size:0.75rem;color:var(--text-soft);
                  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
        {user_email}
      </div>
    </div>""", unsafe_allow_html=True)

    if st.button("Sign Out", use_container_width=True, key="signout_btn"):
        try:
            _supabase.auth.sign_out()
        except Exception:
            pass
        st.session_state.clear()
        st.rerun()


# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────
try:
    health     = requests.get(f"{BASE_URL}/health", timeout=2)
    backend_ok = health.json().get("model_loaded", False)
except Exception:
    backend_ok = False

if not backend_ok:
    st.markdown("""
    <div style="border:1px solid rgba(201,168,0,0.4);background:rgba(201,168,0,0.05);
                border-radius:12px;padding:2rem 2.2rem;margin-top:2rem;">
      <div style="font-family:'Space Mono',monospace;font-size:0.9rem;font-weight:700;
                  color:var(--gold);margin-bottom:8px;">⬡ Backend Offline</div>
      <div style="font-size:0.86rem;color:var(--muted);margin-bottom:12px;">
        Start the FastAPI server to continue.
      </div>
      <code style="background:var(--black3);padding:8px 16px;border-radius:6px;
                   font-size:0.8rem;color:var(--lemon);border:1px solid rgba(168,230,0,0.15);">
        uvicorn main:app --reload --port 8000
      </code>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.8rem;">
  <div style="font-family:'Space Mono',monospace;font-size:0.58rem;letter-spacing:0.22em;
              color:rgba(168,230,0,0.4);text-transform:uppercase;margin-bottom:8px;">
    EyeShield Diagnostics
  </div>
  <div style="display:flex;align-items:flex-end;justify-content:space-between;
              flex-wrap:wrap;gap:1rem;">
    <div style="font-family:'Space Grotesk',sans-serif;font-size:2.5rem;font-weight:700;
                letter-spacing:-0.01em;line-height:1;
                background:linear-gradient(135deg, #A8E600 0%, #E8FF00 40%, #C9A800 100%);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;">
      AI Cataract Detection
    </div>
    <div style="display:flex;align-items:center;gap:8px;padding:8px 16px;
                background:rgba(46,204,64,0.06);border:1px solid rgba(46,204,64,0.2);
                border-radius:6px;">
      <span style="width:6px;height:6px;background:var(--green);border-radius:50%;
                   display:inline-block;box-shadow:0 0 8px var(--green);
                   animation:pulse 2s ease-in-out infinite;"></span>
      <span style="font-family:'Space Mono',monospace;font-size:0.6rem;letter-spacing:0.1em;
                   color:rgba(46,204,64,0.65);text-transform:uppercase;">
        Model Online
      </span>
    </div>
  </div>
  <div style="height:1px;margin-top:1.2rem;
              background:linear-gradient(90deg,rgba(168,230,0,0.35),rgba(232,255,0,0.1),transparent);
              "></div>
</div>
<style>
@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 8px var(--green)}50%{opacity:0.35;box-shadow:0 0 3px var(--green)}}
</style>
""", unsafe_allow_html=True)

# ── KPIs ──
try:
    _p  = requests.get(f"{BASE_URL}/predictions", timeout=2).json()
    _pt = requests.get(f"{BASE_URL}/patients",    timeout=2).json()
    _t  = len(_p); _n = len(_pt)
    _c  = sum(1 for x in _p if x.get("label") == "cataract")
    _r  = f"{_c/_t*100:.0f}%" if _t else "—"
except Exception:
    _t = _n = _c = 0; _r = "—"

k1, k2, k3, k4 = st.columns(4)
with k1: kpi_box("👥", _n,  "Total Patients")
with k2: kpi_box("🔬", _t,  "Screenings")
with k3: kpi_box("⬡",  _c,  "Cataract Cases")
with k4: kpi_box("📊", _r,  "Detection Rate")

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TABS — visibility controlled by Admin Access
# ─────────────────────────────────────────────
if ADMIN_ACCESS:
    tab1, tab2, tab3 = st.tabs(["New Scan", "Patient History", "All Records"])
else:
    tab1, = st.tabs(["New Scan"])
    tab2 = tab3 = None  # Not rendered for normal users


# ══════════════════════════════════════════════
# TAB 1 — New Scan
# ══════════════════════════════════════════════
with tab1:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1, 1], gap="large")

    with col_l:
        sec_label("Patient")
        mode = st.radio("", ["Register new patient", "Select existing patient"], horizontal=True)
        patient_id = None

        if mode == "Register new patient":
            with st.form("register_form"):
                name    = st.text_input("Full Name *", placeholder="e.g. Anjali Mehta")
                a, b    = st.columns(2)
                age     = a.number_input("Age *", min_value=1, max_value=120, value=30)
                gender  = b.selectbox("Gender *", ["Male", "Female", "Other"])
                contact = st.text_input("Contact Number", placeholder="+91 XXXXX XXXXX")
                sub     = st.form_submit_button("Register Patient →", use_container_width=True)

            if sub:
                if not name.strip():
                    st.error("Name is required.")
                else:
                    resp = requests.post(
                        f"{BASE_URL}/patients",
                        json={"name": name, "age": int(age), "gender": gender, "contact": contact},
                    )
                    if resp.status_code == 200:
                        patient_id = resp.json()["patient_id"]
                        st.session_state["selected_patient_id"] = patient_id
                        st.success(f"✓ Registered — ID {patient_id}")
                    else:
                        st.error("Registration failed.")
        else:
            sq = st.text_input("Search by name or contact", placeholder="Type to search…")
            if sq:
                results = requests.get(f"{BASE_URL}/patients/search", params={"query": sq}).json()
                if results:
                    opts = {f"{p['name']}  ·  ID {p['id']}  ·  Age {p['age']}": p["id"] for p in results}
                    chosen = st.selectbox("Select patient", list(opts.keys()))
                    st.session_state["selected_patient_id"] = opts[chosen]
                    st.info(f"Active patient ID: {opts[chosen]}")
                else:
                    st.warning("No patients found.")
            elif "selected_patient_id" in st.session_state:
                st.info(f"Active patient ID: {st.session_state['selected_patient_id']}")

    with col_r:
        sec_label("Upload & Analyse")
        uploaded_file = st.file_uploader(
            "Choose a retinal image (JPG / PNG)",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
        )

        if uploaded_file:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, use_container_width=True)
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            if st.button("Run Prediction →", use_container_width=True):
                pid = st.session_state.get("selected_patient_id")
                if not pid:
                    st.error("Please register or select a patient first.")
                else:
                    with st.spinner("Analysing image…"):
                        uploaded_file.seek(0)
                        response = requests.post(
                            f"{BASE_URL}/patients/{pid}/predict",
                            files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)},
                            timeout=30,
                        )
                    if response.status_code == 200:
                        data       = response.json()
                        label      = data["label"]
                        confidence = data["confidence"]
                        probs      = data["probabilities"]
                        result_display(label, confidence, probs)
                        st.caption(f"Prediction ID: {data['prediction_id']}")

                        # ── Download Report ──────────────────────────
                        # Fetch patient info for the report
                        try:
                            pat_resp = requests.get(
                                f"{BASE_URL}/patients/{pid}/history", timeout=5
                            ).json()
                            pat_info = pat_resp.get("patient", {
                                "name": "Unknown", "age": "—",
                                "gender": "—", "contact": "—", "id": pid,
                            })
                        except Exception:
                            pat_info = {
                                "name": "Unknown", "age": "—",
                                "gender": "—", "contact": "—", "id": pid,
                            }

                        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                        pdf_bytes = generate_pdf_report(pat_info, label, confidence, probs)
                        fname = (
                            f"EyeShield_{pat_info.get('name','patient').replace(' ','_')}"
                            f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                        )
                        st.download_button(
                            label="⬇  Download Full Report (PDF)",
                            data=pdf_bytes,
                            file_name=fname,
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    else:
                        st.error(f"API error {response.status_code}: {response.json().get('detail')}")
        else:
            st.markdown("""
            <div style="border:1px dashed rgba(168,230,0,0.2);border-radius:10px;
                        padding:4rem 1.5rem;text-align:center;background:var(--black3);">
              <div style="font-size:2.5rem;opacity:0.15;margin-bottom:10px;">👁</div>
              <div style="font-family:'Space Mono',monospace;font-size:0.65rem;
                          letter-spacing:0.15em;color:rgba(232,255,0,0.18);
                          text-transform:uppercase;">Drop retinal image here</div>
              <div style="font-size:0.72rem;color:rgba(232,255,0,0.1);margin-top:5px;">
                JPG · JPEG · PNG
              </div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 2 — Patient History (Admin Access only)
# ══════════════════════════════════════════════
if ADMIN_ACCESS and tab2 is not None:
    with tab2:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        search_q = st.text_input("", placeholder="Search patient by name or contact…",
                                  key="history_search", label_visibility="collapsed")

        if search_q:
            patients = requests.get(f"{BASE_URL}/patients/search", params={"query": search_q}).json()
        else:
            patients = requests.get(f"{BASE_URL}/patients").json()

        if not patients:
            st.info("No patients found.")
        else:
            options = {
                f"{p['name']}  ·  ID {p['id']}  ·  {p['gender']}  ·  Age {p['age']}": p["id"]
                for p in patients
            }
            chosen_label = st.selectbox("", list(options.keys()), key="history_select",
                                         label_visibility="collapsed")
            chosen_id    = options[chosen_label]

            history_resp = requests.get(f"{BASE_URL}/patients/{chosen_id}/history").json()
            patient_info = history_resp["patient"]
            scans        = history_resp["scans"]
            total        = history_resp["total_scans"]

            patient_banner(patient_info, total)

            col_tl, col_det = st.columns([1, 1], gap="large")

            with col_tl:
                sec_label("Scan Timeline")
                if not scans:
                    st.info("No scans recorded yet.")
                else:
                    # ── Date filter ──────────────────────────────────
                    all_dates = sorted(set(s["scanned_at"][:10] for s in scans), reverse=True)
                    date_options = ["All dates"] + all_dates
                    selected_date = st.selectbox(
                        "Filter by date",
                        date_options,
                        key="timeline_date_filter",
                        label_visibility="collapsed",
                    )
                    filtered_scans = scans if selected_date == "All dates" else [
                        s for s in scans if s["scanned_at"][:10] == selected_date
                    ]
                    if not filtered_scans:
                        st.info("No scans on this date.")
                    else:
                        for scan in filtered_scans:
                            scan_row(scan)

            with col_det:
                if scans:
                    sec_label("Latest Result")
                    latest = scans[0]
                    result_display(latest["label"], latest["confidence"], {
                        "cataract": latest["cataract_prob"],
                        "normal":   latest["normal_prob"],
                    })
                else:
                    st.markdown("""
                    <div style="text-align:center;padding:3rem;border:1px solid rgba(168,230,0,0.08);
                                border-radius:10px;">
                      <div style="font-size:2rem;opacity:0.1;margin-bottom:8px;">👁</div>
                      <div style="font-family:'Space Mono',monospace;font-size:0.62rem;
                                  letter-spacing:0.15em;color:rgba(232,255,0,0.1);
                                  text-transform:uppercase;">No scan data</div>
                    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 3 — All Records (Admin Access only)
# ══════════════════════════════════════════════
if ADMIN_ACCESS and tab3 is not None:
    with tab3:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        hd, bt = st.columns([6, 1])
        with hd: sec_label("Full Patient Record Database")
        with bt:
            if st.button("↺ Refresh", key="refresh_all"):
                st.rerun()

        all_preds = requests.get(f"{BASE_URL}/predictions").json()

        if not all_preds:
            st.info("No predictions recorded yet.")
        else:
            import pandas as pd

            df = pd.DataFrame(all_preds)
            df = df.rename(columns={
                "id":            "Scan ID",
                "patient_name":  "Patient",
                "age":           "Age",
                "gender":        "Gender",
                "label":         "Result",
                "confidence":    "Confidence",
                "cataract_prob": "Cataract %",
                "normal_prob":   "Normal %",
                "scanned_at":    "Scanned At",
            })
            df["Confidence"] = (df["Confidence"] * 100).round(1).astype(str) + "%"
            df["Cataract %"] = (df["Cataract %"] * 100).round(2).astype(str) + "%"
            df["Normal %"]   = (df["Normal %"]   * 100).round(2).astype(str) + "%"
            df["Scanned At"] = df["Scanned At"].str[:19].str.replace("T", " ")
            df["Result"]     = df["Result"].str.capitalize()

            display_cols = ["Scan ID", "Patient", "Age", "Gender", "Result",
                            "Confidence", "Cataract %", "Normal %", "Scanned At"]
            st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
            st.caption(f"Total scans: {len(df)}")


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding-top:1rem;
            border-top:1px solid rgba(168,230,0,0.08);
            display:flex;justify-content:space-between;align-items:center;
            flex-wrap:wrap;gap:8px;">
  <div style="font-size:0.7rem;color:rgba(232,255,0,0.15);">
    ⚠ For research and educational use only — not a substitute for medical advice
  </div>
  <div style="font-family:'Space Mono',monospace;font-size:0.62rem;
              color:rgba(168,230,0,0.15);text-transform:uppercase;letter-spacing:0.08em;">
    EyeShield · v2.0
  </div>
</div>
""", unsafe_allow_html=True)