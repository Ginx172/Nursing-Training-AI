import requests
import json
import os
from datetime import datetime

LMSTUDIO_API = "http://localhost:1234/v1/completions"
SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

def ask_lmstudio(prompt):
    payload = {
        "model": "mistral",
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": 512
    }
    response = requests.post(LMSTUDIO_API, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["text"].strip()
    else:
        return f"[ERROR {response.status_code}] {response.text}"

def main():
    print("\n🎙️ ANTM – Structured Interview Simulation (v2)\n")
    role = input("👉 Role for simulation (e.g., Band 6 ward nurse):\n> ").strip()

    prompt_intro = (
        f"You are the interviewer for a mock simulation for the role of {role}. "
        "You will ask ONE interview question at a time, wait for the user's reply, and then proceed. "
        "Never simulate the user's response. At the end, the user will type 'END INTERVIEW AND PROVIDE FEEDBACK' "
        "to receive feedback on their answers.\n\n"
        f"Begin the interview. Introduce yourself and ask the first question for the {role} role."
    )

    full_log = []
    print("\n📡 Starting interview with LM Studio...\n")
    question = ask_lmstudio(prompt_intro)
    i = 1

    while True:
        print(f"\n🧑‍⚕️ Question {i}: {question}")
        answer = input("\n🗣️ Your answer:\n> ").strip()

        if answer.strip().lower().startswith("end interview"):
            break

        full_log.append({"question": question, "answer": answer})

        # Construct prompt for next turn
        context = "\n".join([f"Q{i+1}: {q['question']}\nA{i+1}: {q['answer']}" for i, q in enumerate(full_log)])
        next_prompt = (
            f"You are continuing the mock interview for the {role} role.\n\n"
            f"Here is the conversation so far:\n{context}\n\n"
            f"Please now ask the NEXT interview question. Only the question. Do NOT comment or simulate a response."
        )

        question = ask_lmstudio(next_prompt)
        i += 1

    print("\n🧾 Generating final feedback...\n")

    # Build prompt for feedback
    context = "\n".join([f"Q{i+1}: {q['question']}\nA{i+1}: {q['answer']}" for i, q in enumerate(full_log)])
    feedback_prompt = (
        f"The following is a complete mock interview for the role of {role}. "
        f"Please provide feedback structured per question.\n\n{context}\n\n"
        "Use the feedback format described in your system prompt: "
        "1) Briefly state what was good, 2) List what was missing or could be improved "
        "for each question, 3) Offer a short summary at the end if appropriate."
    )

    feedback = ask_lmstudio(feedback_prompt)
    print("\n✅ FEEDBACK FROM AI:\n")
    print(feedback)

    # Save session
    session_data = {
        "role": role,
        "qa_pairs": full_log,
        "feedback": feedback,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    session_file = os.path.join(SESSION_DIR, f"interview_structured_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Session saved to: {session_file}")

if __name__ == "__main__":
    main()
