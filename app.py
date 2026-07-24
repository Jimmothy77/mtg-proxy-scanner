import cv2
import numpy as np
import pytesseract
import requests
import streamlit as st
import re  # <--- NEW: Add this to the top of your file!

# ... [Keep your page config and camera setup the same] ...

  # Run Tesseract OCR
  raw_text = pytesseract.image_to_string(gray).strip()
  
  st.info(f"🔍 Raw Text Detected: '{raw_text}'")

  if raw_text:
    # --- NEW TEXT CLEANUP BLOCK ---
    # Strip out all numbers, punctuation, and weird symbols (keep only letters and spaces)
    clean_text = re.sub(r'[^a-zA-Z\s]', '', raw_text)
    
    # Grab just the first 3 valid words to send to Scryfall
    search_query = " ".join(clean_text.split()[:3])
    
    st.info(f"✨ Cleaned Query for Scryfall: '{search_query}'")

    # Query Scryfall Fuzzy API using the cleaned query
    res = requests.get(
        f"https://api.scryfall.com/cards/named?fuzzy={search_query}",
        headers={"User-Agent": "MTGProxyScanner/1.0"},
    )
    
    # ... [Keep the rest of your success/error code exactly the same] ...
  
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
