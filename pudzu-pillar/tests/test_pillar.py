import pytest

from pudzu.pillar import ImageDraw, sans


@pytest.mark.parametrize(
    "text,params,height",
    [
        [" ", {}, 15],
        ["uwu", {}, 15],
        ["dud", {}, 15],
        ["dug", {}, 18],
        ["dud\ndud", {}, 15 + 15 + 4],
        ["dud\ndug", {}, 15 + 18 + 4],
        ["dug\ndud", {}, 15 + 15 + 4],
        ["dug\ndug", {}, 15 + 18 + 4],
        ["uwu", dict(beard_line=True), 18],
        ["dug\ndug", dict(spacing=10), 15 + 18 + 10],
    ],
)
def test_text_size_height(text, params, height):
    x, y = ImageDraw.text_size(text, sans(16), **params)
    assert y == height
