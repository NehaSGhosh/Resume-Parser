from types import SimpleNamespace

import pytest

from extractors.skills_extractor import SkillsExtractor


def test_init_raises_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set"):
        SkillsExtractor()


def test_extract_returns_empty_list_for_blank_text(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    class DummyClient:
        pass

    monkeypatch.setattr("extractors.skills_extractor.OpenAI", lambda api_key: DummyClient())

    extractor = SkillsExtractor()

    assert extractor.extract("") == []
    assert extractor.extract("   ") == []


def test_parse_skills_response_returns_deduped_list():
    content = '{"skills": ["Python", "SQL", "python", " Machine Learning "]}'

    result = SkillsExtractor._parse_skills_response(content)

    assert result == ["Python", "SQL", "Machine Learning"]


def test_parse_skills_response_returns_empty_list_for_invalid_json():
    content = "not valid json"

    result = SkillsExtractor._parse_skills_response(content)

    assert result == []


def test_parse_skills_response_returns_empty_list_when_skills_not_list():
    content = '{"skills": "Python"}'

    result = SkillsExtractor._parse_skills_response(content)

    assert result == []


def test_parse_skills_response_skips_non_string_values():
    content = '{"skills": ["Python", 123, null, "SQL"]}'

    result = SkillsExtractor._parse_skills_response(content)

    assert result == ["Python", "SQL"]


def test_extract_returns_parsed_skills(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    mock_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content='{"skills": ["Python", "FastAPI", "Python"]}'
                )
            )
        ]
    )

    class MockCompletions:
        @staticmethod
        def create(**kwargs):
            return mock_response

    class MockChat:
        completions = MockCompletions()

    class MockClient:
        chat = MockChat()

    monkeypatch.setattr("extractors.skills_extractor.OpenAI", lambda api_key: MockClient())

    extractor = SkillsExtractor()
    result = extractor.extract("Experienced in Python and FastAPI.")

    assert result == ["Python", "FastAPI"]


def test_extract_trims_long_input(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    captured = {"prompt": None}

    class MockCompletions:
        @staticmethod
        def create(**kwargs):
            captured["prompt"] = kwargs["messages"][1]["content"]
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content='{"skills": ["Python"]}')
                    )
                ]
            )

    class MockChat:
        completions = MockCompletions()

    class MockClient:
        chat = MockChat()

    monkeypatch.setattr("extractors.skills_extractor.OpenAI", lambda api_key: MockClient())

    extractor = SkillsExtractor(max_input_chars=10)
    extractor.extract("1234567890ABCDEFGHIJ")

    assert "1234567890" in captured["prompt"]
    assert "ABCDEFGHIJ" not in captured["prompt"]