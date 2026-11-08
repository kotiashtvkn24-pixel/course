import pytest

from app.models import ValidationError


def test_catalog_lists_all_styles(factory):
    assert [s["key"] for s in factory.catalog()] == ["warm", "formal", "funny", "short"]


@pytest.mark.parametrize("key", ["warm", "formal", "funny", "short"])
def test_every_style_mentions_the_name(factory, key):
    assert "Оксана" in factory.create(key).compose("Оксана")


def test_unknown_style(factory):
    assert not factory.has("nope")
    with pytest.raises(ValidationError):
        factory.create("nope")
