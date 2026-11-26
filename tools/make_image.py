#!/usr/bin/env python3
"""Draw a classic newspaper front page for 25 November 2026.

Everything on the page -- masthead, headlines, summaries, rules -- is
drawn in code with PIL. No photos, no external images, no web fetches.
Run:  python3 tools/make_image.py
Writes: entry.png next to this script's parent directory (the entry root).
"""

import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRY_DIR = os.path.dirname(HERE)
OUT_PATH = os.path.join(ENTRY_DIR, "entry.png")

CANVAS_W = 1024
CANVAS_H = 1024
MARGIN = 40
CONTENT_W = CANVAS_W - 2 * MARGIN

PAPER = (250, 246, 236)      # warm newsprint
INK = (18, 18, 18)           # near-black ink
ACCENT = (139, 0, 0)         # dark red, used only for kickers
RULE_GREY = (120, 115, 100)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = current + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_centered(draw, y, text, fnt, fill=INK):
    width = draw.textlength(text, font=fnt)
    draw.text(((CANVAS_W - width) / 2, y), text, font=fnt, fill=fill)
    return y + fnt.size


def draw_rule(draw, y, thickness=1, x0=None, x1=None, fill=INK):
    x0 = MARGIN if x0 is None else x0
    x1 = CANVAS_W - MARGIN if x1 is None else x1
    draw.rectangle([x0, y, x1, y + thickness - 1], fill=fill)


def draw_story(draw, x, y, width, kicker, headline, summary,
               head_size=28, sum_size=19):
    """One boxed story: small-caps kicker, bold headline, short summary."""
    kick_font = font(SANS_BOLD, 17)
    head_font = font(SERIF_BOLD, head_size)
    sum_font = font(SERIF, sum_size)

    draw.text((x, y), kicker, font=kick_font, fill=ACCENT)
    y += 24
    for line in wrap_text(draw, headline, head_font, width):
        draw.text((x, y), line, font=head_font, fill=INK)
        y += head_size + 6
    y += 2
    for line in wrap_text(draw, summary, sum_font, width):
        draw.text((x, y), line, font=sum_font, fill=INK)
        y += sum_size + 6
    return y


def build_page():
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), PAPER)
    draw = ImageDraw.Draw(img)

    # --- top meta line -------------------------------------------------
    meta_font = font(SANS, 16)
    draw.text((MARGIN, 24), "WORLD EDITION", font=meta_font, fill=INK)
    right_meta = "No. 329  •  SIX STORIES"
    rw = draw.textlength(right_meta, font=meta_font)
    draw.text((CANVAS_W - MARGIN - rw, 24), right_meta,
              font=meta_font, fill=INK)
    draw_rule(draw, 48, 1)

    # --- masthead ------------------------------------------------------
    mast_font = font(SERIF_BOLD, 78)
    draw_centered(draw, 56, "THE WORLD TODAY", mast_font)
    date_font = font(SERIF_BOLD, 30)
    draw_centered(draw, 152, "Wednesday, 25 November 2026", date_font)
    note_font = font(SANS, 16)
    draw_centered(draw, 190,
                  "ALL STORIES BELOW WERE REPORTED ON THIS DAY",
                  note_font, fill=RULE_GREY)
    draw_rule(draw, 216, 4)
    draw_rule(draw, 224, 1)

    # --- lead story ----------------------------------------------------
    kick_font = font(SANS_BOLD, 20)
    draw.text((MARGIN, 238), "MIDDLE EAST  —  LEAD STORY",
              font=kick_font, fill=ACCENT)
    lead_font = font(SERIF_BOLD, 56)
    lead_head = "TWO TANKERS HIT MINES IN THE STRAIT OF HORMUZ"
    y = 264
    for line in wrap_text(draw, lead_head, lead_font, CONTENT_W):
        draw.text((MARGIN, y), line, font=lead_font, fill=INK)
        y += 56 + 8
    y += 4
    lead_sum = (
        "Iran\u2019s Revolutionary Guard said two oil tankers struck naval "
        "mines early on Wednesday, exploded and caught fire on what Tehran "
        "called an unauthorised route. Brent crude rose to $91\u2013$92 a "
        "barrel as fears grew over the world\u2019s busiest oil chokepoint."
    )
    sum_font = font(SERIF, 24)
    for line in wrap_text(draw, lead_sum, sum_font, CONTENT_W):
        draw.text((MARGIN, y), line, font=sum_font, fill=INK)
        y += 24 + 7
    draw_rule(draw, 518, 2)

    # --- four stories in a 2 x 2 grid ----------------------------------
    col_w = (CONTENT_W - 40) // 2
    left_x = MARGIN
    right_x = MARGIN + col_w + 40
    # faint vertical divider between the columns
    draw.rectangle([CANVAS_W // 2 - 1, 532, CANVAS_W // 2, 880],
                   fill=(200, 194, 178))

    stories = [
        ("YEMEN  —  SAUDI ARABIA",
         "HOUTHIS STRIKE SAUDI REFINERY AT RAS TANURA",
         "Yemen\u2019s Houthis said they attacked Saudi Arabia\u2019s Ras "
         "Tanura refinery, causing fires, a day after a Riyadh strike "
         "injured 11."),
        ("UNITED STATES  —  TECHNOLOGY",
         "HUAWEI CONVICTED IN U.S. TRADE-SECRETS TRIAL",
         "A federal jury found the Chinese tech giant guilty of conspiracy "
         "to steal trade secrets and bank fraud, but not of racketeering."),
        ("UNITED STATES  —  ECONOMY",
         "U.S. PLANS NEW TARIFFS; MARKETS SLIDE",
         "Washington proposed fresh tariffs, including an extra 20% on "
         "imports from China. The Nasdaq fell 2% on Wednesday."),
        ("CHINA  —  SPACE",
         "FIRST FOREIGN ASTRONAUT AT TIANGONG",
         "China\u2019s Shenzhou-24 docked with Tiangong carrying Pakistani "
         "astronaut Muhammad Zeeshan Ali, the first foreign visitor."),
    ]
    draw_story(draw, left_x, 532, col_w, *stories[0])
    draw_story(draw, right_x, 532, col_w, *stories[1])
    draw_story(draw, left_x, 710, col_w, *stories[2])
    draw_story(draw, right_x, 710, col_w, *stories[3])
    draw_rule(draw, 888, 2)

    # --- sixth story: full-width strip at the foot ----------------------
    draw.text((MARGIN, 902), "PACIFIC  —  SECURITY",
              font=kick_font, fill=ACCENT)
    foot_head_font = font(SERIF_BOLD, 27)
    draw.text((MARGIN, 928),
              "SOLOMON ISLANDS SIGNS PACT WITH AUSTRALIA",
              font=foot_head_font, fill=INK)
    foot_sum_font = font(SERIF_ITALIC, 20)
    draw.text((MARGIN, 958),
              "The treaty would bar a foreign military or security base on "
              "Solomon Islands.",
              font=foot_sum_font, fill=INK)

    # --- footer ---------------------------------------------------------
    draw_rule(draw, 990, 1)
    foot_font = font(SANS, 14)
    footer = ("Sources: Reuters  •  Just Security  •  Xinhua  •  Aviation "
              "Week  —  All six stories reported on 25 November 2026.")
    draw_centered(draw, 998, footer, foot_font, fill=RULE_GREY)

    img.save(OUT_PATH, "PNG", optimize=True)
    return OUT_PATH


if __name__ == "__main__":
    path = build_page()
    size = os.path.getsize(path)
    with Image.open(path) as check:
        print(f"Wrote {path}: {check.size[0]}x{check.size[1]}, "
              f"{size} bytes")
