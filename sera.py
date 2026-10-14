import asyncio
from datetime import datetime
import io
import os
import re
import sys
import time
import pygame
import speech_recognition as sr
from groq import Groq
import edge_tts

# Terminal Encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# -------------------------------------------------------------
# GROQ API KEY
# -------------------------------------------------------------
GROQ_API_KEY = "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"

try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"⚠️ Groq client initialization error: {e}", flush=True)

pygame.mixer.init()


# 1. Text-to-Speech
async def text_to_speech(text, output_file="sera_temp.mp3"):
    try:
        voice = "hi-IN-SwaraNeural"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)

        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()
        if os.path.exists(output_file):
            os.remove(output_file)
    except Exception as e:
        print(f"⚠️ Audio playback error: {e}", flush=True)


# 2. Speech-to-Text
def listen():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("\n🎤 Sera sun rahi hai...", flush=True)
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            recognizer.dynamic_energy_threshold = True
            try:
                audio = recognizer.listen(source, timeout=6, phrase_time_limit=15)
                print("⚡ Soch kar deep answer taiyar kar rahi hoon...", flush=True)
                query = recognizer.recognize_google(audio, language="en-IN")
                print(f"👤 Aapne kaha: {query}", flush=True)
                return query
            except sr.UnknownValueError:
                return ""
            except sr.RequestError:
                print("❌ Network connection error.", flush=True)
                return ""
            except Exception:
                return ""
    except Exception as e:
        print(f"⚠️ Microphone error: {e}", flush=True)
        return ""


# 3. AI Brain (Focused on Deep & Accurate Answers)
def get_ai_response(prompt):
    # System prompt jo model ko deep aur detail me samjhane ke liye guide karega
    system_prompt = (
        "You are Sera, a highly knowledgeable and intelligent academic companion. "
        "When the user asks a question, do not rush or give a short answer. "
        "Provide a comprehensive, highly accurate, and deeply explained answer in clear, conversational Hinglish. "
        "CRITICAL FOR VOICE: Do NOT use markdown, bullet points, numbers, asterisks (*), hashtags (#), brackets, or symbols. "
        "Write in detailed, flowy paragraphs suitable for spoken voice output."
    )

    # Groq ke sabse stable aur powerful models jo detail me answer dete hain
    models_to_try = [
        "llama-3.1-70b-versatile",
        "llama3-70b-8192"
    ]

    for model_name in models_to_try:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5, # Thoda low temperature rakha hai taaki accurate aur exact facts de
                max_tokens=1200, # Bada response allow karne ke liye taaki details miss na ho
            )
            
            raw_text = completion.choices[0].message.content
            clean_text = re.sub(r'[*#_~()`"\[\]\{\}>]', '', raw_text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            return clean_text
        except Exception as e:
            print(f"⚠️ Model '{model_name}' failed with error: {e}", flush=True)
            continue

    return "Arey yaar, server response nahi de raha. Ek baar fir se bolna!"


# 4. Local Commands
def handle_local_commands(user_input):
    user_input_lower = user_input.lower()
    time_keywords = ["time", "samay", "waqt", "baje"]
    date_keywords = ["date", "tareekh", "tarikh", "din"]

    if any(keyword in user_input_lower for keyword in time_keywords):
        now = datetime.now()
        current_time = now.strftime("%I:%M %p")
        return f"Abhi samay {current_time} ho raha hai dost!"

    if any(keyword in user_input_lower for keyword in date_keywords):
        now = datetime.now()
        current_date = now.strftime("%d %B %Y")
        return f"Aaj ki date {current_date} hai dost!"

    return None


# 5. Main Loop
def main():
    print("\n==========================================", flush=True)
    print("    ✨ SERA (DEEP & ACCURATE) READY ✨    ", flush=True)
    print("==========================================\n", flush=True)

    asyncio.run(
        text_to_speech("Hello dost! Main Sera hoon. Ab aapko har sawal ka poora aur sahi detail answer milega.")
    )

    while True:
        try:
            user_input = listen()

            if user_input:
                if any(word in user_input.lower() for word in ["exit", "bye", "stop", "band karo"]):
                    asyncio.run(text_to_speech("Alvida dost! Apna bohot saara khayal rakhna."))
                    print("Sera stopped.", flush=True)
                    break

                local_response = handle_local_commands(user_input)

                if local_response:
                    response = local_response
                else:
                    response = get_ai_response(user_input)

                print(f"🤖 Sera: {response}", flush=True)
                asyncio.run(text_to_speech(response))

        except KeyboardInterrupt:
            print("\nSera manually stopped.", flush=True)
            break
        except Exception as e:
            print(f"⚠️ Loop error caught: {e}", flush=True)
            time.sleep(1)


if __name__ == "__main__":
    main()