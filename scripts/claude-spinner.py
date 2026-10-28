#!/usr/bin/env python3
"""Give Claude Code's native spinner verbs an emoji.

Claude Code reads `spinnerVerbs` from ~/.claude/settings.json. In `append`
mode the built-in verbs are concatenated as-is, so they can never carry an
emoji. This script therefore uses `replace`, and rebuilds the list from the
verb table inside the Claude Code you actually have installed — new native
verbs show up the next time you run it.
"""
import argparse
import json
import mmap
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ANCHOR = b'"Razzle-dazzling"'
STATE_NAME = 'spinner-install-state.json'


def unescape(word):
    word = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), word)
    return word.replace('\\"', '"').replace('\\\\', '\\')


# One emoji per built-in verb. Words missing from this table (a Claude Code
# update added them) get a stable emoji from FALLBACK_EMOJI instead.
EMOJI = {
    'Accomplishing': '✅', 'Actioning': '🎬', 'Actualizing': '🌱',
    'Architecting': '📐', 'Baking': '🥐', 'Beaming': '😊',
    "Beboppin'": '🎷', 'Befuddling': '😵‍💫', 'Billowing': '🌬️',
    'Blanching': '🥬', 'Bloviating': '🗣️', 'Boogieing': '🕺',
    'Boondoggling': '🧶', 'Booping': '👆', 'Bootstrapping': '👢',
    'Brewing': '☕', 'Bunning': '🥯', 'Burrowing': '🦔',
    'Calculating': '🧮', 'Caramelizing': '🍮', 'Cascading': '🌊',
    'Catapulting': '🏹', 'Cerebrating': '🧠', 'Channeling': '📡',
    'Choreographing': '💃', 'Churning': '🧈', 'Clauding': '🟠',
    'Coalescing': '🫧', 'Cogitating': '🤔', 'Combobulating': '🧩',
    'Composing': '🎼', 'Computing': '💻', 'Concocting': '🧪',
    'Considering': '🤨', 'Contemplating': '🗿', 'Cooking': '🍳',
    'Crafting': '🧵', 'Creating': '🎨', 'Crunching': '🔢',
    'Crystallizing': '💎', 'Cultivating': '🌾', 'Deciphering': '🔎',
    'Deliberating': '⚖️', 'Determining': '🧭', 'Dilly-dallying': '🐌',
    'Discombobulating': '😵', 'Doing': '🛠️', 'Doodling': '✏️',
    'Drizzling': '🌧️', 'Ebbing': '〰️', 'Effecting': '🪄',
    'Elucidating': '💡', 'Embellishing': '🎀', 'Enchanting': '✨',
    'Envisioning': '🔭', 'Fermenting': '🫙', 'Fiddle-faddling': '🎻',
    'Finagling': '🕵️', 'Flambéing': '🔥', 'Flibbertigibbeting': '🤪',
    'Flowing': '🏞️', 'Flummoxing': '😳', 'Fluttering': '🕊️',
    'Forging': '⚒️', 'Forming': '🧱', 'Frolicking': '🌼',
    'Frosting': '🍰', 'Gallivanting': '🚶', 'Galloping': '🐎',
    'Garnishing': '🌿', 'Generating': '⚙️', 'Gesticulating': '🙌',
    'Germinating': '🌰', 'Gitifying': '🐙', 'Grooving': '🪩',
    'Gusting': '💨', 'Harmonizing': '🎶', 'Hashing': '#️⃣',
    'Hatching': '🐣', 'Herding': '🐑', 'Honking': '🪿',
    'Hullaballooing': '📢', 'Hyperspacing': '🚀', 'Ideating': '💭',
    'Imagining': '🌈', 'Improvising': '🎭', 'Incubating': '🥚',
    'Inferring': '🔍', 'Infusing': '🫖', 'Ionizing': '⚛️',
    'Jitterbugging': '🤸', 'Julienning': '🔪', 'Kerfuffling': '🤯',
    'Kneading': '🥖', 'Leavening': '🍞', 'Levitating': '🎈',
    'Lollygagging': '🍭', 'Manifesting': '🔮', 'Marinating': '🥣',
    'Meandering': '🌀', 'Metamorphosing': '🐛', 'Misting': '💦',
    'Moonwalking': '🌙', 'Moseying': '🐢', 'Mulling': '🍵',
    'Mustering': '🛡️', 'Nebulizing': '🌌', 'Nesting': '🪺',
    'Newspapering': '📰', 'Noodling': '🍜', 'Nucleating': '🔬',
    'Onioning': '🧅', 'Orbiting': '🪐', 'Orchestrating': '🎺',
    'Osmosing': '💧', 'Perambulating': '👟', 'Percolating': '🫗',
    'Perusing': '📖', 'Philosophizing': '🦉', 'Photosynthesizing': '☀️',
    'Polishing': '🪞', 'Pollinating': '🐝', 'Pondering': '🧐',
    'Pontificating': '🎙️', 'Pouncing': '🐈', 'Precipitating': '❄️',
    'Prestidigitating': '🎩', 'Processing': '🖥️', 'Proofing': '📄',
    'Propagating': '🧬', 'Puttering': '🧰', 'Puzzling': '❓',
    'Quantumizing': '🌠', 'Razzle-dazzling': '🎪', 'Razzmatazzing': '🎆',
    'Recombobulating': '🔧', 'Reticulating': '🕸️', 'Roosting': '🐦',
    'Ruminating': '🐄', 'Sautéing': '🥘', 'Scampering': '🐿️',
    'Schlepping': '🧳', 'Scurrying': '🐁', 'Seasoning': '🧂',
    'Shenaniganing': '😈', 'Shimmying': '💫', 'Simmering': '🍲',
    'Skedaddling': '🏃', 'Sketching': '🖊️', 'Slithering': '🐍',
    'Smooshing': '🫠', 'Sock-hopping': '🧦', 'Spelunking': '🔦',
    'Spinning': '🎡', 'Sprouting': '🪴', 'Stewing': '🫕',
    'Sublimating': '🧊', 'Swirling': '🌪️', 'Swooping': '🦅',
    'Symbioting': '🍄', 'Synthesizing': '⚗️', 'Tempering': '🍫',
    'Thinking': '💭', 'Thundering': '⛈️', 'Tinkering': '🪛',
    'Tomfoolering': '🤡', 'Topsy-turvying': '🙃', 'Transfiguring': '🦄',
    'Transmogrifying': '🧟', 'Transmuting': '🔄', 'Twisting': '🍥',
    'Undulating': '🌊', 'Unfurling': '🌸', 'Unraveling': '🪡',
    'Vibing': '🎧', 'Waddling': '🐧', 'Wandering': '🗺️',
    'Warping': '🛸', 'Whatchamacalliting': '🤷', 'Whirlpooling': '🛁',
    'Whirring': '🔊', 'Whisking': '🧑‍🍳', 'Wibbling': '🫨',
    'Working': '💼', 'Wrangling': '🤠', 'Zesting': '🍋',
    'Zigzagging': '🦓',
}

# Ours, not Claude Code's. Kept because they are the words the author actually
# likes seeing; they sit after the native ones.
EXTRAS = [
    ('🎩', 'Conjuring'), ('✨', 'Sparkling'), ('💡', 'Brainstorming'),
    ('🔍', 'Exploring'), ('🔮', 'Summoning'), ('🚀', 'Launching'),
]

FALLBACK_EMOJI = ['🌠', '🎈', '🔭', '🧭', '🎲', '🪐', '🌟', '🎨', '🪁', '🧿']

# Snapshot of the built-in list from Claude Code 2.1.312, used only when the
# installed binary cannot be read (a future release, a locked-down install).
FALLBACK_VERBS = [
    'Accomplishing', 'Actioning', 'Actualizing', 'Architecting', 'Baking',
    'Beaming', "Beboppin'", 'Befuddling', 'Billowing', 'Blanching',
    'Bloviating', 'Boogieing', 'Boondoggling', 'Booping', 'Bootstrapping',
    'Brewing', 'Bunning', 'Burrowing', 'Calculating', 'Caramelizing',
    'Cascading', 'Catapulting', 'Cerebrating', 'Channeling', 'Choreographing',
    'Churning', 'Clauding', 'Coalescing', 'Cogitating', 'Combobulating',
    'Composing', 'Computing', 'Concocting', 'Considering', 'Contemplating',
    'Cooking', 'Crafting', 'Creating', 'Crunching', 'Crystallizing',
    'Cultivating', 'Deciphering', 'Deliberating', 'Determining',
    'Dilly-dallying', 'Discombobulating', 'Doing', 'Doodling', 'Drizzling',
    'Ebbing', 'Effecting', 'Elucidating', 'Embellishing', 'Enchanting',
    'Envisioning', 'Fermenting', 'Fiddle-faddling', 'Finagling',
    'Flambéing', 'Flibbertigibbeting', 'Flowing', 'Flummoxing', 'Fluttering',
    'Forging', 'Forming', 'Frolicking', 'Frosting', 'Gallivanting',
    'Galloping', 'Garnishing', 'Generating', 'Gesticulating', 'Germinating',
    'Gitifying', 'Grooving', 'Gusting', 'Harmonizing', 'Hashing', 'Hatching',
    'Herding', 'Honking', 'Hullaballooing', 'Hyperspacing', 'Ideating',
    'Imagining', 'Improvising', 'Incubating', 'Inferring', 'Infusing',
    'Ionizing', 'Jitterbugging', 'Julienning', 'Kerfuffling', 'Kneading',
    'Leavening', 'Levitating', 'Lollygagging', 'Manifesting', 'Marinating',
    'Meandering', 'Metamorphosing', 'Misting', 'Moonwalking', 'Moseying',
    'Mulling', 'Mustering', 'Nebulizing', 'Nesting', 'Newspapering',
    'Noodling', 'Nucleating', 'Onioning', 'Orbiting', 'Orchestrating',
    'Osmosing', 'Perambulating', 'Percolating', 'Perusing', 'Philosophizing',
    'Photosynthesizing', 'Polishing', 'Pollinating', 'Pondering',
    'Pontificating', 'Pouncing', 'Precipitating', 'Prestidigitating',
    'Processing', 'Proofing', 'Propagating', 'Puttering', 'Puzzling',
    'Quantumizing', 'Razzle-dazzling', 'Razzmatazzing', 'Recombobulating',
    'Reticulating', 'Roosting', 'Ruminating', 'Sautéing', 'Scampering',
    'Schlepping', 'Scurrying', 'Seasoning', 'Shenaniganing', 'Shimmying',
    'Simmering', 'Skedaddling', 'Sketching', 'Slithering', 'Smooshing',
    'Sock-hopping', 'Spelunking', 'Spinning', 'Sprouting', 'Stewing',
    'Sublimating', 'Swirling', 'Swooping', 'Symbioting', 'Synthesizing',
    'Tempering', 'Thinking', 'Thundering', 'Tinkering', 'Tomfoolering',
    'Topsy-turvying', 'Transfiguring', 'Transmogrifying', 'Transmuting',
    'Twisting', 'Undulating', 'Unfurling', 'Unraveling', 'Vibing',
    'Waddling', 'Wandering', 'Warping', 'Whatchamacalliting', 'Whirlpooling',
    'Whirring', 'Whisking', 'Wibbling', 'Working', 'Wrangling', 'Zesting',
    'Zigzagging',
]


def find_claude(explicit=None):
    path = explicit or shutil.which('claude')
    if not path:
        raise SystemExit(
            'Claude Code was not found on PATH. Install it first, or pass '
            '--claude /path/to/claude.'
        )
    return Path(os.path.realpath(path))


def candidate_binaries(found):
    """Real binaries to try, in order. npm and native installs differ by OS."""
    seen, out = set(), []

    def add(candidate):
        if not candidate:
            return
        candidate = Path(candidate)
        try:
            key = candidate.resolve()
        except OSError:
            key = candidate
        if key in seen or not candidate.is_file():
            return
        seen.add(key)
        out.append(candidate)

    add(found)
    add(Path(os.path.realpath(found)))
    for folder in (found.parent, Path(os.path.realpath(found)).parent):
        add(folder/'claude.exe')
        add(folder/'claude')
        add(folder.parent/'bin'/'claude.exe')
        add(folder.parent/'bin'/'claude')

    home = Path.home()
    add(home/'.local'/'bin'/'claude.exe')
    add(home/'.local'/'bin'/'claude')
    if os.name == 'nt':
        for base in (os.environ.get('APPDATA'), os.environ.get('LOCALAPPDATA'),
                     os.environ.get('USERPROFILE')):
            if not base:
                continue
            root = Path(base)
            add(root/'npm'/'node_modules'/'@anthropic-ai'/'claude-code'/'bin'/'claude.exe')
            add(root/'npm'/'node_modules'/'@anthropic-ai'/'claude-code-win32-x64'/'claude.exe')
            add(root/'npm'/'node_modules'/'@anthropic-ai'/'claude-code-win32-arm64'/'claude.exe')
            add(root/'Programs'/'claude'/'claude.exe')
        add(home/'.local'/'bin'/'claude.exe')
    return out


def extract_verbs(binary):
    """Return the built-in verb list embedded in a Claude Code binary."""
    try:
        with binary.open('rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                at = mm.find(ANCHOR)
                if at < 0:
                    return None
                start = mm.rfind(b'[', 0, at)
                end = mm.find(b']', at)
                if start < 0 or end < 0:
                    return None
                raw = mm[start:end + 1].decode('latin-1')
    except (OSError, ValueError):
        return None
    words = [unescape(w) for w in re.findall(r'"((?:[^"\\]|\\.)*)"', raw)]
    # The table is a long flat array of single words; anything else means the
    # binary is laid out differently than expected.
    if len(words) < 50 or any(len(w) > 40 for w in words):
        return None
    return words


def claude_version(binary):
    try:
        done = subprocess.run([str(binary), '--version'], capture_output=True,
                              text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    lines = (done.stdout or done.stderr).strip().splitlines()
    if not lines:
        return None
    match = re.search(r'\d+\.\d+\.\d+', lines[0])
    return match.group(0) if match else None


def inspect(found):
    """Return (binary, native verbs or None, version or None)."""
    for candidate in candidate_binaries(found):
        native = extract_verbs(candidate)
        if native:
            return candidate, native, claude_version(candidate)
    return found, None, None


def describe_source(binary, native, version):
    if native is not None:
        label = f'Claude Code {version}' if version else 'Claude Code'
        return (f'{len(native)} native verbs read from {label} '
                f'({binary})')
    return (f'bundled snapshot of {len(FALLBACK_VERBS)} verbs; {binary} could '
            'not be inspected, so a newer built-in list may be missing')


def emoji_for(word):
    if word in EMOJI:
        return EMOJI[word]
    return FALLBACK_EMOJI[sum(map(ord, word)) % len(FALLBACK_EMOJI)]


def build_verbs(native):
    verbs = [f'{emoji_for(word)} {word}' for word in native]
    for emoji, word in EXTRAS:
        if word not in native:
            verbs.append(f'{emoji} {word}')
    return verbs


def settings_path():
    return Path.home() / '.claude' / 'settings.json'


def state_path():
    return Path.home() / '.config' / 'starfield-terminal' / STATE_NAME


def load_json(path, default):
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return default
    except (OSError, ValueError) as exc:
        raise SystemExit(f'Cannot read {path}: {exc}')
    return value


def backup(settings):
    folder = (Path.home() / '.config' / 'starfield-terminal' / 'backups'
              / ('spinner-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f')))
    folder.mkdir(parents=True, exist_ok=False)
    if settings.exists():
        shutil.copy2(settings, folder / 'claude-settings.json')
    return folder


def cmd_install(found, dry_run):
    binary, native, version = inspect(found)
    source = describe_source(binary, native, version)
    if native is None:
        native = list(FALLBACK_VERBS)
    verbs = build_verbs(native)
    payload = {'mode': 'replace', 'verbs': verbs}
    if dry_run:
        print(json.dumps({'spinnerVerbs': payload}, ensure_ascii=False, indent=2))
        print(f'# Source: {source}', file=sys.stderr)
        return 0

    path = settings_path()
    settings = load_json(path, {})
    if not isinstance(settings, dict):
        print('Claude settings.json must be a JSON object.', file=sys.stderr)
        return 1
    old = settings.get('spinnerVerbs')
    folder = backup(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    settings['spinnerVerbs'] = payload
    path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + '\n',
                    encoding='utf-8')

    state_file = state_path()
    state = load_json(state_file, {})
    if not isinstance(state, dict):
        state = {}
    # Keep the very first original so uninstall can put it back. Re-installs
    # only refresh what we consider "ours".
    if 'had_spinner' not in state:
        state['had_spinner'] = old is not None
        state['old_spinner'] = old
    state['written'] = payload
    state['claude'] = str(binary)
    state['verb_count'] = len(verbs)
    state['native_count'] = len(native)
    state['source'] = source
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n',
                          encoding='utf-8')

    print(f'Playful spinner enabled: {len(verbs)} verbs.')
    print(f'  Source: {source}')
    print(f'  Settings: {path}')
    print(f'  Backup:   {folder}')
    print('  Restart Claude Code to see it.')
    return 0


def cmd_check(found):
    path = settings_path()
    settings = load_json(path, {})
    current = settings.get('spinnerVerbs') if isinstance(settings, dict) else None
    if not isinstance(current, dict) or current.get('mode') != 'replace':
        print('Playful spinner is not enabled (spinnerVerbs is not replace).')
        return 1
    binary, native, version = inspect(found)
    source = describe_source(binary, native, version)
    if native is None:
        native = list(FALLBACK_VERBS)
    configured = []
    for verb in current.get('verbs', []):
        word = verb.split(' ', 1)[1] if ' ' in verb else verb
        configured.append(word)
    missing = [w for w in native if w not in configured]
    extra = [w for w in configured if w not in native and w not in {e[1] for e in EXTRAS}]
    print(f'Source: {source}')
    if not missing and not extra:
        print(f'Up to date: {len(native)} native verbs.')
        return 0
    if missing:
        print(f'{len(missing)} new native verb(s) not in your spinner: '
              + ', '.join(missing[:8]) + ('…' if len(missing) > 8 else ''))
    if extra:
        print(f'{len(extra)} verb(s) are no longer native: '
              + ', '.join(extra[:8]) + ('…' if len(extra) > 8 else ''))
    print('Run this script again to refresh the list.')
    return 1


def cmd_remove():
    path = settings_path()
    settings = load_json(path, {})
    if not isinstance(settings, dict):
        print('Claude settings.json must be a JSON object.', file=sys.stderr)
        return 1
    state_file = state_path()
    state = load_json(state_file, {})
    if not isinstance(state, dict) or 'had_spinner' not in state:
        print('No spinner state recorded; leaving settings.json untouched.')
        return 0
    if settings.get('spinnerVerbs') != state.get('written'):
        print('spinnerVerbs changed since install; left untouched.')
        return 0
    folder = backup(path)
    if state.get('had_spinner'):
        settings['spinnerVerbs'] = state.get('old_spinner')
    else:
        settings.pop('spinnerVerbs', None)
    path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + '\n',
                    encoding='utf-8')
    state_file.unlink(missing_ok=True)
    print(f'Removed the playful spinner. Backup: {folder}')
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Give every native Claude Code spinner verb an emoji.')
    parser.add_argument('--claude', metavar='PATH',
                        help='path to the claude executable (default: find on PATH)')
    parser.add_argument('--install', action='store_true',
                        help='write the emoji spinner list (the default action)')
    parser.add_argument('--check', action='store_true',
                        help='report whether new native verbs need a refresh')
    parser.add_argument('--remove', action='store_true',
                        help='restore the spinnerVerbs value from before install')
    parser.add_argument('--dry-run', action='store_true',
                        help='print the generated configuration and write nothing')
    parser.add_argument('--list', action='store_true',
                        help='print the native verbs found on this machine')
    args = parser.parse_args()

    if args.list:
        binary, native, version = inspect(find_claude(args.claude))
        print('# ' + describe_source(binary, native, version), file=sys.stderr)
        print('\n'.join(native if native is not None else FALLBACK_VERBS))
        return 0
    if args.remove:
        return cmd_remove()
    found = find_claude(args.claude)
    if args.check:
        return cmd_check(found)
    return cmd_install(found, args.dry_run)


if __name__ == '__main__':
    sys.exit(main())
