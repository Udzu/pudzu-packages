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
    _, y = ImageDraw.text_size(text, sans(16), **params)
    assert y == height


@pytest.mark.parametrize(
    "text,params,width",
    [
        [" ", {}, 4],
        ["a", {}, 9],
        ["A", {}, 12],
    ],
)
def test_text_size_width(text, params, width):
    x, _ = ImageDraw.text_size(text, sans(16), **params)
    assert x == width
