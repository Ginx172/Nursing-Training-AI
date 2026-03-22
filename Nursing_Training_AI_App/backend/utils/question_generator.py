import os
import sys
import json
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from utils.rag_engine import RAGEngine


class QuestionGenerator:
    """Generates nursing interview questions using RAG + Ollama LLM"""

    OLLAMA_URL = "http://localhost:11434/api/generate"
    MODEL = "llama3.1:8b"

    def __init__(self, rag_engine=None):
        if rag_engine is None:
            self.rag = RAGEngine()
        else:
            self.rag = rag_engine

    def _call_ollama(self, prompt, temperature=0.7, max_tokens=2000):
        """Call local Ollama LLM"""
        payload = {
            "model": self.MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        try:
            resp = requests.post(self.OLLAMA_URL, json=payload, timeout=300)
            resp.raise_for_status()
            return resp.json().get("response", "")
        except Exception as e:
            print(f"Ollama error: {e}")
            return ""

    def generate_questions(self, topic, band="Band 5", speciality="General Nursing",
                           num_questions=5, difficulty="intermediate"):
        """Generate interview questions based on nursing knowledge base"""

        # Step 1: Get relevant context from RAG
        search_queries = [
            f"{topic} nursing {speciality}",
            f"{topic} interview question {band}",
            f"{topic} clinical practice guidelines",
        ]

        all_context = []
        for sq in search_queries:
            results = self.rag.search(sq, n_results=3)
            for r in results:
                if r["text"] not in [c["text"] for c in all_context]:
                    all_context.append(r)

        context_text = "\n\n".join([
            f"[From: {c['source']}]\n{c['text'][:400]}" for c in all_context[:4]
        ])

        # Step 2: Build prompt
        prompt = f"""You are an expert NHS nursing interview panel member preparing questions for a {band} {speciality} position.

Based on the following nursing knowledge extracted from medical textbooks and guidelines:

---CONTEXT START---
{context_text}
---CONTEXT END---

Generate exactly {num_questions} interview questions about: {topic}

Difficulty level: {difficulty}

For each question provide:
1. The interview question
2. Key points the candidate should cover in their answer
3. A model answer (what an excellent candidate would say)
4. Which NHS values/competencies this tests

Format your response as JSON array:
[
  {{
    "question": "...",
    "key_points": ["point1", "point2", "point3"],
    "model_answer": "...",
    "competencies_tested": ["competency1", "competency2"],
    "difficulty": "{difficulty}",
    "topic": "{topic}",
    "band": "{band}"
  }}
]

Return ONLY the JSON array, no other text.
"""

        # Step 3: Call Ollama
        print(f"Generating {num_questions} questions about '{topic}' for {band}...")
        response = self._call_ollama(prompt, temperature=0.7)

        # Step 4: Parse response
        questions = self._parse_response(response)
        return questions

    def _parse_response(self, response):
        """Parse LLM response into structured questions"""
        try:
            # Find JSON array in response
            start = response.find("[")
            end = response.rfind("]") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Raw response: {response[:500]}")
        return []

    def generate_scenario_question(self, topic, band="Band 5", speciality="General Nursing"):
        """Generate a clinical scenario-based question"""

        results = self.rag.search(f"{topic} clinical scenario patient case", n_results=5)
        context = "\n\n".join([f"[{r['source']}]\n{r['text'][:400]}" for r in results[:3]])

        prompt = f"""You are an NHS nursing interview examiner for {band} {speciality}.

Using this clinical knowledge:
---
{context}
---

Create ONE realistic clinical scenario question about {topic}.

The scenario should:
- Describe a specific patient situation
- Require the candidate to explain their nursing assessment and actions
- Test clinical reasoning and decision-making
- Be appropriate for {band} level

Format as JSON:
{{
  "scenario": "A detailed patient scenario...",
  "question": "What would you do in this situation?",
  "expected_actions": ["action1", "action2", "action3"],
  "model_answer": "A comprehensive answer...",
  "clinical_skills_tested": ["skill1", "skill2"],
  "topic": "{topic}",
  "band": "{band}",
  "type": "scenario"
}}

Return ONLY the JSON object.
"""
        response = self._call_ollama(prompt, temperature=0.8)
        try:
            start = response.find("{{")
            if start < 0:
                start = response.find("{")
            end = response.rfind("}}") + 2
            if end <= 2:
                end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except:
            pass
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("AI Question Generator - Test")
    print("=" * 60)

    gen = QuestionGenerator()

    # Test 1: Generate interview questions
    questions = gen.generate_questions(
        topic="medication safety and drug administration",
        band="Band 5",
        speciality="A&E Nursing",
        num_questions=3,
        difficulty="intermediate"
    )

    print(f"\nGenerated {len(questions)} questions:\n")
    for i, q in enumerate(questions, 1):
        print(f"Q{i}: {q.get('question', 'N/A')}")
        print(f"    Competencies: {q.get('competencies_tested', [])}")
        print(f"    Key points: {q.get('key_points', [])[:3]}")
        print()

    # Test 2: Generate scenario question
    print("\n" + "=" * 60)
    print("Generating scenario question...")
    scenario = gen.generate_scenario_question(
        topic="sepsis management",
        band="Band 5",
        speciality="A&E Nursing"
    )
    if scenario:
        print(f"\nScenario: {scenario.get('scenario', 'N/A')[:200]}...")
        print(f"Question: {scenario.get('question', 'N/A')}")
        print(f"Skills tested: {scenario.get('clinical_skills_tested', [])}")
