import hashlib
import re
import cv2
import numpy as np
import pytesseract
import requests
import streamlit as st
from collections import Counter

st.set_page_config(page_title="Proxy MTG Scanner", layout="centered")
st.title("🎴 MTG Proxy Scanner")

# Initialize session state variables
if "decklist" not in st.session_state:
  st.session_state.decklist = []
if "last_scanned_hash" not in st.session_state:
  st.session_state.last_scanned_hash = ""

# Camera input for mobile browsers
picture = st.camera_input("Take a photo of the card")

if picture:
  # Read image bytes
  bytes_data = picture.getvalue()

  # Create a unique fingerprint hash for the current photo
  current_photo_hash = hashlib.md5(bytes_data).hexdigest()

  nparr = np.frombuffer(bytes_data, np.uint8)
  img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

  # Crop top ~15% (Card Title Area)
  h, w, _ = img.shape
  header = img[0 : int(h * 0.15), 0:w]

  st.image(header, caption="What the OCR scanner sees")

  # Preprocessing for OCR
  gray = cv2.cvtColor(header, cv2.COLOR_BGR2GRAY)

  # Run Tesseract OCR
  raw_text = pytesseract.image_to_string(gray).strip()

  if raw_text:
    # Clean text to alphanumeric characters and spaces
    clean_text = re.sub(r"[^a-zA-Z\s]", "", raw_text)
    
    # Isolate the first 3 words for a clean Scryfall search
    search_query = " ".join(clean_text.split()[:3])

    if search_query:
      res = requests.get(
          f"https://api.scryfall.com/cards/named?fuzzy={search_query}",
          headers={"User-Agent": "MTGProxyScanner/1.0"},
      )

      if res.status_code == 200:
        card = res.json()
        card_name = card.get("name")

        st.success(f"Matched: **{card_name}**")

        # Display official Scryfall image preview
        if "image_uris" in card:
          st.image(card["image_uris"]["normal"], width=220)

        # AUTOMATIC ADDITION LOGIC
        # Only add if this specific photo hasn't been processed yet
        if st.session_state.last_scanned_hash != current_photo_hash:
          st.session_state.decklist.append(card_name)
          st.session_state.last_scanned_hash = current_photo_hash
          st.toast(f"Auto-added '{card_name}' to collection!", icon="⚡")

      else:
        st.error(f"Couldn't match card text: '{search_query}'")
  else:
    st.warning("No text detected. Try adjusting the lighting to reduce glare!")

# Visual divider
st.divider()

# Display Active Collection / Decklist
st.subheader("📋 Scanned Collection")

if st.session_state.decklist:
  # Count occurrences of each card
  counts = Counter(st.session_state.decklist)

  # Format list cleanly for Moxfield export (e.g., "3 Sol Ring")
  formatted_list = "\n".join(
      [f"{count} {card}" for card, count in counts.items()]
  )

  # Show formatted list on screen
  st.code(formatted_list, language="text")

  # Export options
  col1, col2 = st.columns(2)

  with col1:
    # Direct Moxfield .txt download
    st.download_button(
        label="📥 Export to Moxfield (.txt)",
        data=formatted_list,
        file_name="moxfield_decklist.txt",
        mime="text/plain",
    )

  with col2:
    if st.button("🗑️ Clear Collection"):
      st.session_state.decklist = []
      st.session_state.last_scanned_hash = ""
      st.rerun()

else:
  st.info("No cards in collection yet. Take a photo to auto-add!")
