import random
from typing import List
import re
import hashlib

from anki.template import TemplateRenderOutput, TemplateRenderContext
from anki.hooks import card_did_render
from aqt import mw

css = """
<style>
.tag {
    display: inline-block;
    margin: 2px;
    margin-bottom: 15px;
    padding: 5px;
    border: 1px dashed black;
    font-size: small;
}
</style>
"""

html = """<div id="tag-list">{}</div>"""


# Some snippets are adapted from https://stackoverflow.com/a/35970186


def rand_color(tag) -> List[int]:
    return rand_color_in_range(tag, 255, 0)


def rand_color_in_range(tag, upper, lower) -> List[int]:
    hash = hashlib.md5(tag.encode()).hexdigest()
    r = int(hash[:2], 16)
    g = int(hash[2:4], 16)
    b = int(hash[4:6], 16)
    
    # clamp values based on upper and lower bounds
    r = max(lower, min(upper, r))
    g = max(lower, min(upper, g))
    b = max(lower, min(upper, b))

    return [r, g, b]



def fb_from_bg(color):
    r = color[0]
    g = color[1]
    b = color[2]
    return [0, 0, 0] if (r * 0.299 + g * 0.587 + b * 0.114) > 186 else [255, 255, 255]


def pad_zero(s):
    return s.zfill(2)


def format_color(color):
    r = hex(color[0])[2:]
    g = hex(color[1])[2:]
    b = hex(color[2])[2:]
    return "#" + pad_zero(r) + pad_zero(g) + pad_zero(b)


config = mw.addonManager.getConfig(__name__)


def escape_tag(tag: str) -> str:
    return re.sub(r"[*_\\]", r"\\\g<0>", tag).replace("\\", "\\\\").replace("'", r"\'")


def taglist_str(tags: List[str]) -> str:
    elements = []
    upper = config.get("upperRGBBound")
    lower = config.get("lowerRGBBound")
    for tag in tags:
        if config.get("limitColorRange", True):
            color = rand_color_in_range(tag, upper, lower)
        else:
            color = rand_color()
        bg_color = format_color(color)
        fg_color = format_color(fb_from_bg(color))
        if config.get("noColors", False):
            styles = """style="color: grey; border: none;" """
        else:
            styles = f"""style="color: {fg_color}; background-color: {bg_color};" """
        escaped_tag = escape_tag(tag)
        tag_el = f"""<a href=# onclick="pycmd('search:&quot;tag:{escaped_tag}&quot;'); return false;" class="tag" {styles}>{tag}</a>"""
        elements.append(tag_el)

    return "\n".join(elements)


def on_card_did_render(
        output: TemplateRenderOutput, ctx: TemplateRenderContext
) -> None:
    tags = ctx.note().tags
    text = html.format(taglist_str(tags)) + css
    output.question_text = text + output.question_text
    output.answer_text = text + output.answer_text


card_did_render.append(on_card_did_render)
