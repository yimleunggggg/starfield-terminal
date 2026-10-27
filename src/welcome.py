#!/usr/bin/env python3
"""Ghostty welcome: 12 random jokes and 6 PNG constellation-inspired illustrations.

Requires only the macOS Python 3 standard library. Ghostty displays the PNGs
through the Kitty graphics protocol. Other terminals get the text-only design.
"""
import argparse
import base64
import json
import os
import random
import shutil
import sys
import textwrap
from pathlib import Path

HOME = Path.home()
VERSION = '1.1.0'
IMAGE_DIR = HOME / '.config' / 'starfield-terminal' / 'constellations'
LIBRARY = HOME / '.config' / 'starfield-terminal' / 'welcome-library.json'
TITLE_SPRITES = HOME / '.config' / 'starfield-terminal' / 'titles'
ENTRIES = [
    ('🥐', 'OH, YOU AGAIN.', "Your bugs missed you. The feeling isn't mutual.", 'some things never change.'),
    ('🍳', 'LET HER COOK.', 'What could possibly go wrong?', 'famous last words.'),
    ('🚀', 'BAD IDEAS, GREAT ENERGY.', "Let's see if the tests agree.", 'proceed with unreasonable confidence.'),
    ('☕', 'BACK FOR MORE?', 'Another day, another entirely preventable problem.', 'character development, apparently.'),
    ('✨', 'ALL SYSTEMS NOMINAL.', 'Suspicious, if you ask me.', 'trust issues, but make them technical.'),
    ('🔮', 'CHAOS LOADING.', 'Everything is under control. Allegedly.', "please don't quote me on that."),
    ('🎭', 'THE PLOT THICKENS.', 'The documentation does not.', 'a familiar tragedy.'),
    ('🐛', 'STILL HERE?', "So is that bug you said you'd fix yesterday.", 'some relationships are hard to quit.'),
    ('🪩', 'NEW TAB. WHO DIS?', 'Same laptop. Fresh delusions.', 'a clean slate, more or less.'),
    ('🔥', 'PERFECT TIMING.', 'Nothing is on fire. Yet.', 'give it a minute.'),
    ('💀', 'THE AUDACITY.', 'Starting another project before finishing the last one?', 'iconic behavior.'),
    ('🌌', 'WELCOME TO THE VOID.', 'At least the typography is nice.', 'priorities, darling.'),
]
RESET = '\033[0m'
BOLD = '\033[1m'
ITALIC = '\033[3m'
PAL = {'muted': '#919cb2', 'cyan': '#99e9f4', 'white': '#edf0f5', 'footer': '#a9b0c0'}


def color(text, name, active, *, bold=False, italic=False):
    if not active:
        return text
    rgb = PAL[name].lstrip('#')
    r, g, b = (int(rgb[i:i + 2], 16) for i in (0, 2, 4))
    prefix = f'\033[38;2;{r};{g};{b}m'
    if bold:
        prefix += BOLD
    if italic:
        prefix += ITALIC
    return prefix + text + RESET


def entries():
    if LIBRARY.is_file():
        try:
            library = json.loads(LIBRARY.read_text(encoding='utf-8'))
            if library and all(len(row) == 4 and all(isinstance(s, str) for s in row) for row in library):
                return library
        except (OSError, ValueError, TypeError):
            pass
    return ENTRIES


def kitty_supported(force=False):
    return (force or bool(os.environ.get('GHOSTTY_RESOURCES_DIR'))
            or os.environ.get('TERM_PROGRAM', '').lower() == 'ghostty'
            or 'ghostty' in os.environ.get('TERM', '').lower())


def display_png(path, columns=19, rows=7):
    """Emit Kitty Graphics Protocol PNG chunks at the CURRENT cursor position.

    Protocol: f=100 PNG, t=d direct, a=T transmit and display, c/r placement,
    m continuation; q=2 prevents control replies from appearing in the shell.
    """
    payload = base64.b64encode(path.read_bytes()).decode('ascii')
    for i in range(0, len(payload), 4096):
        last = i + 4096 >= len(payload)
        hdr = ('a=T,f=100,t=d,q=2,c=%d,r=%d,m=%d' %
               (columns, rows, 0 if last else 1)) if i == 0 else ('m=%d' % (0 if last else 1))
        sys.stdout.write('\x1b_G' + hdr + ';' + payload[i:i+4096] + '\x1b\\')
    sys.stdout.flush()


def render(entry, star_num, cols, *, ansi=True, graphics=True, force=False, settings=None):
    settings = settings or {}
    emo, heading, body, footer = entry
    image_path = IMAGE_DIR / f'celestial-{star_num:02}.png'
    # Display the real image only in Ghostty and when a side-by-side placement fits.
    beside = graphics and cols >= 84 and (sys.stdout.isatty() or force) and kitty_supported(force)
    art_cols, art_rows = 19, 7
    art_col = max(1, cols - art_cols - 4)
    text_width = max(28, min(58, art_col - 7)) if beside else max(32, min(cols - 6, 74))

    print()
    # Draw before text at the current row and restore the cursor afterwards;
    # text remains on the left, while the picture occupies 19x7 right-side cells.
    if beside and image_path.is_file():
        sys.stdout.write('\x1b7')                # DECSC: save position
        sys.stdout.write('\x1b[1B')  # move star down one row
        sys.stdout.write(f'\x1b[{art_col}G')    # CHA: right-side column
        display_png(image_path, art_cols, art_rows)
        sys.stdout.write('\x1b8')                # DECRC: restore position
        sys.stdout.flush()

    print('  ' + emo + '  ' + color(settings.get('label', 'STARFIELD / TERMINAL'), 'muted', ansi))
    print()
    # v7 EDITORIAL_HEADLINE: proportionate Inter headline; shared 2-cell indent.
    index = next((i for i, item in enumerate(entries(), 1) if item[1] == heading), None)
    sprite = TITLE_SPRITES / f'title-{index:02d}.png' if index else None
    drawn = False
    if beside and ansi and sprite is not None and sprite.is_file():
        with sprite.open('rb') as f:
            hdr = f.read(24)
        if hdr[:8] == b'\x89PNG\r\n\x1a\n' and hdr[12:16] == b'IHDR':
            width = int.from_bytes(hdr[16:20], 'big')
            height = int.from_bytes(hdr[20:24], 'big')
            title_cols = round(4.0 * width / height) if height else 0
            if 8 <= title_cols <= art_col - 6:
                sys.stdout.write('\x1b7')
                sys.stdout.write('\x1b[3G')
                display_png(sprite, title_cols, 2)
                sys.stdout.write('\x1b8')
                sys.stdout.write('\n\n')
                sys.stdout.flush()
                drawn = True
    if not drawn:
        print('  ' + color(heading, 'cyan', ansi, bold=True))
    print()
    for line in textwrap.wrap(body, width=text_width, break_long_words=False, break_on_hyphens=False):
        print('  ' + color(line, 'white', ansi))
    print()
    for line in textwrap.wrap(footer, width=text_width, break_long_words=False, break_on_hyphens=False):
        print('  ' + color(line, 'footer', ansi, italic=True))
    # Blank rows guarantee that the Starship prompt starts *below* the image.
    print('\n' * (2 if beside else 1), end='')


def read_settings():
    config = HOME / '.config' / 'starfield-terminal' / 'config.json'
    try:
        data = json.loads(config.read_text(encoding='utf-8')) if config.is_file() else {}
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def diagnose():
    """Explain whether images will render and which check decides it.

    Plain text with no escape sequences, so the output can be pasted into an
    issue as-is.
    """
    cols = shutil.get_terminal_size(fallback=(90, 24)).columns
    term_program = os.environ.get('TERM_PROGRAM', '')
    term = os.environ.get('TERM', '')
    resources = os.environ.get('GHOSTTY_RESOURCES_DIR', '')
    tty = sys.stdout.isatty()
    no_color = 'NO_COLOR' in os.environ
    ghostty = kitty_supported()
    wide = cols >= 84
    binaries = sorted(IMAGE_DIR.glob('*.png')) if IMAGE_DIR.is_dir() else []
    sprites = sorted(TITLE_SPRITES.glob('*.png')) if TITLE_SPRITES.is_dir() else []
    library = LIBRARY.is_file()

    def mark(ok):
        return '[ok]  ' if ok else '[FAIL]'

    print(f'Starfield Terminal {VERSION} - diagnosis')
    print()
    print(f'  script                 {Path(__file__).resolve()}')
    print(f'  TERM_PROGRAM           {term_program or "<unset>"}')
    print(f'  TERM                   {term or "<unset>"}')
    print(f'  GHOSTTY_RESOURCES_DIR  {resources or "<unset>"}')
    print(f'  columns                {cols}')
    print()
    print(f'  {mark(ghostty)}  Ghostty detected')
    print(f'  {mark(wide)}  width {cols} (images need at least 84)')
    print(f'  {mark(tty)}  stdout is a terminal')
    print(f'  {mark(not no_color)}  colour enabled')
    print(f'  {mark(len(binaries) == 6)}  constellations: {len(binaries)} of 6')
    print(f'  {mark(len(sprites) == 12)}  title sprites: {len(sprites)} of 12')
    print()

    images = ghostty and wide and tty and len(binaries) == 6
    headings = images and not no_color and len(sprites) == 12
    print(f'  constellation images   {"yes" if images else "no"}')
    print(f'  heading sprites        {"yes" if headings else "no"}')

    hints = []
    if not images:
        if not ghostty:
            hints.append('Images are Ghostty-only. Run inside Ghostty, or try --force-image elsewhere.')
        if not wide:
            hints.append(f'Widen the window to at least 84 columns (currently {cols}).')
        if not tty:
            hints.append('stdout is redirected; images need an interactive terminal.')
        if len(binaries) != 6:
            hints.append('Constellation files are missing. Re-run: bash scripts/install.sh')
    elif not headings and no_color:
        hints.append('NO_COLOR is set, so headings fall back to text. Images still draw.')
    if hints:
        print()
        for h in hints:
            print(f'  Hint: {h}')

    print()
    print(f'  greeting library       {"custom: " + str(LIBRARY) if library else "built-in (12 entries)"}')
    return 0


def main():
    parser = argparse.ArgumentParser(description='Starfield Terminal welcome')
    parser.add_argument('--version', action='version', version=f'Starfield Terminal {VERSION}')
    parser.add_argument('--diagnose', action='store_true', help='Report whether images will render, and why not')
    parser.add_argument('--gallery', action='store_true', help='Preview all six decorative constellation illustrations')
    parser.add_argument('--seed', type=int, help='Deterministic random seed for testing')
    parser.add_argument('--no-image', action='store_true', help='Text only')
    parser.add_argument('--force-image', action='store_true', help='Test Kitty images even if terminal identification is missing')
    parser.add_argument('--columns', type=int, help='Override detected terminal width for testing')
    opts = parser.parse_args()
    if opts.diagnose:
        raise SystemExit(diagnose())
    cols = opts.columns or shutil.get_terminal_size(fallback=(90, 24)).columns
    rng = random.Random(opts.seed)
    item_list = entries()
    settings = read_settings()
    ansi = sys.stdout.isatty() and 'NO_COLOR' not in os.environ
    if opts.gallery:
        for j in range(1, 7):
            i = rng.randrange(len(item_list))
            render(item_list[i], j, cols, ansi=ansi, graphics=not opts.no_image, force=opts.force_image, settings=settings)
    else:
        i = rng.randrange(len(item_list))
        render(item_list[i], rng.randint(1, 6), cols, ansi=ansi,
               graphics=not opts.no_image, force=opts.force_image, settings=settings)

if __name__ == '__main__':
    main()
