import unittest
from unittest.mock import patch

from backend.notifier import app
from backend.vocabulary_agent import (
    generate_quiz,
    get_vocabulary_word,
    orchestrate_chat,
    search_vocabulary,
)


WORDS = [
    {
        "id": 1,
        "word": "lucid",
        "definition": "Expressed clearly and easy to understand.",
        "meaning": "Clear in thought or expression.",
        "synonyms": ["clear", "coherent"],
        "example": "She gave a lucid explanation.",
    },
    {
        "id": 2,
        "word": "opaque",
        "definition": "Difficult to understand or not transparent.",
        "meaning": "Not allowing light to pass through.",
        "synonyms": ["unclear"],
        "example": "The instructions were opaque.",
    },
    {
        "id": 3,
        "word": "resilient",
        "definition": "Able to recover quickly from difficulty.",
        "meaning": "Strong and adaptable.",
        "synonyms": ["tough"],
        "example": "The resilient team recovered.",
    },
    {
        "id": 4,
        "word": "candid",
        "definition": "Truthful and straightforward.",
        "meaning": "Open and sincere.",
        "synonyms": ["frank"],
        "example": "He gave a candid answer.",
    },
]


class VocabularyAgentTests(unittest.TestCase):
    def test_exact_lookup_ignores_case_and_supports_id(self):
        self.assertEqual(get_vocabulary_word(WORDS, "LUCID")["word"], "lucid")
        self.assertEqual(get_vocabulary_word(WORDS, "2")["word"], "opaque")
        self.assertIsNone(get_vocabulary_word(WORDS, "missing"))

    def test_search_ranks_exact_word_and_matches_synonyms(self):
        self.assertEqual(search_vocabulary(WORDS, "lucid")[0]["word"], "lucid")
        self.assertEqual(search_vocabulary(WORDS, "coherent")[0]["word"], "lucid")

    def test_quiz_has_unique_choices_and_answer(self):
        questions = generate_quiz(WORDS, count=2)
        self.assertEqual(len(questions), 2)
        for question in questions:
            self.assertIn(question["answer"], question["choices"])
            self.assertEqual(len(question["choices"]), len(set(question["choices"])))

    def test_chat_uses_dictionary_tool_and_returns_frontend_shape(self):
        result = orchestrate_chat("What does LUCID mean?", WORDS)
        self.assertEqual(result["tools"], ["get_vocabulary_word"])
        self.assertIn("Expressed clearly", result["response"])

    def test_chat_endpoint_returns_expected_response(self):
        with patch("backend.notifier.load_words", return_value=WORDS):
            response = app.test_client().post(
                "/chat",
                json={"message": "define lucid", "session": "test"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("chat", response.get_json())
        self.assertIn("response", response.get_json()["chat"])

    def test_chat_endpoint_rejects_empty_message(self):
        response = app.test_client().post("/chat", json={"message": "  "})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "message is required")

    def test_chat_endpoint_rejects_oversized_message(self):
        response = app.test_client().post("/chat", json={"message": "x" * 1201})
        self.assertEqual(response.status_code, 413)

    def test_chat_endpoint_allows_github_pages_origin(self):
        response = app.test_client().options(
            "/chat",
            headers={
                "Origin": "https://shru98sri-web.github.io",
                "Access-Control-Request-Method": "POST",
            },
        )
        self.assertEqual(
            response.headers["Access-Control-Allow-Origin"],
            "https://shru98sri-web.github.io",
        )


if __name__ == "__main__":
    unittest.main()
