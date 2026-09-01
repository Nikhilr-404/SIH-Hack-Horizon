import easyocr

print("Initializing EasyOCR reader (English)...")
# gpu=False ensures it runs reliably on CPU for quick testing
reader = easyocr.Reader(['en'], gpu=False)

print("EasyOCR is installed and initialized successfully!")

# You can test reading an online sample image or a local image
test_url = 'https://raw.githubusercontent.com/JaidedAI/EasyOCR/master/examples/english.png'
print(f"Reading sample image from: {test_url} ...")

results = reader.readtext(test_url)

print("\n--- Extracted Text ---")
for bbox, text, confidence in results:
    print(f"Text: '{text}'  (Confidence: {confidence:.2f})")
    