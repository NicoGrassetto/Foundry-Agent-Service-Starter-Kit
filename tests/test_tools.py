"""Unit tests for wardrobe tool – no Azure credentials needed."""
import json

from src.tools.wardrobe import WARDROBE_DB, query_wardrobe


def test_returns_all_items_when_no_filters():
    results = json.loads(query_wardrobe())
    assert len(results) == len(WARDROBE_DB)


def test_filter_by_type():
    results = json.loads(query_wardrobe(clothing_type="shoes"))
    assert all(item["type"] == "shoes" for item in results)
    assert len(results) == 2


def test_filter_by_style():
    results = json.loads(query_wardrobe(style="formal"))
    assert all(item["style"] == "formal" for item in results)


def test_filter_by_color():
    results = json.loads(query_wardrobe(color="black"))
    assert all(item["color"] == "black" for item in results)


def test_combined_filters():
    results = json.loads(query_wardrobe(clothing_type="top", style="casual"))
    assert len(results) == 2  # white t-shirt + black hoodie
    assert all(item["type"] == "top" and item["style"] == "casual" for item in results)


def test_no_matches_returns_empty():
    results = json.loads(query_wardrobe(clothing_type="top", color="pink"))
    assert results == []


def test_case_insensitive():
    results = json.loads(query_wardrobe(clothing_type="TOP", style="Formal"))
    assert len(results) == 1
    assert results[0]["name"] == "Navy dress shirt"


if __name__ == "__main__":
    test_returns_all_items_when_no_filters()
    test_filter_by_type()
    test_filter_by_style()
    test_filter_by_color()
    test_combined_filters()
    test_no_matches_returns_empty()
    test_case_insensitive()
    print("All wardrobe tool tests passed!")
