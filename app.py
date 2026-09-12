from fastapi import FastAPI, File, UploadFile, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import easyocr
import re
import io
import os
import gc
import datetime
import torch
from PIL import Image, ImageOps
import numpy as np

# Restrict PyTorch thread pool to prevent container memory exhaustion
torch.set_num_threads(1)
if hasattr(torch, "set_num_interop_threads"):
    try:
        torch.set_num_interop_threads(1)
    except Exception:
        pass

app = FastAPI(title="MetrologyGuard AI - SIH 2026 PS-26034")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

reader = None

def get_reader():
    global reader
    if reader is None:
        print("🚀 Initializing EasyOCR Engine (low-memory container mode)...")
        reader = easyocr.Reader(['en'], gpu=False, quantize=False)
        print("✅ OCR & Legal Metrology Engine Ready!")
    return reader

@app.on_event("startup")
def startup_warmup():
    print("⚡ Pre-warming OCR Engine at startup...")
    try:
        get_reader()
    except Exception as e:
        print(f"Startup warmup note: {e}")

# Real-time Live Analytics Store aligned with PARAKH™ Design Board
analytics_data = {
    "total_scans": 128,
    "compliant": 86,
    "violations_flagged": 28,
    "need_review": 14,
    "notices_issued": 28,
    "violation_counts": {
        "mrp_tax": 11,
        "country_origin": 8,
        "standard_units": 6,
        "consumer_care": 3
    },
    "trend_data": {
        "labels": ["06 Sep", "07 Sep", "08 Sep", "09 Sep", "10 Sep", "11 Sep", "12 Sep"],
        "total": [14, 22, 18, 30, 26, 35, 42],
        "compliant": [10, 16, 12, 21, 18, 25, 29],
        "violations": [4, 6, 6, 9, 8, 10, 13]
    },
    "category_compliance": [
        {"name": "Packaged Food & Beverages (FSSAI)", "scans": 54, "compliant": 45, "rate": 83},
        {"name": "Cosmetics & Personal Care", "scans": 32, "compliant": 22, "rate": 69},
        {"name": "Electronics & Electrical Appliances (BEE/BIS)", "scans": 24, "compliant": 18, "rate": 75},
        {"name": "Household Goods & Commodities", "scans": 18, "compliant": 11, "rate": 61}
    ],
    "recent_history": [
        {"product": "Basmati Rice 1kg", "date": "12 Sep 2026, 10:30 AM", "status": "Compliant", "score": 91, "issues": 0},
        {"product": "Choco Cookies 200g", "date": "12 Sep 2026, 09:15 AM", "status": "Needs Review", "score": 68, "issues": 2},
        {"product": "Herbal Shampoo 500ml", "date": "11 Sep 2026, 04:45 PM", "status": "Non-Compliant", "score": 48, "issues": 4},
        {"product": "Salt Pack 1kg", "date": "11 Sep 2026, 11:20 AM", "status": "Compliant", "score": 94, "issues": 0},
        {"product": "Instant Noodles 70g", "date": "10 Sep 2026, 06:10 PM", "status": "Needs Review", "score": 72, "issues": 1}
    ]
}

def map_box_to_original(pts, angle, orig_w, orig_h, scale_factor=1.0):
    """Maps rotated and scaled bounding box coordinates back to the original image dimensions."""
    mapped = []
    for pt in pts:
        x, y = pt[0], pt[1]
        if angle == 90:
            # 90 degrees counter-clockwise
            ox = orig_w - 1 - y
            oy = x
        elif angle == 270:
            # 270 degrees counter-clockwise (90 deg clockwise)
            ox = y
            oy = orig_h - 1 - x
        elif angle == 180:
            ox = orig_w - 1 - x
            oy = orig_h - 1 - y
        else:
            ox, oy = x, y
            
        if scale_factor != 1.0 and scale_factor > 0:
            ox = ox / scale_factor
            oy = oy / scale_factor
            
        mapped.append([int(ox), int(oy)])
    return mapped

@app.get("/", response_class=HTMLResponse)
def serve_homepage():
    index_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>index.html not found</h1>")

@app.get("/pouch.png")
def serve_pouch_image():
    pouch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pouch.png")
    if os.path.exists(pouch_path):
        with open(pouch_path, "rb") as f:
            return Response(content=f.read(), media_type="image/png")
    return Response(status_code=404)

@app.get("/logo.png")
def serve_logo_image():
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return Response(content=f.read(), media_type="image/png")
    return Response(status_code=404)

@app.get("/favicon.png")
def serve_favicon_image():
    fav_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "favicon.png")
    if os.path.exists(fav_path):
        with open(fav_path, "rb") as f:
            return Response(content=f.read(), media_type="image/png")
    return Response(status_code=404)

@app.get("/emblem.png")
def serve_emblem_image():
    emblem_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emblem.png")
    if os.path.exists(emblem_path):
        with open(emblem_path, "rb") as f:
            return Response(content=f.read(), media_type="image/png")
    return Response(status_code=404)

@app.get("/analytics")
def get_analytics():
    return analytics_data

@app.post("/scan")
async def scan_product(file: UploadFile = File(...)):
    contents = await file.read()
    
    # 1. Open image and normalize mobile camera EXIF orientation
    raw_image = Image.open(io.BytesIO(contents))
    del contents  # Release raw upload bytes immediately
    image = ImageOps.exif_transpose(raw_image).convert('RGB')
    raw_image.close()
    del raw_image
    orig_w, orig_h = image.size
    
    # 2. Smart downscaling for fast OCR & strictly controlled memory footprint
    max_dim = max(orig_w, orig_h)
    if max_dim > 1024:
        scale_factor = 1024.0 / max_dim
        proc_w = int(orig_w * scale_factor)
        proc_h = int(orig_h * scale_factor)
        ocr_image = image.resize((proc_w, proc_h), Image.Resampling.BILINEAR)
    else:
        scale_factor = 1.0
        proc_w, proc_h = orig_w, orig_h
        ocr_image = image
    
    del image  # Release unscaled image buffer
    
    # 3. Optical Recognition with Adaptive Multi-Angle Fallback
    ocr_reader = get_reader()
    results = ocr_reader.readtext(np.array(ocr_image))
    chosen_angle = 0

    # If the product was held sideways (few text lines found), test 90° and 270°
    if len(results) < 3:
        for angle in [90, 270]:
            rotated_img = ocr_image.rotate(angle, expand=True)
            rotated_results = ocr_reader.readtext(np.array(rotated_img))
            if len(rotated_results) > len(results):
                results = rotated_results
                chosen_angle = angle
                if len(results) >= 4:
                    break
    
    raw_lines = []
    boxes = []
    
    for bbox, text, conf in results:
        # Ignore tiny 1-character noise
        if len(text.strip()) > 1 and conf > 0.15:
            raw_lines.append(text)
            clean_box = map_box_to_original(bbox, chosen_angle, proc_w, proc_h, scale_factor)
            boxes.append({"text": text, "box": clean_box, "confidence": float(conf)})
        
    full_text = " ".join(raw_lines).lower()
    
    # Remove weird punctuation for robust keyword matching
    clean_text = re.sub(r'[^a-z0-9\s₹\./@]', ' ', full_text)
    
    checks = []

    # -------------------------------------------------------------
    # ROBUST LMPC RULE 6 INTELLIGENCE (Fuzzy & Context Aware)
    # -------------------------------------------------------------

    # Rule 1: MRP & Tax Declaration
    has_price_indicator = any(k in clean_text for k in ['mrp', 'rs', 'inr', 'price', '₹', 'max retail', 'maximum retail']) or bool(re.search(r'₹?\s*\d+(\.\d{2})?', clean_text))
    has_tax_indicator = any(k in clean_text for k in ['tax', 'taxes', 'incl', 'inclusive', 'all taxes', 'inc of'])
    
    if has_price_indicator and has_tax_indicator:
        checks.append({"rule": "Rule 6(1)(e): MRP with Tax Clause", "status": "PASS", "detail": "MRP declared with 'inclusive of all taxes'"})
    elif has_price_indicator and not has_tax_indicator:
        checks.append({"rule": "Rule 6(1)(e): MRP with Tax Clause", "status": "VIOLATION", "detail": "Price detected, but missing mandatory 'incl. of all taxes'"})
        analytics_data["violation_counts"]["mrp_tax"] += 1
    else:
        checks.append({"rule": "Rule 6(1)(e): MRP with Tax Clause", "status": "WARNING", "detail": "MRP or price tag not clearly visible on this label panel"})

    # Rule 2: Country of Origin
    indian_states = ['india', 'delhi', 'mumbai', 'gujarat', 'maharashtra', 'haryana', 'karnataka', 'tamil nadu', 'punjab', 'rajasthan', 'uttar pradesh', 'bengaluru', 'kolkata']
    has_origin_tag = any(k in clean_text for k in ['country of origin', 'made in', 'product of', 'origin', 'mfd in', 'packed in', 'mfg in'])
    has_indian_geo = any(state in clean_text for state in indian_states)
    
    if has_origin_tag or has_indian_geo:
        checks.append({"rule": "Rule 6(1)(aa): Country of Origin", "status": "PASS", "detail": "Country of origin / manufacturing location declared"})
    else:
        checks.append({"rule": "Rule 6(1)(aa): Country of Origin", "status": "VIOLATION", "detail": "Country of origin tag not detected on packaging"})
        analytics_data["violation_counts"]["country_origin"] += 1

    # Rule 3: Net Quantity in Standard Metric Units
    has_illegal_units = bool(re.search(r'\b\d+\s*(gms|kgs|ltr|ltrs|oz|lbs|kilo)\b', clean_text))
    has_valid_units = bool(re.search(r'\b\d+\s*(g|kg|ml|l|m|cm|gm)\b', clean_text)) or any(k in clean_text for k in ['net wt', 'net weight', 'net qty', 'net quantity', 'net vol', 'volume', 'weight', '100g', '200g', '500g', '1kg', '50ml', '100ml', '500ml', '1l'])
    
    if has_illegal_units:
        checks.append({"rule": "Rule 6(1)(c): Standard Metric Units", "status": "VIOLATION", "detail": "Non-standard unit used (e.g. 'gms'/'ltr' instead of 'g'/'l')"})
        analytics_data["violation_counts"]["standard_units"] += 1
    elif has_valid_units:
        checks.append({"rule": "Rule 6(1)(c): Standard Metric Units", "status": "PASS", "detail": "Standard metric unit declaration detected"})
    else:
        checks.append({"rule": "Rule 6(1)(c): Standard Metric Units", "status": "WARNING", "detail": "Net quantity not detected on this display panel"})

    # Rule 4: Date of Packing / Manufacture
    has_date_tag = any(k in clean_text for k in ['mfg', 'pkd', 'mfd', 'date', 'packed', 'pkg', 'batch', 'use by', 'expiry', 'exp', 'best before', 'lot'])
    has_date_format = bool(re.search(r'\b\d{1,2}[/-]\d{2,4}\b', clean_text)) or any(m in clean_text for m in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', '2024', '2025', '2026'])
    
    if has_date_tag or has_date_format:
        checks.append({"rule": "Rule 6(1)(d): Month & Year of Packing", "status": "PASS", "detail": "Manufacturing / Packing date detected"})
    else:
        checks.append({"rule": "Rule 6(1)(d): Month & Year of Packing", "status": "VIOLATION", "detail": "Month and Year of packing not detected"})

    # Rule 5: Consumer Helpline & Grievance
    has_email = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', clean_text)) or "care@" in clean_text or "feedback@" in clean_text
    has_phone = bool(re.search(r'\b(1800|\+?91|0)?\d{6,10}\b', clean_text)) or any(k in clean_text for k in ['care', 'helpline', 'contact', 'toll free', 'tel', 'phone', 'customer', 'consumer'])
    
    if has_email or has_phone:
        checks.append({"rule": "Rule 6(1)(g): Consumer Care Details", "status": "PASS", "detail": "Consumer grievance helpline/contact detected"})
    else:
        checks.append({"rule": "Rule 6(1)(g): Consumer Care Details", "status": "VIOLATION", "detail": "Consumer grievance email/phone not found"})
        analytics_data["violation_counts"]["consumer_care"] += 1

    # Rule 6: Manufacturer / Packer Details
    has_mfg = any(k in clean_text for k in ['mfd by', 'mfg by', 'manufactured', 'packed by', 'marketed by', 'pvt ltd', 'ltd', 'plot', 'foods', 'industries', 'consumer', 'corp', 'road', 'sector', 'nagar', 'industrial'])
    if has_mfg:
        checks.append({"rule": "Rule 6(1)(a): Manufacturer Details", "status": "PASS", "detail": "Manufacturer / Packer address details found"})
    else:
        checks.append({"rule": "Rule 6(1)(a): Manufacturer Details", "status": "WARNING", "detail": "Manufacturer details not detected on this panel"})

    # Calculate Score
    pass_count = sum(1 for c in checks if c["status"] == "PASS")
    total_rules = len(checks)
    score = int((pass_count / total_rules) * 100)

    # Detect Company / Product Name for the report
    detected_mfg = "Packaged Product Label"
    for line in raw_lines:
        if any(w in line.lower() for w in ['ltd', 'foods', 'industries', 'pvt', 'corp', 'wellness', 'beverages', 'chips', 'biscuit']):
            detected_mfg = line
            break

    issues_count = sum(1 for c in checks if c["status"] != "PASS")
    if score >= 80:
        status_label = "Compliant"
        analytics_data["compliant"] += 1
    elif score >= 60:
        status_label = "Needs Review"
        analytics_data["need_review"] += 1
    else:
        status_label = "Non-Compliant"
        analytics_data["violations_flagged"] += 1
        analytics_data["notices_issued"] += 1

    # -------------------------------------------------------------
    # UPDATE LIVE ANALYTICS (Real-time Calculation)
    # -------------------------------------------------------------
    analytics_data["total_scans"] += 1

    now_date = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    analytics_data["recent_history"].insert(0, {
        "product": detected_mfg[:28],
        "date": now_date,
        "status": status_label,
        "score": score,
        "issues": issues_count
    })
    analytics_data["recent_history"] = analytics_data["recent_history"][:8]

    # Clean memory immediately after scan finishes
    gc.collect()

    return {
        "score": score,
        "status": status_label,
        "mfg_name": detected_mfg,
        "raw_text_lines": raw_lines,
        "boxes": boxes,
        "checks": checks
    }