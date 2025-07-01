from openai import OpenAI
client = OpenAI()
import streamlit as st
# import matplotlib.pyplot as plt
import speech_recognition as sr
from gtts import gTTS
# import random
import os
import tempfile
import shutil
import subprocess
import platform
import pygame
import time
import atexit
from datetime import datetime, timedelta

titel_container = st.container()
klant_container = st.container()
tekst_container = st.container()

# Instellingen
recognizer = sr.Recognizer()
# recognizer.energy_threshold = 50
#     This is basically how sensitive the recognizer is to when recognition should start. 
#     Higher values mean that it will be less sensitive, which is useful if you are in a loud room.
#     This value depends entirely on your microphone or audio data. 
#     There is no one-size-fits-all value, but good values typically range from 50 to 4000.       
st.sidebar.title("Instellingen")
recognizer.energy_threshold = st.sidebar.slider("Opname gevoeligheid", 1000, 4000, 2000)
# recognizer.dynamic_energy_threshold = False
# max_opnametijd = st.sidebar.slider("Maximale opnametijd (seconden)", 10, 300, 60)
# opnamemodus_volledig = st.sidebar.radio("🔊 Opnamemodus", ["Segmenten (kort)", "Volledig (lang)"]) == "Volledig (lang)"
# exporteer_transcriptie = st.sidebar.button("📄 Exporteer gesprek & feedback")
# audio_afspelen = st.sidebar.checkbox("Speel AI-reactie automatisch af", value=True)
# live_transcriptie = st.sidebar.checkbox("Toon live transcriptie van spreker", value=True)
# live_ai_transcriptie = st.sidebar.checkbox("Toon transcriptie van klantreactie", value=True)

opname_timeout = st.sidebar.slider("Opname timeot", 1, 30, 15)
# Onduidelijk waarvoor dit is de tijd stilte na gesprek 

# Pad voor tijdelijk audiobestand
audio_pad = os.path.join(tempfile.gettempdir(), "ai_reactie.mp3")

# Verwijder tijdelijk audiobestand bij afsluiten + opschonen oude bestanden
def opruimen_audio():
    print("[LOG] Opruimen audio gestart")
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        time.sleep(0.5)
    except Exception as e:
        print(f"[ERROR] Bij stop/quit mixer: {e}")

    try:
        temp_dir = tempfile.gettempdir()
        for bestand in os.listdir(temp_dir):
            pad = os.path.join(temp_dir, bestand)
            if bestand.endswith(".mp3") or bestand.endswith(".wav") or bestand.endswith(".tmp"):
                try:
                    os.remove(pad)
                    print(f"[LOG] Verwijderd: {pad}")
                except Exception as e:
                    print(f"[ERROR] Kon {pad} niet verwijderen: {e}")
    except Exception as e:
        print(f"[ERROR] Tijdens opruimen temp-dir: {e}")

atexit.register(opruimen_audio)

if "opname_klant" not in st.session_state:
    st.session_state["opname_klant"] = False
if "opname_aan" not in st.session_state:
    st.session_state["opname_aan"] = False
if "wacht_op_reactie" not in st.session_state:
    st.session_state["wacht_op_reactie"] = False
if "gesprek_einde" not in st.session_state:
    st.session_state["gesprek_einde"] = False
if "gesprekshistorie" not in st.session_state:
    st.session_state["gesprekshistorie"] = ""


with titel_container:
     st.title("AI Gesprekstraining- The Trusted Advisor (live microfoon & automatische audio-uitvoer)")
with klant_container:
    st.markdown("### 👤 Klantbeschrijving")
    klant_beschrijving = "Geef een beschrijving het bedrijf van de klant, de klant en de manier waarop je wil dat de klant reageert"
    with klant_container:
        st.write(klant_beschrijving) 
with tekst_container:
    st.markdown("### 💬 Gesprek")

col_opname = st.columns([4.15, 0.85])
with col_opname[0]:
    opname_klant = st.button("1. 🎤 Beschrijf de klant die je wil als tegenspeler")
with col_opname[0]:
    opname_klik = st.button("2. 🎤 Start input")
with col_opname[0]:
    gesprek_einde = st.button("Stop het gesprek")

ai_text = ""

if opname_klant:
    print("[LOG] Opname klant geklikt")
    st.session_state["opname_klant"] = True
    st.session_state["opname_aan"] = True
  
if opname_klik:
    print("[LOG] Opnameknop geklikt")
    st.session_state["opname_aan"] = True

if gesprek_einde:
    print("[LOG] Einde gesprek")
    st.session_state["gesprek_einde"] = True


if st.session_state["opname_aan"]:
   st.session_state["visuele_melding"] = st.info("⏳ Voorbereiding... de opname start over 1 seconde.")
   print("Microfoon gevoeligheid:", recognizer.energy_threshold)
   with sr.Microphone() as source:     
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("[LOG] Ambient noise aangepast") 
        time.sleep(1)
        st.session_state["visuele_melding"].empty()
        st.session_state["microfoon_indicator"] = st.markdown("<small style='color:gray;'>🎤 Microfoon staat aan...</small>", unsafe_allow_html=True)
        print("[LOG] Start opname")
        try:
           audio_data = recognizer.listen(source, timeout=opname_timeout, phrase_time_limit=300)
        except Exception as e:
           print(f"[ERROR] Bij audio listen: {e}")
        st.session_state["microfoon_indicator"].empty()
        print("[LOG] Opname verwerken")
        try:
            print("[LOG] Opname verwerken Try")
            if st.session_state["opname_klant"]:
               klant_beschrijving = recognizer.recognize_google(audio_data,language="nl-NL")
               st.session_state["klant_beschrijving"] = klant_beschrijving
 #              st.markdown("### 👤 Klantbeschrijving")
               with klant_container:
                   st.write(klant_beschrijving)
               print("[LOG] klantbeschrijving:", klant_beschrijving)
            else:
               volledige_tekst = recognizer.recognize_google(audio_data,language="nl-NL")
  #             st.markdown("### 💬 Gesprek")
               with tekst_container:
                   st.write(volledige_tekst)
               print("[LOG] gesprekstekst:", volledige_tekst)
               st.session_state["gesprekshistorie"] += f"\nJij: {volledige_tekst}"
            st.success("🎧 Transcriptie voltooid.")
            print("[LOG] Transcriptie voltooid")
        except sr.UnknownValueError:
            st.error("Kon spraak niet herkennen.")
            print("[LOG] Kon spraak niet herkennen.")
        except sr.RequestError as e:
            st.error(f"Spraakservice niet bereikbaar: {e}")
            print("[LOG] Spraakservice niet bereikbaar: {e}")
   if st.session_state["opname_klant"]:
      st.session_state["wacht_op_reactie"] = False
   else:
      st.session_state["wacht_op_reactie"] = True
   st.session_state["opname_klant"] = False
   st.session_state["opname_aan"] = False

if st.session_state["wacht_op_reactie"]:
   print("[LOG] wachten op reactie AI")
   print("[LOG] Hele gesprekstekst:", st.session_state["gesprekshistorie"])
   with st.spinner("🧠 AI denkt na over een reactie..."):
        response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Je speelt de rol van een klant in een professioneel gesprek. Reageer realistisch en opbouwend. De rol die je speelt is die van '{st.session_state['klant_beschrijving']}'"},
            {"role": "user", "content": st.session_state["gesprekshistorie"]}
        ]
    )
   ai_antwoord = response.choices[0].message.content
   tts = gTTS(text=ai_antwoord, lang='nl')
   if os.path.exists(audio_pad):
      try:
         if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
         os.remove(audio_pad)
      except Exception as e:
            print(f"[ERROR] Bij audio opruimen: {e}")
   tts.save(audio_pad)
   try:
      pygame.mixer.init()
      pygame.mixer.music.load(audio_pad)
      pygame.mixer.music.play()
      while pygame.mixer.music.get_busy():
          pygame.time.Clock().tick(10)
   except Exception as e:
      st.warning(f"Kan audio niet afspelen: {e}")
   st.session_state["wacht_op_reactie"] = False
   st.session_state["gesprekshistorie"] += f"\nKlant: {ai_antwoord}"
   print("[LOG] Hele gesprekstekst:", st.session_state["gesprekshistorie"])
   with klant_container:
      st.write(st.session_state["klant_beschrijving"])
#   st.success("✅ Klant heeft gereageerd.")

if st.session_state["gesprek_einde"]:
   print("[LOG] Gesprek wordt beëindigd en evaluatie volgt")
   st.success("Het gesprek is beëindigd. Hieronder volgt jouw feedback:")
   feedback_prompt = [
        {"role": "system", "content": "Je bent een coach die feedback geeft op een gesprek volgens de principes van The Trusted Advisor: geloofwaardigheid, betrouwbaarheid, intimiteit en egogerichtheid."},
        {"role": "user", "content": st.session_state["gesprekshistorie"]}
   ]
   response = client.chat.completions.create(
        model="gpt-4",
        messages=feedback_prompt
   )
   feedback = response.choices[0].message.content
   st.write("**Feedback op jouw bijdrage:**")
   st.write(feedback)
   try:
      opruimen_audio()
   except error:
      print("[LOG] Laatste bestand opgeruimd")
      st.session_state["gesprek_einde"] = False
