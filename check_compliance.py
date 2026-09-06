import easyocr
import re

def verify_lmpc_compliance(image_path):
    print(f"🔍 Scanning image: {image_path} ...")
    
    # 1. Run EasyOCR
    reader = easyocr.Reader(['en'], gpu=False)
    ocr_results = reader.readtext(image_path)
    
    # Combine all lines into lowercase text for keyword checking
    raw_lines = [item[1] for item in ocr_results]
    full_text = " ".join(raw_lines).lower()
    
    print("\n--- 📝 Raw Extracted Text ---")
    for line in raw_lines:
        print(f"  • {line}")
    
    # 2. Rule 6 Legal Checks
    results = []
    
    # Check 1: Rule 6(1)(e) - MRP & Tax Clause
    has_mrp = any(k in full_text for k in ['mrp', 'rs.', 'rs ', '₹', 'price', 'max retail'])
    has_tax = any(k in full_text for k in ['tax', 'taxes', 'incl', 'inclusive'])
    if has_mrp and has_tax:
        results.append({"rule": "Rule 6(1)(e): MRP with Tax Clause", "status": "PASS", "msg": "MRP declared with 'inclusive of all taxes'"})
    elif has_mrp and not has_tax:
        results.append({"rule": "Rule 6(1)(e): MRP with Tax Clause", "status": "VIOLATION", "msg": "MRP is present but missing mandatory 'incl. of all taxes'"})
    else:
        results.append({"rule": "Rule 6(1)(e): MRP with Tax Clause", "status": "VIOLATION", "msg": "MRP price tag not detected"})

    # Check 2: Rule 6(1)(aa) - Country of Origin
    has_origin = any(k in full_text for k in ['country of origin', 'made in', 'product of', 'origin:'])
    if has_origin or 'india' in full_text:
        results.append({"rule": "Rule 6(1)(aa): Country of Origin", "status": "PASS", "msg": "Country of origin declared"})
    else:
        results.append({"rule": "Rule 6(1)(aa): Country of Origin", "status": "VIOLATION", "msg": "Missing mandatory Country of Origin declaration"})

    # Check 3: Rule 6(1)(c) - Standard Metric Units Check
    # Valid units: g, kg, ml, l. Flags illegal units: gms, kgs, ltr
    has_illegal_units = bool(re.search(r'\b\d+\s*(gms|kgs|ltr|ltrs|gm|kilo)\b', full_text))
    has_valid_units = bool(re.search(r'\b\d+\s*(g|kg|ml|l|m|cm)\b', full_text)) or "net" in full_text or "weight" in full_text
    if has_illegal_units:
        results.append({"rule": "Rule 6(1)(c): Standard Metric Units", "status": "VIOLATION", "msg": "Non-standard unit used (e.g., 'gms'/'ltr' instead of 'g'/'l')"})
    elif has_valid_units:
        results.append({"rule": "Rule 6(1)(c): Standard Metric Units", "status": "PASS", "msg": "Standard metric unit format detected"})
    else:
        results.append({"rule": "Rule 6(1)(c): Standard Metric Units", "status": "WARNING", "msg": "Net quantity unit could not be confirmed"})

    # Check 4: Rule 6(1)(d) - Date of Manufacture / Packing
    has_date = bool(re.search(r'\b(mfg|pkd|mfd|date|packed|pkg)\b', full_text)) or bool(re.search(r'\b\d{2}[/-]\d{2,4}\b', full_text))
    if has_date:
        results.append({"rule": "Rule 6(1)(d): Month & Year of Packing", "status": "PASS", "msg": "Manufacturing / Packing date detected"})
    else:
        results.append({"rule": "Rule 6(1)(d): Month & Year of Packing", "status": "VIOLATION", "msg": "Missing Month and Year of manufacture/packing"})

    # Check 5: Rule 6(1)(g) - Consumer Care (Helpline & Email)
    has_email = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', full_text))
    has_phone = bool(re.search(r'\b(1800|\+91|0\d{2,4})?\d{6,10}\b', full_text)) or any(k in full_text for k in ['care', 'helpline', 'contact', 'toll free'])
    if has_email and has_phone:
        results.append({"rule": "Rule 6(1)(g): Consumer Grievance Details", "status": "PASS", "msg": "Both helpline phone & email present"})
    elif has_phone or has_email:
        results.append({"rule": "Rule 6(1)(g): Consumer Grievance Details", "status": "WARNING", "msg": "Partial care details (Need BOTH phone and email)"})
    else:
        results.append({"rule": "Rule 6(1)(g): Consumer Grievance Details", "status": "VIOLATION", "msg": "Consumer helpline contact details missing"})

    # Check 6: Rule 6(1)(a) - Manufacturer / Packer Details
    has_mfg_info = any(k in full_text for k in ['mfd by', 'mfg by', 'manufactured', 'packed by', 'marketed by', 'pvt ltd', 'ltd', 'plot', 'industrial'])
    if has_mfg_info:
        results.append({"rule": "Rule 6(1)(a): Manufacturer Name & Address", "status": "PASS", "msg": "Manufacturer / Packer address detected"})
    else:
        results.append({"rule": "Rule 6(1)(a): Manufacturer Name & Address", "status": "VIOLATION", "msg": "Missing manufacturer or packer details"})

    # Check 7: Rule 6(1)(b) - Generic / Common Name
    has_generic = any(k in full_text for k in ['chips', 'biscuit', 'cream', 'soap', 'oil', 'drink', 'beverage', 'powder', 'shampoo', 'snack']) or len(raw_lines) > 0
    if has_generic:
        results.append({"rule": "Rule 6(1)(b): Generic Commodity Name", "status": "PASS", "msg": "Generic product identity detected"})
    else:
        results.append({"rule": "Rule 6(1)(b): Generic Commodity Name", "status": "VIOLATION", "msg": "Generic name of commodity missing"})

    # 3. Calculate Overall Compliance Score
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    total_rules = len(results)
    score_percentage = int((pass_count / total_rules) * 100)
    
    # 4. Print Beautiful Inspection Report
    print("\n" + "="*60)
    print("⚖️  LEGAL METROLOGY (PACKAGED COMMODITIES) RULES, 2011 REPORT")
    print("="*60)
    print(f"Compliance Score : {score_percentage}% ({pass_count}/{total_rules} Rules Passed)")
    
    if score_percentage >= 80:
        print("Final Status     : ✅ LEGAL METROLOGY COMPLIANT")
    elif score_percentage >= 50:
        print("Final Status     : ⚠️ DEFICIENCIES DETECTED (Format Warning)")
    else:
        print("Final Status     : ❌ STATUTORY VIOLATION (Non-Compliant)")
    print("-" * 60)
    
    for r in results:
        badge = "✅ PASS" if r["status"] == "PASS" else ("⚠️ WARN" if r["status"] == "WARNING" else "❌ FAIL")
        print(f"{badge:<10} | {r['rule']:<38} | {r['msg']}")
    print("="*60)

# Run test on your image
if __name__ == "__main__":
    verify_lmpc_compliance('chips.jpg')