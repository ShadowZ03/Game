"""
Generates placeholder images and WAV sound files for the game.
Run once to create assets/. Replace files with real art/audio anytime.
"""
from PIL import Image, ImageDraw, ImageFont
import wave, struct, math, os

OUT_IMG = "assets/images"
OUT_SND = "assets/sounds"
os.makedirs(OUT_IMG, exist_ok=True)
os.makedirs(OUT_SND, exist_ok=True)

W, H = 480, 320

# ── colour palettes ──────────────────────────────────────────────────────────
SCENES = {
    "forest_edge":  {"bg": (34, 85, 34),   "fg": (20, 50, 20),   "label": "Whispering Forest"},
    "goblin_fight": {"bg": (180, 120, 60),  "fg": (100, 60, 20),  "label": "Goblin Encounter"},
    "slime_fight":  {"bg": (60, 160, 80),   "fg": (30, 100, 50),  "label": "Slime Encounter"},
    "end_scene":    {"bg": (20, 20, 60),    "fg": (10, 10, 40),   "label": "Adventure Ends"},
    # monsters
    "goblin":       {"bg": (160, 100, 40),  "fg": (80, 50, 10),   "label": "Goblin"},
    "slime":        {"bg": (80, 200, 100),  "fg": (40, 130, 60),  "label": "Wobbly Slime"},
    "wolf":         {"bg": (90, 90, 110),   "fg": (50, 50, 70),   "label": "Forest Wolf"},
}

def draw_placeholder(name, bg, fg, label):
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    # simple geometric "art" — layered rectangles + circle
    d.rectangle([0, H*2//3, W, H], fill=fg)
    d.ellipse([W//2-60, H//3-60, W//2+60, H//3+60], fill=fg, outline=(255,255,255,80), width=2)
    # grid lines for texture
    for x in range(0, W, 40):
        d.line([(x, 0), (x, H)], fill=(0,0,0,30), width=1)
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=(0,0,0,30), width=1)
    # label banner
    d.rectangle([0, H-50, W, H], fill=(0,0,0))
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    except Exception:
        font = ImageFont.load_default()
    bbox = d.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2, H - 42), label, fill=(255, 220, 80), font=font)

    path = os.path.join(OUT_IMG, f"{name}.png")
    img.save(path)
    print(f"  ✓ {path}")

print("Generating images...")
for name, cfg in SCENES.items():
    draw_placeholder(name, cfg["bg"], cfg["fg"], cfg["label"])

# ── WAV sound generator ──────────────────────────────────────────────────────
RATE = 22050

def make_wav(path, waveform, duration=0.6, volume=0.5):
    """Write a simple synthesised WAV file."""
    n = int(RATE * duration)
    with wave.open(path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        frames = []
        for i in range(n):
            t = i / RATE
            env = math.exp(-4 * t / duration)      # decay envelope
            sample = waveform(t) * env * volume
            frames.append(struct.pack('<h', int(sample * 32767)))
        wf.writeframes(b''.join(frames))

def sine(freq):
    return lambda t: math.sin(2 * math.pi * freq * t)

def square(freq):
    return lambda t: (1 if math.sin(2 * math.pi * freq * t) > 0 else -1)

def sweep(f0, f1):
    return lambda t: math.sin(2 * math.pi * (f0 + (f1-f0)*t) * t)

def chord(*freqs):
    return lambda t: sum(math.sin(2*math.pi*f*t) for f in freqs) / len(freqs)

SOUNDS = {
    # abilities
    "power_strike":  (square(180),  0.35),   # heavy thud
    "fireball":      (sweep(300,900), 0.5),  # rising whoosh
    "heal_friend":   (chord(523,659,784), 0.6),  # pleasant chord (C-E-G)
    "sneaky_stab":   (square(220),  0.25),
    "slime_splash":  (sweep(400,150), 0.4),  # descending splat
    "howl":          (sine(180),    0.8),    # low drone
    # basic combat
    "basic_attack":  (square(160),  0.2),
    "miss":          (sine(300),    0.2),
    # events
    "victory":       (chord(523,659,784,1047), 1.0),
    "level_up":      (sweep(400,1200), 0.8),
    "rest":          (chord(392,494,587), 1.2),
    "game_over":     (sweep(300,80),  1.0),
    # scenes
    "forest_edge":   (chord(220,277,330), 1.5),
    "goblin_fight":  (square(200),  0.5),
    "slime_fight":   (sine(250),    0.5),
}

print("\nGenerating sounds...")
for name, (wfn, dur) in SOUNDS.items():
    path = os.path.join(OUT_SND, f"{name}.wav")
    make_wav(path, wfn, duration=dur)
    print(f"  ✓ {path}")

print("\n✅ All assets generated.")
print("   Replace any file in assets/ with your own PNG/WAV at any time.")