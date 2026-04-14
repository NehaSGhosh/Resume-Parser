import pytest

from core.resume_extractor import ResumeExtractor


class StubExtractor:
    def __init__(self, value):
        self.value = value

    def extract(self, _text):
        return self.value


def test_resume_extractor_requires_all_fields() -> None:
    with pytest.raises(ValueError, match="Missing required extractors"):
        ResumeExtractor(
            {
                "name": StubExtractor("Jane Doe"),
                "email": StubExtractor("jane@example.com"),
            }
        )


def test_resume_extractor_builds_resume_data() -> None:
    extractor = ResumeExtractor(
        {
            "name": StubExtractor("Jane Doe"),
            "email": StubExtractor("jane@example.com"),
            "skills": StubExtractor(["Python", "SQL"]),
        }
    )

    result = extractor.extract("resume text")

    assert result.name == "Jane Doe"
    assert result.email == "jane@example.com"
    assert result.skills == ["Python", "SQL"]
