#!/usr/bin/env python3
"""Render a cheerful 30-second Turkish children's Shorts video with Pillow + FFmpeg."""
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 720, 1280, 30
DURATION = 30

# Each scene: start, end, headline, subtitle, scene color.
SCENES = [
    (0, 4, "Renk Avı!", "Minik Bulut'la renkleri keşfet", (111, 202, 255)),
    (4, 10, "Kırmızı!", "Elma kıpkırmızı 🍎", (255, 125, 150)),
    (10, 16, "Sarı!", "Güneş ışıl ışıl ☀", (255, 199, 74)),
    (16, 22, "Mavi!", "Balık masmavi 🐟", (86, 169, 255)),
    (22, 27, "Harika!", "Kırmızı, sarı, mavi!", (164, 125, 244)),
    (27, 30, "Senin favorin?", "Yorumlarda söyle! Hoşça kal!", (92, 207, 165)),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/Library/Fonts/Arial Bold.ttf"]
        if bold else
        ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/Library/Fonts/Arial.ttf"]
    )
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


TITLE_FONT = font(68, True)
SUB_FONT = font(34, True)
SMALL_FONT = font(25, True)


def centered(draw: ImageDraw.ImageDraw, text: str, y: int, fnt, fill, stroke=0):
    box = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
    draw.text(((W - (box[2] - box[0])) / 2, y), text, font=fnt, fill=fill,
              stroke_width=stroke, stroke_fill=(45, 54, 91))


def cloud(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0, fill=(255, 255, 255)):
    r = int(55 * scale)
    draw.ellipse((cx-r*2, cy-r//2, cx, cy+r), fill=fill)
    draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=fill)
    draw.ellipse((cx, cy-r//2, cx+r*2, cy+r), fill=fill)
    draw.rounded_rectangle((cx-r*2, cy, cx+r*2, cy+r), radius=r//2, fill=fill)
    # Cute face
    eye = max(3, int(5*scale))
    draw.ellipse((cx-int(22*scale)-eye, cy+int(10*scale)-eye, cx-int(22*scale)+eye, cy+int(10*scale)+eye), fill=(60, 75, 110))
    draw.ellipse((cx+int(22*scale)-eye, cy+int(10*scale)-eye, cx+int(22*scale)+eye, cy+int(10*scale)+eye), fill=(60, 75, 110))
    draw.arc((cx-int(15*scale), cy+int(14*scale), cx+int(15*scale), cy+int(36*scale)), 5, 175, fill=(60, 75, 110), width=max(2, int(3*scale)))


def draw_scene(im: Image.Image, t: float):
    scene = next(s for s in SCENES if s[0] <= t < s[1])
    start, end, title, subtitle, color = scene
    draw = ImageDraw.Draw(im)
    # Soft sky background and playful confetti dots.
    for y in range(H):
        p = y / H
        c = tuple(int(color[i] * (1-p) + (255, 244, 224)[i] * p) for i in range(3))
        draw.line((0, y, W, y), fill=c)
    local = t - start
    bob = int(16 * math.sin(local * 3.2))
    # Floating decorative circles
    for x, y, r, c in [(75, 260, 17, (255,255,255)), (638, 340, 13, (255,255,255)), (100, 800, 12, (255,230,140)), (620, 900, 20, (255,255,255))]:
        draw.ellipse((x-r, y-r+bob, x+r, y+r+bob), fill=c)

    if start == 0:
        cloud(draw, W//2, 520+bob, 1.35)
        # rainbow arcs
        for i, c in enumerate([(255,92,92),(255,179,71),(255,225,93),(94,201,125),(80,161,255)]):
            draw.arc((150+i*9, 365+i*9, 570-i*9, 760-i*9), 190, 350, fill=c, width=13)
    elif start == 4:
        # smiling red apple with leaf
        draw.ellipse((235, 410+bob, 485, 690+bob), fill=(239, 63, 74), outline=(190, 42, 63), width=7)
        draw.ellipse((330, 395+bob, 390, 470+bob), fill=(239, 63, 74))
        draw.line((360, 420+bob, 370, 365+bob), fill=(105, 74, 46), width=13)
        draw.ellipse((365, 365+bob, 440, 405+bob), fill=(80, 190, 96))
        draw.ellipse((285, 500+bob, 300, 515+bob), fill=(255,255,255))
    elif start == 10:
        cx, cy, r = W//2, 545+bob, 130
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(255, 195, 43), outline=(255, 153, 49), width=8)
        for a in range(0, 360, 45):
            rad = math.radians(a)
            x1, y1 = cx+math.cos(rad)*155, cy+math.sin(rad)*155
            x2, y2 = cx+math.cos(rad)*205, cy+math.sin(rad)*205
            draw.line((x1,y1,x2,y2), fill=(255, 185, 48), width=15)
        draw.ellipse((cx-43,cy-20,cx-25,cy-2), fill=(80,70,80)); draw.ellipse((cx+25,cy-20,cx+43,cy-2), fill=(80,70,80))
        draw.arc((cx-35,cy-5,cx+35,cy+45), 5, 175, fill=(80,70,80), width=6)
    elif start == 16:
        # A friendly fish, facing right
        cx, cy = W//2-20, 545+bob
        draw.ellipse((cx-135,cy-85,cx+115,cy+85), fill=(58,152,244), outline=(38,110,210), width=7)
        draw.polygon([(cx+95,cy),(cx+195,cy-80),(cx+195,cy+80)], fill=(37,120,225))
        draw.ellipse((cx+55,cy-32,cx+76,cy-11), fill=(255,255,255)); draw.ellipse((cx+62,cy-27,cx+72,cy-17), fill=(48,58,86))
        draw.arc((cx+32,cy-5,cx+83,cy+39), 10, 160, fill=(255,255,255), width=5)
        for x,y,r in [(135,620,12),(170,550,8),(570,640,15)]:
            draw.ellipse((x-r,y-r-bob,x+r,y+r-bob), outline=(255,255,255), width=5)
    else:
        # Celebration: confetti and smiling cloud
        for i in range(24):
            x = (i*97 + int(t*45)) % W
            y = (i*173 + int(t*65)) % 850 + 150
            col = [(255,86,111),(255,192,66),(67,185,132),(85,146,255),(171,103,230)][i % 5]
            draw.rounded_rectangle((x,y,x+13,y+25), radius=5, fill=col)
        cloud(draw, W//2, 535+bob, 1.2)

    centered(draw, title, 900, TITLE_FONT, (255,255,255), stroke=3)
    centered(draw, subtitle, 1000, SUB_FONT, (54,65,101), stroke=0)
    # Progress bar
    draw.rounded_rectangle((72, 1160, 648, 1176), radius=8, fill=(255,255,255,160))
    draw.rounded_rectangle((72, 1160, 72+int(576*t/DURATION), 1176), radius=8, fill=(255,255,255))
    centered(draw, "Minik Bulut'un Renk Avı", 1200, SMALL_FONT, (54,65,101))


def make_music(path: Path):
    """Create a gentle, original synthesized melody (no external music assets)."""
    rate = 22050
    notes = [523.25, 659.25, 783.99, 659.25, 587.33, 698.46, 880.00, 698.46,
             523.25, 659.25, 783.99, 1046.5, 880.00, 698.46, 659.25, 523.25]
    samples = bytearray()
    count = rate * DURATION
    for n in range(count):
        t = n / rate
        note_index = int(t / 0.375) % len(notes)
        phase = t % 0.375
        freq = notes[note_index]
        attack = min(1.0, phase / 0.025)
        release = min(1.0, (0.375-phase) / 0.07)
        envelope = attack * release * (0.72 + 0.28 * math.sin(math.pi * phase / 0.375))
        # Quiet bass pulse keeps the backing soft and playful.
        bass = math.sin(2 * math.pi * (freq / 2) * t) * 0.12
        value = (math.sin(2 * math.pi * freq * t) * 0.24 + bass) * envelope
        # Short fade-in/out.
        value *= min(1.0, t/0.8, (DURATION-t)/1.2)
        samples.extend(int(max(-1, min(1, value)) * 32767).to_bytes(2, "little", signed=True))
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1); out.setsampwidth(2); out.setframerate(rate); out.writeframes(samples)


def main():
    parser = argparse.ArgumentParser(description="Create a 30-second animated kids' YouTube Short.")
    parser.add_argument("-o", "--output", default="minik-bulut-renk-avi.mp4", help="Output MP4 path")
    args = parser.parse_args()
    if shutil.which("ffmpeg") is None:
        raise SystemExit("FFmpeg is required. Install it and ensure `ffmpeg` is on PATH.")
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="minik-bulut-") as temp:
        tmp = Path(temp)
        for frame_no in range(FPS * DURATION):
            image = Image.new("RGB", (W, H))
            draw_scene(image, frame_no / FPS)
            image.save(tmp / f"frame-{frame_no:04d}.png", optimize=False)
        audio = tmp / "music.wav"
        make_music(audio)
        command = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning",
            "-framerate", str(FPS), "-i", str(tmp / "frame-%04d.png"),
            "-i", str(audio), "-t", str(DURATION),
            "-c:v", "libx264", "-preset", "medium", "-crf", "21",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", str(output),
        ]
        subprocess.run(command, check=True)
    print(f"Created: {output}")


if __name__ == "__main__":
    main()
