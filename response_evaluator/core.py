"""
Response evaluator - Quality scoring for AI responses.

Evaluate relevance, completeness, accuracy, and confidence.
"""

import re
from typing import Dict, List, Tuple


class ResponseEvaluator:
    """Evaluate AI response quality."""

    @staticmethod
    def evaluate_length(response: str, min_words: int = 10, max_words: int = 5000) -> Dict:
        """Evaluate response length."""
        word_count = len(response.split())
        char_count = len(response)

        return {
            "word_count": word_count,
            "char_count": char_count,
            "is_too_short": word_count < min_words,
            "is_too_long": word_count > max_words,
            "score": min(100, (word_count / ((min_words + max_words) / 2)) * 100),
        }

    @staticmethod
    def evaluate_structure(response: str) -> Dict:
        """Evaluate response structure."""
        has_intro = bool(re.search(r"^.{0,100}(overview|summary|introduction|here|following)", response.lower()))
        has_sections = len(re.findall(r"^#{1,3}\s", response, re.MULTILINE)) > 0
        has_lists = bool(re.search(r"^[\s]*[-*•]\s", response, re.MULTILINE))
        has_conclusion = bool(re.search(r"(conclusion|summary|final|wrap|complete)", response.lower()))
        has_formatting = bool(re.search(r"[*_`]|```", response))

        structure_score = (
            (has_intro and 20 or 0) +
            (has_sections and 20 or 0) +
            (has_lists and 20 or 0) +
            (has_conclusion and 20 or 0) +
            (has_formatting and 20 or 0)
        )

        return {
            "has_intro": has_intro,
            "has_sections": has_sections,
            "has_lists": has_lists,
            "has_conclusion": has_conclusion,
            "has_formatting": has_formatting,
            "score": structure_score,
        }

    @staticmethod
    def evaluate_clarity(response: str) -> Dict:
        """Evaluate response clarity."""
        sentences = re.split(r"[.!?]+", response)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

        # Too long sentences reduce clarity
        clarity_score = 100 - min(50, (avg_sentence_length - 15) * 2)
        clarity_score = max(50, clarity_score)

        return {
            "avg_sentence_length": round(avg_sentence_length, 1),
            "sentence_count": len(sentences),
            "score": clarity_score,
        }

    @staticmethod
    def evaluate_technical_accuracy(response: str) -> Dict:
        """Evaluate technical indicators."""
        has_numbers = bool(re.search(r"\d+", response))
        has_citations = bool(re.search(r"\[.*?\]|\(.*?[0-9]{4}.*?\)", response))
        has_code = bool(re.search(r"```|`[^`]+`", response))
        has_links = bool(re.search(r"http|www", response))

        accuracy_score = (
            (has_numbers and 25 or 0) +
            (has_citations and 25 or 0) +
            (has_code and 25 or 0) +
            (has_links and 25 or 0)
        )

        return {
            "has_numbers": has_numbers,
            "has_citations": has_citations,
            "has_code": has_code,
            "has_links": has_links,
            "score": accuracy_score,
        }

    @staticmethod
    def evaluate_completeness(response: str, prompt: str = "") -> Dict:
        """Evaluate if response addresses prompt."""
        response_lower = response.lower()
        prompt_words = set(prompt.lower().split())

        # Check if prompt keywords appear in response
        covered_keywords = sum(1 for word in prompt_words if len(word) > 4 and word in response_lower)
        total_keywords = sum(1 for word in prompt_words if len(word) > 4)

        coverage = (covered_keywords / total_keywords * 100) if total_keywords > 0 else 0

        return {
            "keyword_coverage": round(coverage, 1),
            "covered_keywords": covered_keywords,
            "total_keywords": total_keywords,
            "score": min(100, coverage),
        }

    @staticmethod
    def overall_score(response: str, prompt: str = "") -> Dict:
        """Calculate overall response quality score."""
        length = ResponseEvaluator.evaluate_length(response)
        structure = ResponseEvaluator.evaluate_structure(response)
        clarity = ResponseEvaluator.evaluate_clarity(response)
        accuracy = ResponseEvaluator.evaluate_technical_accuracy(response)
        completeness = ResponseEvaluator.evaluate_completeness(response, prompt)

        # Weighted average
        overall = (
            length["score"] * 0.15 +
            structure["score"] * 0.20 +
            clarity["score"] * 0.20 +
            accuracy["score"] * 0.20 +
            completeness["score"] * 0.25
        )

        return {
            "overall_score": round(overall, 1),
            "length": length,
            "structure": structure,
            "clarity": clarity,
            "accuracy": accuracy,
            "completeness": completeness,
            "rating": _get_rating(overall),
        }

    @staticmethod
    def compare_responses(responses: List[str], prompt: str = "") -> List[Dict]:
        """Compare multiple responses."""
        return sorted(
            [ResponseEvaluator.overall_score(r, prompt) for r in responses],
            key=lambda x: x["overall_score"],
            reverse=True
        )


def _get_rating(score: float) -> str:
    """Get text rating for score."""
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Fair"
    else:
        return "Poor"


def evaluate(response: str, prompt: str = "") -> Dict:
    """Quick evaluation."""
    return ResponseEvaluator.overall_score(response, prompt)


def compare(responses: List[str], prompt: str = "") -> List[Dict]:
    """Quick comparison."""
    return ResponseEvaluator.compare_responses(responses, prompt)


def process(data: str, **kwargs) -> str:
    """Process function."""
    result = evaluate(data)
    return f"Response Score: {result['overall_score']}/100 - {result['rating']}"


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate AI response quality")
    parser.add_argument("response", help="Response to evaluate")
    parser.add_argument("-p", "--prompt", help="Original prompt")

    args = parser.parse_args()

    result = ResponseEvaluator.overall_score(args.response, args.prompt)

    print(f"Overall Score: {result['overall_score']}/100 ({result['rating']})")
    print(f"  Length: {result['length']['score']:.0f}/100")
    print(f"  Structure: {result['structure']['score']:.0f}/100")
    print(f"  Clarity: {result['clarity']['score']:.0f}/100")
    print(f"  Accuracy: {result['accuracy']['score']:.0f}/100")
    print(f"  Completeness: {result['completeness']['score']:.0f}/100")


if __name__ == "__main__":
    main()
