from __future__ import annotations

import random
import re
from collections.abc import Mapping, Sequence
from typing import Any


Word = Mapping[str, Any]


def _normalize(value: object) -> str:
    return " ".join(re.sub(r"[^\w\s'-]", " ", str(value or "")).split()).casefold()


def get_vocabulary_word(words: Sequence[Word], term: str) -> dict[str, Any] | None:
    normalized_term = _normalize(term)
    if not normalized_term:
        return None

    for word in words:
        if (
            _normalize(word.get("word")) == normalized_term
            or _normalize(word.get("id")) == normalized_term
        ):
            return dict(word)
    return None


def search_vocabulary(
    words: Sequence[Word], query: str, limit: int = 5
) -> list[dict[str, Any]]:
    normalized_query = _normalize(query)
    if not normalized_query:
        raise ValueError("query must not be empty")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 20:
        raise ValueError("limit must be an integer between 1 and 20")

    query_tokens = set(normalized_query.split())
    scored: list[tuple[int, int, dict[str, Any]]] = []

    for index, word in enumerate(words):
        term = _normalize(word.get("word"))
        synonyms = word.get("synonyms", [])
        normalized_synonyms = (
            [_normalize(value) for value in synonyms]
            if isinstance(synonyms, list)
            else []
        )

        score = 0
        if term == normalized_query:
            score = 1000
        elif term.startswith(normalized_query):
            score = 700
        elif normalized_query in term:
            score = 500
        elif normalized_query in normalized_synonyms:
            score = 450
        else:
            searchable = " ".join(
                _normalize(word.get(field))
                for field in ("definition", "meaning", "example", "usage")
            )
            searchable += " " + " ".join(normalized_synonyms)
            if normalized_query in searchable:
                score = 250
            else:
                score = 10 * len(query_tokens.intersection(searchable.split()))

        if score:
            scored.append((score, index, dict(word)))

    scored.sort(key=lambda result: (-result[0], result[1]))
    return [word for _, _, word in scored[:limit]]


def generate_quiz(words: Sequence[Word], count: int = 3) -> list[dict[str, Any]]:
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 5:
        raise ValueError("count must be an integer between 1 and 5")

    eligible: list[dict[str, Any]] = []
    seen_words: set[str] = set()
    for word in words:
        name = str(word.get("word", "")).strip()
        definition = str(word.get("definition") or word.get("meaning") or "").strip()
        if name and definition and name.casefold() not in seen_words:
            eligible.append(dict(word))
            seen_words.add(name.casefold())

    if len(eligible) < count + 1:
        raise ValueError("not enough vocabulary entries to create the requested quiz")

    randomizer = random.SystemRandom()
    selected = randomizer.sample(eligible, count)
    questions: list[dict[str, Any]] = []

    for answer in selected:
        answer_word = str(answer["word"])
        distractors = [
            word
            for word in eligible
            if str(word["word"]).casefold() != answer_word.casefold()
        ]
        choices = [
            answer_word,
            *(
                str(word["word"])
                for word in randomizer.sample(distractors, min(3, len(distractors)))
            ),
        ]
        randomizer.shuffle(choices)
        questions.append(
            {
                "prompt": str(answer.get("definition") or answer.get("meaning")),
                "choices": choices,
                "answer": answer_word,
            }
        )

    return questions


def _extract_term(message: str) -> str:
    patterns = (
        r"^(?:define|definition of|meaning of|explain|tell me about)\s+(?:the word\s+)?(.+?)\s*[?.!]*$",
        r"^what\s+does\s+(.+?)\s+mean\s*[?.!]*$",
        r"^what\s+is\s+(?:the word\s+)?(.+?)\s*[?.!]*$",
    )
    normalized_message = message.strip()

    for pattern in patterns:
        match = re.match(pattern, normalized_message, re.IGNORECASE)
        if match:
            return re.sub(r"\s+(?:mean|means)$", "", match.group(1).strip(), flags=re.IGNORECASE)
    return normalized_message


def _format_word(word: Word) -> str:
    name = str(word.get("word", ""))
    part_of_speech = str(word.get("part_of_speech") or word.get("parts_of_speech") or "")
    definition = str(word.get("definition") or word.get("meaning") or "No definition available.")
    lines = [f"{name}{f' ({part_of_speech})' if part_of_speech else ''}: {definition}"]

    meaning = str(word.get("meaning", "")).strip()
    if meaning and meaning != definition:
        lines.append(f"Meaning: {meaning}")
    synonyms = word.get("synonyms", [])
    if isinstance(synonyms, list) and synonyms:
        lines.append(f"Synonyms: {', '.join(str(item) for item in synonyms)}")
    example = str(word.get("example", "")).strip()
    if example:
        lines.append(f"Example: {example}")
    return "\n".join(lines)


def orchestrate_chat(message: str, words: Sequence[Word]) -> dict[str, Any]:
    normalized_message = message.strip()
    if not normalized_message:
        raise ValueError("message must not be empty")

    if re.search(r"\bquiz\b|\btest me\b", normalized_message, re.IGNORECASE):
        questions = generate_quiz(words)
        lines = ["Quick vocabulary quiz:"]
        answer_key: list[str] = []
        for index, question in enumerate(questions, start=1):
            choices = question["choices"]
            lines.append(
                f"{index}. {question['prompt']}\n"
                + "\n".join(
                    f"   {label}. {choice}"
                    for label, choice in zip("ABCD", choices)
                )
            )
            answer_key.append(f"{index}. {question['answer']}")
        lines.append("Answer key: " + "; ".join(answer_key))
        return {
            "response": "\n".join(lines),
            "mode": "local",
            "tools": ["generate_quiz"],
        }

    term = _extract_term(normalized_message)
    word = get_vocabulary_word(words, term)
    if word is not None:
        return {
            "response": _format_word(word),
            "mode": "local",
            "tools": ["get_vocabulary_word"],
        }

    matches = search_vocabulary(words, term, limit=3)
    if not matches:
        response = (
            f"I couldn't find a vocabulary entry for “{term}”. "
            "Try another word, or ask me to quiz you."
        )
    else:
        response = f"I couldn't find an exact entry for “{term}”. Closest matches:\n\n"
        response += "\n\n".join(_format_word(match) for match in matches)

    return {
        "response": response,
        "mode": "local",
        "tools": ["search_vocabulary"],
    }
