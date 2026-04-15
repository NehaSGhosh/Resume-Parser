from types import SimpleNamespace

import pytest

from extractors.name_extractor import NameExtractor


def test_name_extractor_fallback_when_no_api_key(monkeypatch):
    # Remove API key so fallback is triggered
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    extractor = NameExtractor()
    text = "Jane Doe\nSenior Engineer\njane@example.com"

    result = extractor.extract(text)

    assert result == "Jane Doe"


def test_name_extractor_llm_success(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    mock_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content='{"name": "Jane Doe"}'
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

    # Mock OpenAI client
    monkeypatch.setattr("extractors.name_extractor.OpenAI", lambda api_key: MockClient())

    extractor = NameExtractor()
    text = "Random text"

    result = extractor.extract(text)

    assert result == "Jane Doe"


def test_name_extractor_llm_returns_invalid_fallback(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    mock_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content='{"name": "Resume"}'  # invalid name
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

    monkeypatch.setattr("extractors.name_extractor.OpenAI", lambda api_key: MockClient())

    extractor = NameExtractor()
    text = "Jane Doe\nEngineer"

    result = extractor.extract(text)

    # Should fallback
    assert result == "Jane Doe"


def test_name_extractor_llm_exception_fallback(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    class MockCompletions:
        @staticmethod
        def create(**kwargs):
            raise Exception("LLM failure")

    class MockChat:
        completions = MockCompletions()

    class MockClient:
        chat = MockChat()

    monkeypatch.setattr("extractors.name_extractor.OpenAI", lambda api_key: MockClient())

    extractor = NameExtractor()
    text = "Jane Doe\nEngineer"

    result = extractor.extract(text)

    assert result == "Jane Doe"


def test_parse_name_response_valid():
    content = '{"name": "John Smith"}'

    result = NameExtractor._parse_name_response(content)

    assert result == "John Smith"


def test_parse_name_response_invalid_json():
    content = "invalid json"

    result = NameExtractor._parse_name_response(content)

    assert result is None


def test_parse_name_response_null():
    content = '{"name": null}'

    result = NameExtractor._parse_name_response(content)

    assert result is None