---
title: Parakh Portal
emoji: 🏛️
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 🇮🇳 PARAKH™ — Packaged Article Review and Assessment Kompliance Hub
### Smart India Hackathon 2026 — Problem Statement ID: SIH-26034
**Ministry of Consumer Affairs, Food & Public Distribution**  
*Department of Consumer Affairs — Directorate of Legal Metrology, Government of India*  
**Developed by Team Hack Horizon**

---

## 📌 Executive Overview
**PARAKH™** is an automated optical intelligence and regulatory compliance surveillance platform engineered to enforce the **Legal Metrology (Packaged Commodities) Rules, 2011** and recent gazette notifications across retail consumer packaged goods in India.

By replacing slow, manual physical spot-checks with **adaptive 360° deep-learning OCR and deterministic statutory rule matching**, PARAKH™ empowers field enforcement officers and consumer affairs authorities to audit packaging labels in real-time, detect non-compliances (such as missing tax clauses, illegal non-standard units, hidden price gouging, and absent origins), and issue court-admissible statutory notices.

---

## ✨ Core Innovations & Capabilities

1. **🔄 360° Adaptive Neural OCR Engine**:
   - Deep-learning CRAFT text detection and EasyOCR recognition.
   - Handles multi-angle orientations ($0^\circ, 90^\circ, 270^\circ$) with automatic smartphone EXIF orientation correction (`ImageOps.exif_transpose`).
   - Resolves curved foil pouches, cylindrical bottles, and skewed labels.

2. **⚖️ Comprehensive Rule 6 Statutory Audit**:
   - Validates all 9 mandatory packaging declarations:
     - **Rule 6(1)(a)**: Name & complete postal address of Manufacturer/Packer/Importer.
     - **Rule 6(1)(b)**: Generic/Common name of the commodity on PDP.
     - **Rule 6(1)(c)**: Net quantity in standard SI metric units (flags illegal expressions like `gms`, `ltr`, `kilo`).
     - **Rule 6(1)(d)**: Month & Year of manufacture/packing/import.
     - **Rule 6(1)(e)**: Maximum Retail Price (MRP) with mandatory `"inclusive of all taxes"` clause.
     - **Rule 6(1)(aa)**: Country of Origin declaration (`Country of Origin: India`).
     - **Rule 6(1)(f)**: Batch/Lot identification number.
     - **Rule 6(1)(g)**: Consumer Care contact (toll-free helpline, active email address).
     - **Rule 6(11)**: Unit Sale Price (USP) per gram/ml and per kg/litre.

3. **🏷️ Interactive Unit Sale Price (USP) Mathematical Calculator**:
   - Real-time statutory computation under Rule 6(11) for weight ($g, kg$), volume ($ml, l$), and piece counts ($N$).

4. **🏛️ Official Court-Admissible Dossier & Section 36 Notice Generator**:
   - 2-page printable enforcement dossier featuring the **State Emblem of India (Ashoka Stambh)** with the motto *"सत्यमेव जयते"*.
   - Automated generation of 7-day statutory show-cause demand notices under Section 36 of the Legal Metrology Act, 2009.

5. **📈 Real-Time Central Enforcement Analytics**:
   - Dynamic 7-day, 30-day, and QTD inspection trajectories (Chart.js Line graph).
   - Contravention distribution doughnut chart (MRP & Taxes, Country of Origin, Standard Units, Consumer Care).
   - Sectoral compliance index benchmarks (FSSAI Foods, CDSCO Cosmetics, BEE/BIS Electronics).
   - 1-click real CSV enforcement log export.

---

## 🛠️ Technology Stack
* **Backend Framework**: Python 3.11+, FastAPI, Uvicorn
* **Computer Vision & OCR**: PyTorch, EasyOCR, OpenCV (`opencv-python-headless`), Pillow (`PIL`)
* **Frontend Architecture**: HTML5, Tailwind CSS, Chart.js, Vanilla ES6+
* **Deployment**: Docker, Uvicorn ASGI Server, Render / Cloud VM

---

## 🚀 Quick Start & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Nikhilr-404/SIH-Hack-Horizon.git
cd SIH-Hack-Horizon
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Local Server
```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Open in Browser
Visit **`http://127.0.0.1:8000/`** to access the live portal.

---

## 🐳 Docker Deployment
```dockerfile
docker build -t parakh-portal .
docker run -p 8000:8000 parakh-portal
```

---

## 📜 Regulatory Standards & Acts Covered
* **Legal Metrology Act, 2009** (Sections 36, 38, 49)
* **Legal Metrology (Packaged Commodities) Rules, 2011** (Rule 6, Rule 9, Rule 12, First & Second Schedules)
* **Gazette Notification GSR 779(E)** (Unit Sale Price & Digital PDP Amendments)
* **Consumer Protection Act, 2019** (Unfair Trade Practices & E-Commerce Rules)
* **FSSAI Food Safety & Standards (Packaging and Labelling) Regulations**
* **BEE / BIS Compulsory Registration Scheme (IS 13252)**

---

## 👥 Team Hack Horizon (SIH 2026)
* Problem Statement: **SIH-26034**
* Organization: **Ministry of Consumer Affairs, Food & Public Distribution**
