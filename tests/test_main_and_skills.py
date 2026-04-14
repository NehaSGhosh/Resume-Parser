from types import SimpleNamespace

import pytest

import main
from extractors.skills_extractor import SkillsExtractor


def test_get_parser_supports_pdf_and_docx() -> None:
    assert type(main.get_parser("resume.pdf")).__name__ == "PDFParser"
    assert type(main.get_parser("resume.docx")).__name__ == "WordParser"


def test_get_parser_raises_for_unsupported_extension() -> None:
    with pytest.raises(ValueError, match="Unsupported file type"):
        main.get_parser("resume.txt")


def test_parse_resume_returns_dict_shape(monkeypatch) -> None:
    fake_data = SimpleNamespace(name="Jane Doe", email="jane@example.com", skills=["Python"])

    class FakeFramework:
        def parse_resume(self, _file_path: str):
            return fake_data

    monkeypatch.setattr(main, "build_framework", lambda _file_path: FakeFramework())

    result = main.parse_resume("resume.pdf")
    assert result == {"name": "Jane Doe", "email": "jane@example.com", "skills": ["Python"]}


def test_parse_skills_response_handles_invalid_and_deduped_content() -> None:
    invalid = SkillsExtractor._parse_skills_response("not json")
    valid = SkillsExtractor._parse_skills_response(
        '{"skills": ["Python", "python", "", 12, "SQL"]}'
    )

    assert invalid == []
    assert valid == ["Python", "SQL"]
