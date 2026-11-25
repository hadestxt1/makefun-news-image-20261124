"""Draw the front page for Tuesday 24 November 2026 and write entry.png.

A newspaper front page summing up the day's world news, drawn entirely
with Pillow shapes and text: no external images, no network, no clock,
no randomness. Two runs therefore produce byte-identical PNGs.

Layout (1024 x 1024):
  masthead, lead story (Qatar mediation in the US-Iran war), three mid
  stories (COP31 aftermath, Zaporizhzhia, Gaza), three short stories
  (South Korea AI cheating, Nvidia, Trump), and a ticker of the rest.
"""

import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT_NAME = "entry.png"

PAPER = (247, 243, 232)
INK = (18, 18, 18)
RED = (178, 34, 28)
DARKRED = (140, 22, 18)
BLUE = (28, 68, 128)
SKY = (176, 205, 228)
SEA = (46, 98, 150)
GREY = (90, 90, 88)
ORANGE = (224, 110, 30)
FLAME = (240, 160, 40)
GREEN = (46, 110, 62)
GOLD = (196, 150, 44)
MAROON = (138, 21, 56)
DUSK = (222, 178, 140)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def wrap(draw, text, fnt, width):
    """Wrap text to fit pixel width; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, width, fill=INK, leading=1.28):
    """Draw wrapped text; returns y below the last line."""
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += int(fnt.size * leading)
    return y


def headline(draw, x, y, text, fnt, width, fill=INK, leading=1.08):
    return para(draw, x, y, text, fnt, width, fill=fill, leading=leading)


def fit_headline(draw, text, width, start=52, floor=34):
    """Largest serif-bold size that fits the text on one line."""
    size = start
    while size > floor:
        fnt = font(SERIF_B, size)
        if draw.textlength(text, font=fnt) <= width:
            return fnt
        size -= 2
    return font(SERIF_B, floor)


def rule(draw, x0, y, x1, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def kicker(draw, x, y, text, fill=RED):
    f = font(SANS_B, 15)
    draw.text((x, y), text, font=f, fill=fill)
    return y + 21


def smoke(draw, x, y, r, fill=(150, 150, 148)):
    for dx, dy, rr in ((0, 0, r), (r, -r // 2, r * 3 // 4),
                       (-r, -r // 2, r * 2 // 3), (r // 2, -r, r // 2)):
        draw.ellipse([x + dx - rr, y + dy - rr, x + dx + rr, y + dy + rr],
                     fill=fill)


def burst(draw, cx, cy, r, fill=ORANGE):
    """Starburst: radiating spikes with a hot centre."""
    for ang in range(0, 360, 30):
        ex = cx + int(r * math.cos(math.radians(ang)))
        ey = cy + int(r * math.sin(math.radians(ang)))
        draw.line([(cx, cy), (ex, ey)], fill=fill, width=5)
    draw.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2],
                 fill=FLAME)


def stamp_overlay(cx, cy, text="STALLED"):
    """Red rubber stamp, rotated -12 degrees (deterministic)."""
    layer = Image.new("RGBA", (300, 110), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle([6, 6, 294, 104], outline=RED, width=6)
    d.text((150, 55), text, font=font(SANS_B, 52), fill=RED, anchor="mm")
    layer = layer.rotate(12, expand=True, resample=Image.BICUBIC)
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    base.alpha_composite(layer, (cx - layer.width // 2,
                                cy - layer.height // 2))
    return base


# ---------------------------------------------------------------- lead scene
def lead_scene(draw, x, y, w, h):
    """White House talks above, Hormuz blockade below."""
    draw.rectangle([x, y, x + w, y + h], fill=SKY)
    # hazy sun, upper right
    draw.ellipse([x + w - 120, y + 10, x + w - 40, y + 90],
                 fill=(240, 214, 130))
    # White House: main block, pediment, columns
    hx, hy, hw, hh = x + 40, y + h - 118, 420, 96
    draw.rectangle([hx, hy, hx + hw, hy + hh], fill=(238, 236, 228))
    draw.polygon([(hx + 60, hy), (hx + hw // 2, hy - 34),
                  (hx + hw - 60, hy)], fill=(238, 236, 228))
    draw.ellipse([hx + hw // 2 - 14, hy - 30, hx + hw // 2 + 14, hy - 2],
                 fill=(210, 208, 198))
    for i in range(5):
        cx = hx + 40 + i * 80
        draw.rectangle([cx, hy + 12, cx + 18, hy + hh], fill=(250, 248, 240))
    draw.rectangle([hx, hy + 8, hx + hw, hy + 14], fill=(200, 198, 188))
    # flag poles: striped flag left, maroon flag right
    for fx, cols in ((hx + hw + 60, (RED, (240, 240, 240))),
                     (hx + hw + 130, (MAROON, (240, 240, 240)))):
        draw.line([(fx, y + h - 170), (fx, y + h - 22)], fill=INK, width=3)
        for s in range(4):
            draw.polygon([(fx, y + h - 170 + s * 11),
                          (fx + 40, y + h - 164 + s * 11),
                          (fx, y + h - 159 + s * 11)], fill=cols[s % 2])
    # negotiating table with two seated figures, right
    tx, ty = x + w - 300, y + h - 96
    draw.rectangle([tx, ty, tx + 240, ty + 12], fill=(120, 84, 50))
    draw.rectangle([tx + 10, ty + 12, tx + 22, ty + 44], fill=(90, 64, 40))
    draw.rectangle([tx + 208, ty + 12, tx + 220, ty + 44], fill=(90, 64, 40))
    draw.rectangle([tx + 30, ty - 34, tx + 70, ty], fill=(60, 90, 140))
    draw.ellipse([tx + 40, ty - 58, tx + 62, ty - 36], fill=(220, 190, 160))
    draw.rectangle([tx + 170, ty - 34, tx + 210, ty], fill=(140, 60, 60))
    draw.ellipse([tx + 180, ty - 58, tx + 202, ty - 36], fill=(200, 170, 140))
    # Hormuz sea strip along the bottom, with tanker and mines
    sy = y + h - 46
    draw.rectangle([x, sy, x + w, y + h], fill=SEA)
    draw.polygon([(x + 60, sy + 26), (x + 260, sy + 26),
                  (x + 240, sy + 44), (x + 80, sy + 44)], fill=(40, 40, 44))
    draw.rectangle([x + 200, sy + 6, x + 240, sy + 26], fill=(200, 200, 200))
    draw.rectangle([x + 90, sy + 10, x + 130, sy + 26], fill=(120, 40, 36))
    for mx in (x + 330, x + 420, x + 500):
        draw.ellipse([mx - 8, sy + 18, mx + 8, sy + 34], fill=INK)
        for ang in range(0, 360, 45):
            ex = mx + int(13 * math.cos(math.radians(ang)))
            ey = sy + 26 + int(13 * math.sin(math.radians(ang)))
            draw.line([(mx, sy + 26), (ex, ey)], fill=INK, width=2)


# ---------------------------------------------------------------- mid scenes
def cop_scene(draw, x, y, w, h):
    """Empty chairs at the climate table, EU flag, oil derrick."""
    draw.rectangle([x, y, x + w, y + h], fill=(216, 222, 228))
    # EU flag, upper left
    draw.rectangle([x + 14, y + 10, x + 94, y + 62], fill=BLUE)
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        sx = x + 54 + int(20 * math.cos(ang))
        sy = y + 36 + int(20 * math.sin(ang))
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=GOLD)
    # oil derrick silhouette, right (behind the table)
    dx = x + w - 60
    draw.polygon([(dx, y + h - 26), (dx + 44, y + h - 26),
                  (dx + 32, y + 8), (dx + 12, y + 8)], fill=(52, 52, 52))
    smoke(draw, dx + 22, y + 6, 7, fill=(110, 110, 108))
    # long table with empty chairs
    draw.rectangle([x + 110, y + h - 40, x + w - 14, y + h - 26],
                   fill=(120, 84, 50))
    for i in range(4):
        cx = x + 126 + i * 42
        draw.rectangle([cx, y + h - 62, cx + 26, y + h - 40],
                       fill=(90, 64, 40))
    # gavel, upper right
    draw.line([(x + w - 60, y + 12), (x + w - 30, y + 40)],
              fill=(90, 64, 40), width=5)
    draw.rectangle([x + w - 66, y + 6, x + w - 40, y + 20], fill=(90, 64, 40))


def zap_scene(draw, x, y, w, h):
    """Damaged apartment block at dusk, drone overhead."""
    draw.rectangle([x, y, x + w, y + h], fill=DUSK)
    draw.rectangle([x + 30, y + 12, x + w - 30, y + h], fill=(120, 110, 96))
    for r in range(2):
        for c in range(5):
            wx = x + 46 + c * 42
            wy = y + 22 + r * 24
            if r == 0 and c >= 3:
                continue  # blasted-out corner
            draw.rectangle([wx, wy, wx + 26, wy + 16], fill=(240, 220, 160))
    draw.polygon([(x + w - 30, y + 12), (x + w - 30, y + 46),
                  (x + w - 92, y + 12)], fill=(70, 64, 56))
    smoke(draw, x + w - 56, y + 8, 10)
    # drone
    draw.ellipse([x + 16, y + 8, x + 28, y + 20], fill=INK)
    draw.line([(x + 8, y + 14), (x + 36, y + 14)], fill=INK, width=2)
    # rubble
    draw.polygon([(x + w - 110, y + h), (x + w - 30, y + h),
                  (x + w - 60, y + h - 22)], fill=(90, 84, 76))


def gaza_scene(draw, x, y, w, h):
    """City skyline under a strike burst and smoke columns."""
    draw.rectangle([x, y, x + w, y + h], fill=(214, 204, 186))
    heights = (34, 52, 44, 62, 40, 56)
    bx = x + 12
    for hh in heights:
        bw = (w - 24) // 6
        draw.rectangle([bx, y + h - hh, bx + bw - 6, y + h],
                       fill=(96, 90, 82))
        bx += bw
    burst(draw, x + w - 70, y + 26, 16)
    smoke(draw, x + 60, y + 14, 10)
    smoke(draw, x + 150, y + 8, 8)


# ---------------------------------------------------------------- page build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    m = 28  # margin

    # masthead
    draw.text((W // 2, 20), "THE WORLD IN ONE PICTURE",
              font=font(SERIF_B, 58), fill=INK, anchor="ma")
    rule(draw, m, 92, W - m, 3)
    f_date = font(SANS, 18)
    draw.text((m, 100), "TUESDAY 24 NOVEMBER 2026", font=f_date, fill=INK)
    right = "PRICE: ONE PICTURE  •  No. 328"
    draw.text((W - m, 100), right, font=f_date, fill=INK, anchor="ra")
    rule(draw, m, 128, W - m, 2)

    # ---- lead: Qatar mediation, US-Iran war
    lx, ly, lw = m, 140, W - 2 * m
    draw.rectangle([lx, ly, lx + lw, ly + 400], outline=INK, width=2)
    y = ly + 12
    y = kicker(draw, lx + 16, y, "LEAD  •  US-IRAN WAR  •  WASHINGTON")
    y = headline(draw, lx + 16, y, "QATAR RACES TO REVIVE IRAN TALKS",
                 fit_headline(draw, "QATAR RACES TO REVIVE IRAN TALKS",
                              lw - 32),
                 lw - 32, fill=DARKRED)
    y = para(draw, lx + 16, y + 4,
             "Vance and Rubio meet Qatar's prime minister in Washington as "
             "Doha pushes to revive stalled talks — Trump says America "
             "needs no deal, the US naval blockade holds in the Strait of "
             "Hormuz, and mediators offer sanctions relief for open shipping.",
             font(SANS, 20), lw - 32)
    scene_y = y + 10
    lead_scene(draw, lx + 16, scene_y, lw - 32, ly + 400 - 12 - scene_y - 34)
    cap_y = ly + 400 - 30
    draw.text((lx + 16, cap_y),
              "The White House talks: Qatar's Sheikh Mohammed meets Vance "
              "and Rubio as the Hormuz blockade grinds on.",
              font=font(SANS, 15), fill=GREY)
    img.paste(Image.alpha_composite(
        img.convert("RGBA"),
        stamp_overlay(lx + lw - 150, ly + 250, "STALLED")).convert("RGB"),
        (0, 0))

    # ---- three mid stories
    mid_y, mid_h = 556, 244
    cols = [(m, 316), (m + 328, 316), (m + 656, 316)]
    mid = [
        ("CLIMATE  •  BRUSSELS / ANTALYA",
         "EU vows to fix 'hijacked' climate talks",
         "After COP31 ends with no deal — the first since 2009 — the EU "
         "will ask the UN to overhaul consensus rules. 'The process is "
         "being hijacked by a small minority,' says climate chief Hoekstra.",
         cop_scene),
        ("UKRAINE  •  ZAPORIZHZHIA",
         "Russian strike kills two in Zaporizhzhia",
         "An overnight attack hits a block of flats: two dead, 40 wounded, "
         "four of them children. Kyiv confirms it struck a Russian ship in "
         "the Gulf of Finland.", zap_scene),
        ("GAZA",
         "Israel kills Hamas security chief in Gaza",
         "Airstrikes kill Naeem Abu Nahel and six others, including two "
         "police officers; a day earlier three were killed, among them a "
         "UN aid worker.", gaza_scene),
    ]
    for (cx, cw), (kick, head, body, scene) in zip(cols, mid):
        draw.rectangle([cx, mid_y, cx + cw, mid_y + mid_h], outline=INK,
                       width=2)
        y = mid_y + 10
        y = kicker(draw, cx + 12, y, kick)
        y = headline(draw, cx + 12, y, head, font(SERIF_B, 22), cw - 24)
        scene(draw, cx + 12, y + 4, cw - 24, 70)
        para(draw, cx + 12, y + 80, body, font(SANS, 13), cw - 24,
             leading=1.25)

    # ---- three short stories
    short_y, short_h = 812, 146
    shorts = [
        ("SOUTH KOREA  •  SEOUL",
         "Seoul offers $375,000 to catch AI exam cheats",
         "Rewards of up to $375,000 for tips on AI cheating in the college "
         "exam, days after the education minister quit."),
        ("TECH  •  NVIDIA",
         "Nvidia reinstates Jensen Huang as CEO",
         "Less than two weeks after he resigned, Huang is back at the top "
         "of the chipmaker following a scandal over an affair."),
        ("USA  •  WASHINGTON",
         "Trump spares two turkeys, medals Giuliani",
         "Freedom and Feathers escape the Thanksgiving table as the "
         "president gives the Medal of Freedom to Rudy Giuliani."),
    ]
    for (cx, cw), (kick, head, body) in zip(cols, shorts):
        draw.rectangle([cx, short_y, cx + cw, short_y + short_h],
                       outline=INK, width=2)
        y = short_y + 10
        y = kicker(draw, cx + 12, y, kick)
        y = headline(draw, cx + 12, y, head, font(SERIF_B, 21), cw - 24)
        para(draw, cx + 12, y + 2, body, font(SANS, 14), cw - 24,
             leading=1.25)

    # ---- ticker
    ty = 974
    draw.rectangle([m, ty, W - m, ty + 34], fill=INK)
    ticker = ("SARKOZY CASE TO TRIAL  •  DRC FIGHTING TRAPS EBOLA TEAMS  •  "
              "GERMANY GETS DELTA ACCESS  •  RUSSIAN JETS IN KOREA ADIZ  •  "
              "HOUTHIS 60 KM FROM ADEN")
    f_tick = font(SANS_B, 15)
    while (draw.textlength(ticker, font=f_tick) > W - 2 * m - 16
           and f_tick.size > 8):
        f_tick = font(SANS_B, f_tick.size - 1)
    while draw.textlength(ticker, font=f_tick) > W - 2 * m - 16:
        ticker = ticker[:-4].rstrip() + "..."
    tw = draw.textlength(ticker, font=f_tick)
    draw.text(((W - tw) / 2, ty + 8), ticker, font=f_tick,
              fill=(240, 240, 235))
    return img


def main():
    img = build()
    out = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out.mkdir(parents=True, exist_ok=True)
    dest = out / OUT_NAME
    img.save(dest, format="PNG", optimize=True)
    print(f"wrote {dest} ({dest.stat().st_size} bytes, "
          f"{img.width}x{img.height})")


if __name__ == "__main__":
    main()
