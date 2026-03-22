"""
Question Extractor - Extracts interview questions from nursing documents
Uses DocumentReader to parse files, then identifies Q&A patterns
"""

import re
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.document_reader import DocumentReader


class QuestionExtractor:
    """Extracts Q&A pairs from nursing documents"""

    # Patterns that indicate a question
    QUESTION_PATTERNS = [
        r'(?:^|\n)\s*\d+[\.\)]\s*(.+\?)',                          # 1. Question?
        r'(?:^|\n)\s*Q[\.\:\)]\s*(.+\?)',                           # Q. Question?
        r'(?:^|\n)\s*Question[\s\d]*[\.\:]\s*(.+\?)',               # Question 1: ...?
        r'(?:^|\n)\s*(.+\?)\s*(?:Ideal |Model |Sample )?Answer',   # Question? Ideal Answer
        r'(?:^|\n)\s*(?:Tell me|Describe|Explain|How do you|How would you|What (?:do|would|is|are)|Why did|Where do|Can you|Give .* example|Have you)(.+\?)', # Common interview starters
    ]

    # Patterns that indicate an answer
    ANSWER_PATTERNS = [
        r'(?:Ideal |Model |Sample |Suggested |Best )?Answer[\s]*[\.\:\-]\s*["\u201c]?(.+?)(?:["\u201d]?\s*(?:\n\n|\Z))',
        r'A[\.\:\)]\s*(.+?)(?:\n\n|\Z)',
    ]

    @staticmethod
    def extract_from_text(text: str) -> list:
        """Extract Q&A pairs from raw text"""
        pairs = []

        # Strategy 1: Look for "Question? Ideal Answer: ..." pattern
        # This matches the format in your Aintree document
        pattern = r'([^.\n]{15,200}\?)\s*(?:Ideal |Model |Sample )?Answer[\s]*[\.\:\-]\s*["\u201c]?(.+?)(?=[A-Z][^.]{15,200}\?\s*(?:Ideal |Model |Sample )?Answer|$)'
        matches = re.findall(pattern, text, re.DOTALL)

        for q, a in matches:
            q = q.strip()
            a = a.strip().strip('"').strip('\u201c').strip('\u201d').strip()
            if len(q) > 15 and len(a) > 20:
                pairs.append({
                    "question": q,
                    "answer": a[:2000],  # Cap answer length
                    "source": "pattern_match"
                })

        # Strategy 2: Numbered questions with answers
        if not pairs:
            lines = text.split('\n')
            current_q = None
            current_a = []

            for line in lines:
                line = line.strip()
                if not line:
                    if current_q and current_a:
                        pairs.append({
                            "question": current_q,
                            "answer": "\n".join(current_a)[:2000],
                            "source": "numbered"
                        })
                        current_q = None
                        current_a = []
                    continue

                # Check if line is a question
                q_match = re.match(r'^\d+[\.\)]\s*(.+\?)\s*$', line)
                if q_match:
                    if current_q and current_a:
                        pairs.append({
                            "question": current_q,
                            "answer": "\n".join(current_a)[:2000],
                            "source": "numbered"
                        })
                    current_q = q_match.group(1)
                    current_a = []
                elif current_q:
                    current_a.append(line)

            # Don't forget last pair
            if current_q and current_a:
                pairs.append({
                    "question": current_q,
                    "answer": "\n".join(current_a)[:2000],
                    "source": "numbered"
                })

        return pairs

    @staticmethod
    def extract_from_file(file_path: str) -> list:
        """Extract Q&A pairs from a document file"""
        text = DocumentReader.read(file_path)
        if not text:
            return []

        pairs = QuestionExtractor.extract_from_text(text)

        # Add file metadata
        for pair in pairs:
            pair["source_file"] = os.path.basename(file_path)
            pair["source_path"] = file_path

        return pairs

    @staticmethod
    def extract_from_directory(directory: str, recursive: bool = True) -> list:
        """Extract Q&A pairs from all supported files in a directory"""
        all_pairs = []
        path = Path(directory)
        pattern = "**/*" if recursive else "*"

        for file in sorted(path.glob(pattern)):
            if file.is_file() and file.suffix.lower() in DocumentReader.SUPPORTED_FORMATS:
                pairs = QuestionExtractor.extract_from_file(str(file))
                if pairs:
                    print(f"  Found {len(pairs)} Q&A pairs in: {file.name}")
                    all_pairs.extend(pairs)

        return all_pairs

    @staticmethod
    def save_extracted(pairs: list, output_path: str):
        """Save extracted Q&A pairs to JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(pairs, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(pairs)} Q&A pairs to {output_path}")


if __name__ == "__main__":
    # Test with the Aintree interview document
    test_file = r'J:\E-Books\........................._nursing\Nursing Interview\.....Questions_Ideal Answers on Nursing Interviews.DOCX'

    print("Testing QuestionExtractor...")
    print(f"File: {os.path.basename(test_file)}")
    print("-" * 60)

    pairs = QuestionExtractor.extract_from_file(test_file)
    print(f"\nTotal Q&A pairs extracted: {len(pairs)}")

    if pairs:
        print("\nFirst 3 questions:")
        for i, p in enumerate(pairs[:3], 1):
            print(f"\n  Q{i}: {p['question'][:100]}")
            print(f"  A{i}: {p['answer'][:100]}...")

    # Save results
    output = os.path.join(os.path.dirname(__file__), '..', 'data', 'extracted_questions.json')
    os.makedirs(os.path.dirname(output), exist_ok=True)
    QuestionExtractor.save_extracted(pairs, output)
