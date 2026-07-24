import cv2
import numpy as np
import pytesseract
import requests
import streamlit as st

st.set_page_config(page_title="Proxy MTG Scanner", layout="centered")
st.title("🎴 MTG Proxy Scanner")

# Initialize session state for deck storage
if "decklist" not in st.session_state:
  st.session_state.decklist = []

# Camera input for mobile browsers
picture = st.camera_input("Take a photo of the card")

if picture:
  # Read image bytes
  bytes_data = picture.getvalue()
  nparr = np.frombuffer(bytes_data, np.uint8)
  img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

  # Crop top ~15% (Card Title Area)
  h, w, _ = img.shape
  header = img[0 : int(h * 0.15), 0:w]
  
  # --- NEW DEBUG VISUAL ---
  st.image(header, caption="What the OCR scanner sees (Check for glare!)")

  # Preprocessing for cleaner OCR text extraction
  gray = cv2.cvtColor(header, cv2.COLOR_BGR2GRAY)

  # Run Tesseract OCR
  extracted_text = pytesseract.image_to_string(gray).strip()
  
  # --- NEW DEBUG TEXT ---
  st.info(f"🔍 Raw Text Detected: '{extracted_text}'")

  if extracted_text:
    # Query Scryfall Fuzzy API
    res = requests.get(
        f"https://api.scryfall.com/cards/named?fuzzy={extracted_text}",
        headers={"User-Agent": "MTGProxyScanner/1.0"},
    )
    # ... (Keep the rest of your API matching code the same)
  else:
    st.warning("No text detected. Try adjusting the lighting to reduce glare!")
    )

    if res.status_code == 200:
      card = res.json()
      card_name = card.get("name")

      st.success(f"Matched: **{card_name}**")

      # Display official Scryfall image preview
      if "image_uris" in card:
        st.image(card["image_uris"]["normal"], width=220)

      # Add card to list button
      if st.button(f"Add '{card_name}' to Decklist"):
        st.session_state.decklist.append(card_name)
        st.toast(f"Added {card_name}!", icon="✅")
    else:
      st.error(f"Couldn't match card text: '{extracted_text}'")

# Visual divider
st.divider()

# Display Active Decklist
st.subheader("📋 Current Decklist")
if st.session_state.decklist:
  # Format for Moxfield / Archidekt (Count + Name)
  formatted_list = "\n".join(
      [f"1 {card}" for card in st.session_state.decklist]
  )
  st.code(formatted_list, language="text")

  if st.button("Clear Decklist"):
    st.session_state.decklist = []
    st.rerun()
else:
  st.info("No cards scanned yet.")
