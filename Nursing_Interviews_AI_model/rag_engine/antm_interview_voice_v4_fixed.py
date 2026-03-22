import requests
import json
import os
import pyttsx3
import speech_recognition as sr
import time
from datetime import datetime

LMSTUDIO_API = "http://localhost:1234/v1/completions"
SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

engine = pyttsx3.init()
engine.setProperty("rate", 170)

def speak(text):
    print(f"\n🔊 Speaking: {text}")
    engine.say(text)
    engine.runAndWait()

def listen_until_silence(pause_threshold=2.0):
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = pause_threshold
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎙️ Listening... Speak now.")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"📝 Recognized: {text}")
        return text.strip().lower()
    except sr.UnknownValueError:
        print("⚠️ Could not understand.")
        return ""
    except sr.RequestError as e:
        print(f"⚠️ Speech error: {e}")
        return ""

def ask_lmstudio(prompt):
    payload = {
        "model": "mistral",
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": 300
    }
    try:
        r = requests.post(LMSTUDIO_API, json=payload)
        return r.json()["choices"][0]["text"].strip()
    except Exception as e:
        return f"[ERROR] {e}"

def wait_for_user_confirmation():
    speak("Am înțeles. Vrei să adaugi ceva sau pot merge mai departe?")
    response = listen_until_silence()
    return response

def main():
    print("\n🎙️ ANTM – Voice Interview Simulation (v4 FIXED: One Question at a Time)\n")
    speak("Bun venit la simularea realistă a interviului. Voi pune o întrebare pe rând.")

    role = input("👉 Role to simulate (e.g., Band 5 nurse):\n> ").strip()

    intro_prompt = (
        f"You are the interviewer for a realistic mock interview for the role of {role}. "
        "Ask only ONE appropriate interview question for that role. "
        "DO NOT simulate the user's answer. Do not generate multiple questions. "
        "Ask one clear question, then STOP. Wait for user's real response (via microphone)."
    )

    qa_log = []
    question = ask_lmstudio(intro_prompt)
    i = 1

    while True:
        print(f"\n🧑‍⚕️ Question {i}: {question}")
        speak(f"Întrebarea {i}: {question}")

        full_answer = ""
        while True:
            response = listen_until_silence()
            if "end interview" in response:
                break
            if "repeat" in response:
                speak("Sigur, repet întrebarea.")
                speak(question)
                continue
            full_answer += " " + response

            followup = wait_for_user_confirmation()
            if "no" in followup or "add" in followup or "continue" in followup:
                speak("Bine, continuă când ești gata.")
                continue
            if "yes" in followup or "go ahead" in followup or "finished" in followup:
                break
            else:
                speak("Am înțeles. Dacă mai vrei să adaugi ceva, spune acum.")
                continue

        if "end interview" in response:
            break

        qa_log.append({"question": question, "answer": full_answer.strip()})

        context = "\n".join([f"Q{i+1}: {x['question']}\nA{i+1}: {x['answer']}" for i, x in enumerate(qa_log)])
        next_prompt = (
            f"You are continuing the mock interview for the role of {role}. "
            "Ask only the NEXT interview question. Do NOT simulate any answers. Stop after one question.\n\n"
            f"{context}"
        )

        question = ask_lmstudio(next_prompt)
        i += 1

    # Generate feedback
    context = "\n".join([f"Q{i+1}: {x['question']}\nA{i+1}: {x['answer']}" for i, x in enumerate(qa_log)])
    feedback_prompt = (
        f"This was a full mock interview for the role of {role}. Please give detailed, question-by-question feedback.\n\n{context}"
    )
    feedback = ask_lmstudio(feedback_prompt)

    print("\n✅ FEEDBACK:\n")
    print(feedback)
    speak("Interviul s-a încheiat. Iată feedback-ul tău.")
    speak(feedback)

    session = {
        "role": role,
        "qa": qa_log,
        "feedback": feedback,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    filename = os.path.join(SESSION_DIR, f"interview_voice_v4FIXED_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(session, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Sesiune salvată: {filename}")

if __name__ == "__main__":
    main()
