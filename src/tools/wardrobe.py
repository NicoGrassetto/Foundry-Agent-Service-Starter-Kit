"""Wardrobe query tool – searches the user's clothing inventory."""

import json

WARDROBE_DB = [
    {"id": 1, "type": "top", "color": "white", "style": "casual", "name": "White cotton t-shirt"},
    {"id": 2, "type": "top", "color": "blue", "style": "formal", "name": "Navy dress shirt"},
    {"id": 3, "type": "top", "color": "black", "style": "casual", "name": "Black hoodie"},
    {"id": 4, "type": "bottom", "color": "blue", "style": "casual", "name": "Classic blue jeans"},
    {"id": 5, "type": "bottom", "color": "black", "style": "formal", "name": "Black chinos"},
    {"id": 6, "type": "bottom", "color": "beige", "style": "casual", "name": "Beige cargo shorts"},
    {"id": 7, "type": "outerwear", "color": "green", "style": "casual", "name": "Olive bomber jacket"},
    {"id": 8, "type": "outerwear", "color": "black", "style": "formal", "name": "Black blazer"},
    {"id": 9, "type": "shoes", "color": "white", "style": "casual", "name": "White sneakers"},
    {"id": 10, "type": "shoes", "color": "brown", "style": "formal", "name": "Brown leather loafers"},
    {"id": 11, "type": "accessory", "color": "silver", "style": "formal", "name": "Silver watch"},
    {"id": 12, "type": "accessory", "color": "black", "style": "casual", "name": "Black baseball cap"},
]


def query_wardrobe(
    clothing_type: str = "",
    style: str = "",
    color: str = "",
) -> str:
    """Query the user's wardrobe and return matching items.

    :param clothing_type: Filter by type (top, bottom, outerwear, shoes, accessory). Empty for all.
    :param style: Filter by style (casual, formal). Empty for all.
    :param color: Filter by color. Empty for all.
    :return: JSON array of matching wardrobe items.
    """
    results = WARDROBE_DB
    if clothing_type:
        results = [i for i in results if i["type"] == clothing_type.lower()]
    if style:
        results = [i for i in results if i["style"] == style.lower()]
    if color:
        results = [i for i in results if i["color"] == color.lower()]
    return json.dumps(results, indent=2)
