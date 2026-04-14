from extractors.email_extractor import EmailExtractor


def test_extract_email_returns_first_match() -> None:
    extractor = EmailExtractor()
    text = "Reach me at first@example.com or backup@example.org"

    assert extractor.extract(text) == "first@example.com"


def test_extract_email_returns_none_when_missing() -> None:
    extractor = EmailExtractor()

    assert extractor.extract("No contact info here") is None
