from extractors.name_extractor import NameExtractor


def test_name_extractor_fallback_without_model(monkeypatch) -> None:
    # Force model load failure so fallback path is exercised.
    monkeypatch.setattr("extractors.name_extractor.spacy.load", lambda _: (_ for _ in ()).throw(OSError()))

    extractor = NameExtractor()
    text = "Jane Doe\nSenior Engineer\njane@example.com"

    assert extractor.extract(text) == "Jane Doe"
