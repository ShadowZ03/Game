"""
engine/media.py
---------------
Persistent pygame window — fixed-split layout:
  ┌─────────────────────┐
  │   Scene image       │  ART_H px  (image or dark fill)
  ├─────────────────────┤
  │   Text / title      │  TEXT_ROWS_H px  (scrolls if needed)
  ├─────────────────────┤
  │   Buttons           │  sized to fit max_buttons at startup
  └─────────────────────┘
Sounds play non-blocking.  All functions silently no-op without pygame.
"""

import os

_pg     = None
_screen = None
_clock  = None
_bg     = None   # scene image scaled to (WIN_W, ART_H)

# ── Fixed layout constants ────────────────────────────────────────────────────
WIN_W       = 620
ART_H       = 220   # scene image — intentionally modest so UI has room
TEXT_ROWS_H = 140   # dedicated text panel below image
BTN_H       = 44
BTN_MARGIN  = 8
BTN_X       = 30
PANEL_PAD   = 6     # gap between sections

# Derived at init_window() time
BTN_W = WIN_W - BTN_X * 2
WIN_H = 700   # overwritten by init_window()

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
IMG_DIR    = os.path.join(ASSETS_DIR, "images")
SND_DIR    = os.path.join(ASSETS_DIR, "sounds")

# Colours
C_BG         = (15,  15,  25)
C_PANEL      = (20,  22,  38)
C_BTN        = (40,  60,  90)
C_BTN_HOV    = (60,  95, 140)
C_BTN_DIM    = (28,  32,  44)
C_BTN_BORDER = (70, 110, 160)
C_TEXT       = (225, 215, 195)
C_TEXT_DIM   = (95,  95, 105)
C_TITLE      = (255, 215,  70)
C_DIVIDER    = (40,  50,  70)


# ── init ─────────────────────────────────────────────────────────────────────

def init_window(max_buttons: int):
    """
    Open the pygame window sized to fit `max_buttons` buttons comfortably.
    Call once at game start before any rendering.
    """
    global WIN_H, BTN_W, _pg, _screen, _clock

    btn_section_h = BTN_MARGIN + max_buttons * (BTN_H + BTN_MARGIN)
    WIN_H = ART_H + PANEL_PAD + TEXT_ROWS_H + PANEL_PAD + btn_section_h + PANEL_PAD
    BTN_W = WIN_W - BTN_X * 2

    try:
        import pygame
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        _screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Adventure Game")
        _clock = pygame.time.Clock()
        _pg = pygame
    except Exception:
        pass


def _init():
    if _pg is not None:
        return True
    init_window(max_buttons=4)
    return _pg is not None


# ── Layout helpers ────────────────────────────────────────────────────────────

def _text_panel_rect():
    """Rect for the text/narration panel."""
    return _pg.Rect(BTN_X, ART_H + PANEL_PAD, BTN_W, TEXT_ROWS_H)

def _btn_area_top():
    """Y coordinate where the button stack begins."""
    return ART_H + PANEL_PAD + TEXT_ROWS_H + PANEL_PAD

def _btn_rects(count):
    rects = []
    y = _btn_area_top() + BTN_MARGIN
    for _ in range(count):
        rects.append(_pg.Rect(BTN_X, y, BTN_W, BTN_H))
        y += BTN_H + BTN_MARGIN
    return rects


# ── Drawing primitives ────────────────────────────────────────────────────────

def _font(size=20, bold=False):
    try:
        name = "DejaVuSans-Bold" if bold else "DejaVuSans"
        for p in [
            f"/usr/share/fonts/truetype/dejavu/{name}.ttf",
            f"/usr/share/fonts/truetype/liberation/LiberationSans-{'Bold' if bold else 'Regular'}.ttf",
        ]:
            if os.path.isfile(p):
                return _pg.font.Font(p, size)
        return _pg.font.SysFont("sans", size, bold=bold)
    except Exception:
        return _pg.font.SysFont(None, size)


def _draw_base():
    """Draw the scene image + dark panels (called every frame)."""
    # Clear entire window first to prevent ghost text from previous frames
    _screen.fill(C_BG)
    # Scene image or dark fill
    if _bg is not None:
        _screen.blit(_bg, (0, 0))
    else:
        _screen.fill((10, 12, 20), (0, 0, WIN_W, ART_H))

    # Text panel background
    tp = _text_panel_rect()
    _screen.fill(C_PANEL, tp)
    # Divider line under image
    _pg.draw.line(_screen, C_DIVIDER, (0, ART_H), (WIN_W, ART_H), 2)
    # Divider line under text panel
    div_y = ART_H + PANEL_PAD + TEXT_ROWS_H
    _pg.draw.line(_screen, C_DIVIDER, (BTN_X, div_y), (BTN_X + BTN_W, div_y), 1)
    # Fill button area background
    _screen.fill(C_BG, (0, div_y, WIN_W, WIN_H - div_y))


def _draw_text_panel(lines, title=None):
    """Render lines of text inside the text panel, with optional bold title."""
    tp = _text_panel_rect()
    ty = tp.y + 8

    if title:
        tf = _font(18, bold=True)
        ts = tf.render(title, True, C_TITLE)
        _screen.blit(ts, (tp.x + 10, ty))
        ty += ts.get_height() + 6
        _pg.draw.line(_screen, C_DIVIDER,
                      (tp.x + 10, ty), (tp.x + BTN_W - 10, ty), 1)
        ty += 6

    f = _font(17)
    for line in lines:
        if ty + f.get_height() > tp.bottom - 4:
            break  # clip rather than overflow
        if not line:
            ty += 7
            continue
        surf = f.render(line, True, C_TEXT)
        _screen.blit(surf, (tp.x + 10, ty))
        ty += surf.get_height() + 3


def _draw_button(rect, label, hovered=False, dimmed=False, num=None):
    colour     = C_BTN_DIM if dimmed else (C_BTN_HOV if hovered else C_BTN)
    txt_colour = C_TEXT_DIM if dimmed else C_TEXT

    _pg.draw.rect(_screen, colour, rect, border_radius=7)
    if not dimmed:
        _pg.draw.rect(_screen, C_BTN_BORDER, rect, width=2, border_radius=7)

    x_off = 12
    if num is not None:
        badge = _pg.Rect(rect.x + 8, rect.y + rect.h // 2 - 12, 24, 24)
        _pg.draw.rect(_screen, C_BTN_BORDER, badge, border_radius=4)
        ns = _font(14, bold=True).render(str(num), True, C_TITLE)
        _screen.blit(ns, (badge.x + (24 - ns.get_width()) // 2,
                          badge.y + (24 - ns.get_height()) // 2))
        x_off = 40

    txt = _font(19).render(label, True, txt_colour)
    max_w = rect.w - x_off - 10
    if txt.get_width() > max_w:
        txt = txt.subsurface((0, 0, max_w, txt.get_height()))
    _screen.blit(txt, (rect.x + x_off, rect.y + (rect.h - txt.get_height()) // 2))


# ── Public API ────────────────────────────────────────────────────────────────

def set_scene(name: str):
    """Load a webp or png image as the persistent scene backdrop.
    Scales to fit within WIN_W x ART_H while preserving aspect ratio
    (letterbox / pillarbox — black bars fill any unused space).
    """
    global _bg
    if not _init():
        return
    for ext in ("webp", "png"):
        path = os.path.join(IMG_DIR, f"{name}.{ext}")
        if os.path.isfile(path):
            try:
                img = _pg.image.load(path).convert()
                iw, ih = img.get_size()

                # Scale to fit inside WIN_W x ART_H, preserving aspect ratio
                scale = min(WIN_W / iw, ART_H / ih)
                fit_w = int(iw * scale)
                fit_h = int(ih * scale)
                scaled = _pg.transform.scale(img, (fit_w, fit_h))

                # Composite onto a black canvas of the full art strip size
                canvas = _pg.Surface((WIN_W, ART_H))
                canvas.fill((0, 0, 0))
                x_off = (WIN_W - fit_w) // 2
                y_off = (ART_H - fit_h) // 2
                canvas.blit(scaled, (x_off, y_off))
                _bg = canvas
            except Exception:
                _bg = None
            return
    _bg = None


def show_image(name: str):
    set_scene(name)


def prompt_choices(title: str, options: list, recharging: list = None) -> int:
    """
    Show `title` in the text panel and render `options` as clickable buttons.
    Returns 0-based index.  Keyboard 1-9 also works.
    """
    if not _init():
        print(f"\n{title}")
        for i, opt in enumerate(options, 1):
            tag = " (Recharging...)" if (recharging and recharging[i-1]) else ""
            print(f"  {i}. {opt}{tag}")
        while True:
            try:
                v = int(input("> ")) - 1
                if 0 <= v < len(options):
                    return v
            except (ValueError, IndexError):
                pass

    recharging = recharging or [False] * len(options)
    rects = _btn_rects(len(options))
    mouse = (0, 0)

    while True:
        for event in _pg.event.get():
            if event.type == _pg.QUIT:
                quit_media(); raise SystemExit
            if event.type == _pg.MOUSEMOTION:
                mouse = event.pos
            if event.type == _pg.MOUSEBUTTONDOWN and event.button == 1:
                for i, r in enumerate(rects):
                    if r.collidepoint(event.pos) and not recharging[i]:
                        return i
            if event.type == _pg.KEYDOWN:
                k = event.key - _pg.K_1
                if 0 <= k < len(options) and not recharging[k]:
                    return k

        _draw_base()
        _draw_text_panel([], title=title)
        for i, (r, label) in enumerate(zip(rects, options)):
            dim = recharging[i]
            _draw_button(r, label + ("  ⟳" if dim else ""),
                         hovered=r.collidepoint(mouse) and not dim,
                         dimmed=dim, num=i + 1)
        _pg.display.flip()
        _clock.tick(30)


def prompt_yn(question: str) -> bool:
    return prompt_choices(question, ["Yes", "No"]) == 0


def show_message(lines: list, wait_label="Continue"):
    """
    Display lines of text in the text panel with a single Continue button.
    """
    if not _init():
        for line in lines:
            print(line)
        input(f"[ {wait_label} ]")
        return

    btn_rect = _btn_rects(1)[0]   # one button, positioned correctly
    mouse = (0, 0)

    while True:
        for event in _pg.event.get():
            if event.type == _pg.QUIT:
                quit_media(); raise SystemExit
            if event.type == _pg.MOUSEMOTION:
                mouse = event.pos
            if event.type == _pg.MOUSEBUTTONDOWN and event.button == 1:
                if btn_rect.collidepoint(event.pos):
                    return
            if event.type == _pg.KEYDOWN:
                return

        _draw_base()
        _draw_text_panel(lines)
        _draw_button(btn_rect, wait_label, hovered=btn_rect.collidepoint(mouse))
        _pg.display.flip()
        _clock.tick(30)


def play_sound(name: str):
    path = os.path.join(SND_DIR, f"{name}.wav")
    if not os.path.isfile(path) or not _init():
        return
    try:
        _pg.mixer.Sound(path).play()
    except Exception:
        pass


def quit_media():
    global _pg, _screen, _clock, _bg
    if _pg:
        try: _pg.quit()
        except Exception: pass
    _pg = _screen = _clock = _bg = None