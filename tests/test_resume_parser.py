from pathlib import Path
from types import SimpleNamespace

import pytest

import resume_parser
from parsers.pdf_parser import PDFParser
from parsers.word_parser import WordParser


def test_get_parser_returns_pdf_parser():
    parser = resume_parser.get_parser("resume.pdf")
    assert isinstance(parser, PDFParser)


def test_get_parser_returns_word_parser():
    parser = resume_parser.get_parser("resume.docx")
    assert isinstance(parser, WordParser)


def test_get_parser_raises_for_unsupported_file():
    with pytest.raises(ValueError, match="Unsupported file type"):
        resume_parser.get_parser("resume.txt")


def test_format_output_returns_expected_string():
    data = {
        "name": "Jane Doe",
        "email": "jane.doe@gmail.com",
        "skills": ["Machine Learning", "Python", "LLM"],
    }

    result = resume_parser.format_output(data)

    expected = (
        '{\n'
        '\t"name": "Jane Doe",\n'
        '\t"email": "jane.doe@gmail.com",\n'
        '\t"skills": ["Machine Learning", "Python", "LLM"]\n'
        '}'
    )

    assert result == expected


def test_parse_resume_returns_dict(monkeypatch):
    mock_result = SimpleNamespace(
        name="Jane Doe",
        email="jane.doe@gmail.com",
        skills=["Python", "SQL"],
    )

    class MockFramework:
        def parse_resume(self, file_path):
            return mock_result

    monkeypatch.setattr(resume_parser, "build_framework", lambda file_path: MockFramework())

    result = resume_parser.parse_resume("sample.docx")

    assert result == {
        "name": "Jane Doe",
        "email": "jane.doe@gmail.com",
        "skills": ["Python", "SQL"],
    }


def test_build_framework_returns_framework_instance(monkeypatch):
    class MockNameExtractor:
        pass

    class MockEmailExtractor:
        pass

    class MockSkillsExtractor:
        pass

    monkeypatch.setattr(resume_parser, "NameExtractor", MockNameExtractor)
    monkeypatch.setattr(resume_parser, "EmailExtractor", MockEmailExtractor)
    monkeypatch.setattr(resume_parser, "SkillsExtractor", MockSkillsExtractor)

    framework = resume_parser.build_framework("resume.docx")

    assert isinstance(framework, resume_parser.ResumeParserFramework)
    assert isinstance(framework.parser, WordParser)
    assert isinstance(framework.extractor, resume_parser.ResumeExtractor)


def test_main_raises_file_not_found(monkeypatch):
    monkeypatch.setattr(resume_parser.argparse.ArgumentParser, "parse_args", lambda self: SimpleNamespace(file_path="missing.docx"))
    monkeypatch.setattr(Path, "exists", lambda self: False)

    with pytest.raises(FileNotFoundError, match="File not found"):
        resume_parser.main()


def test_main_calls_parse_resume(monkeypatch):
    monkeypatch.setattr(resume_parser.argparse.ArgumentParser, "parse_args", lambda self: SimpleNamespace(file_path="resume.docx"))
    monkeypatch.setattr(Path, "exists", lambda self: True)

    called = {"value": False}

    def mock_parse_resume(file_path):
        called["value"] = True
        return {
            "name": "Jane Doe",
            "email": "jane.doe@gmail.com",
            "skills": ["Python"],
        }

    monkeypatch.setattr(resume_parser, "parse_resume", mock_parse_resume)
    monkeypatch.setattr(resume_parser.logger, "debug", lambda *args, **kwargs: None)

    resume_parser.main()

    assert called["value"] is True