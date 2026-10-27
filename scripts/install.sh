#!/usr/bin/env bash
# Starfield Terminal installer. No downloads, font changes, or Starship changes.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="ghostty"
SHELL_KIND="$(basename "${SHELL:-zsh}")"
CLAUDE=0
NAME=""
for arg in "$@"; do
  case "$arg" in
    --all-terminals) MODE=all ;;
    --with-claude) CLAUDE=1 ;;
    --shell=zsh) SHELL_KIND=zsh ;;
    --shell=bash) SHELL_KIND=bash ;;
    --name=*) NAME="${arg#--name=}" ;;
    *) printf 'Unknown argument: %s\n' "$arg" >&2; exit 2 ;;
  esac
done
command -v python3 >/dev/null || { echo 'Python 3.8 or newer is required. See README.' >&2; exit 1; }
python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 8) else 1)' \
  || { echo 'Python 3.8 or newer is required; found:' "$(python3 -V 2>&1)" >&2; exit 1; }
[[ "$SHELL_KIND" == zsh || "$SHELL_KIND" == bash ]] || { echo 'Supported shell startup files: zsh and bash.' >&2; exit 1; }
[[ -d "$ROOT/assets/constellations" && -d "$ROOT/assets/titles" ]] || { echo 'Repository assets missing.' >&2; exit 1; }

# Ask what the statusline should call this machine, but only on a first,
# interactive install. Re-runs keep whatever the user already chose.
if [[ -z "$NAME" && -t 0 && ! -f "$HOME/.config/starfield-terminal/config.json" ]]; then
  if [[ "$(uname -s)" == Darwin ]]; then
    DEFAULT_NAME="$(scutil --get ComputerName 2>/dev/null || true)"
  else
    DEFAULT_NAME="$(hostname 2>/dev/null | sed 's/\..*$//' || true)"
  fi
  [[ -n "$DEFAULT_NAME" ]] || DEFAULT_NAME="STARFIELD"
  printf 'Name for the statusline [%s]: ' "$DEFAULT_NAME" >&2
  read -r NAME || true
  [[ -n "$NAME" ]] || NAME="$DEFAULT_NAME"
fi

export STARFIELD_ROOT="$ROOT" STARFIELD_MODE="$MODE" STARFIELD_SHELL_KIND="$SHELL_KIND" STARFIELD_WITH_CLAUDE="$CLAUDE" STARFIELD_NAME="$NAME"
python3 - <<'PY'
import json, os, shutil, re
from pathlib import Path
from datetime import datetime
root = Path(os.environ['STARFIELD_ROOT'])
home = Path.home()
target = home / '.config' / 'starfield-terminal'
startup = home / ('.zshrc' if os.environ['STARFIELD_SHELL_KIND'] == 'zsh' else '.bashrc')
claude_dir = home / '.claude'
claude_settings = claude_dir / 'settings.json'
statusline = target / 'statusline.py'
marker_a = '# >>> STARFIELD TERMINAL >>>'
marker_b = '# <<< STARFIELD TERMINAL <<<' 
mode = os.environ['STARFIELD_MODE']
with_claude = os.environ['STARFIELD_WITH_CLAUDE'] == '1'
# Read the existing startup file; it is rewritten only after the checks below pass.
old = startup.read_text(encoding='utf-8') if startup.exists() else ''
# Parse and validate settings before changing anything.
if with_claude:
    settings = json.loads(claude_settings.read_text(encoding='utf-8')) if claude_settings.exists() else {}
    if not isinstance(settings, dict):
        raise ValueError('Claude settings.json must be a JSON object')
else:
    settings = None
stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
backup = target / 'backups' / stamp
backup.mkdir(parents=True, exist_ok=False)
for p, name in [(startup,'shellrc'), (target/'welcome.py','welcome.py'),
                (target/'statusline.py','statusline.py'),(target/'config.json','config.json'),
                (claude_settings,'claude-settings.json')]:
    if p.is_file(): shutil.copy2(p,backup/name)
for folder in ('constellations','titles'):
    if (target/folder).is_dir(): shutil.copytree(target/folder, backup/folder)
target.mkdir(parents=True,exist_ok=True)
shutil.copy2(root/'src/welcome.py',target/'welcome.py')
for folder in ('constellations','titles'):
    (target/folder).mkdir(exist_ok=True)
    for p in (root/'assets'/folder).glob('*.png'):
        shutil.copy2(p,target/folder/p.name)
config = target/'config.json'
if not config.exists():
    shutil.copy2(root/'examples/config.json',config)
# A name given at install time wins; an existing status_label is otherwise kept.
name = os.environ.get('STARFIELD_NAME','').strip()
if name:
    try:
        data = json.loads(config.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            data = {}
    except (OSError, ValueError):
        data = {}
    data['status_label'] = name
    config.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Replace/insert one private, distinct marker block. Do not touch other shell integrations.
if mode == 'all':
    condition = '[[ $- == *i* ]] && [[ -z "${SSH_CONNECTION:-}" ]]'
else:
    condition = '[[ $- == *i* ]] && [[ -z "${SSH_CONNECTION:-}" ]] && { [[ -n "${GHOSTTY_RESOURCES_DIR:-}" ]] || [[ "${TERM_PROGRAM:-}" == "ghostty" ]] || [[ "${TERM:-}" == *ghostty* ]]; }'
block = (marker_a+'\n'
         + '# Installed by Starfield Terminal; safe to remove this marker block.\n'
         + 'if '+condition+'; then\n'
         + '  python3 "$HOME/.config/starfield-terminal/welcome.py"\n'
         + 'fi\n'+marker_b)
if marker_a in old and marker_b in old:
    new, n = re.subn('(?ms)^'+re.escape(marker_a)+r'\n.*?^'+re.escape(marker_b),lambda _:block,old,count=1)
    assert n==1
else:
    new = old.rstrip('\n')+'\n\n'+block+'\n'
startup.parent.mkdir(parents=True,exist_ok=True)
startup.write_text(new,encoding='utf-8')
if with_claude:
    claude_dir.mkdir(exist_ok=True)
    shutil.copy2(root/'src/statusline.py',statusline)
    install_state = target/'statusline-install-state.json'
    # Keep the original once. Re-installation does not replace that snapshot.
    if not install_state.exists():
        install_state.write_text(json.dumps({'had_statusline':'statusLine' in settings,
            'old_statusline':settings.get('statusLine')},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    settings['statusLine'] = {'type':'command','command':f'python3 "{statusline}"','padding':0}
    claude_settings.write_text(json.dumps(settings,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Starfield Terminal installed.')
print('  Name: '+ (name or 'computer name (edit '+str(config)+' to change it)'))
print('  Welcome: one random joke + one random decorative constellation per tab')
print('  Shell startup: '+str(startup)+' ('+mode+')')
print('  Claude statusline: '+('enabled' if with_claude else 'unchanged; run --with-claude to opt in'))
print('  Starship: untouched; run scripts/starship-presets.sh --list to explore presets')
print('  Customization: '+str(config))
print('  Backup: '+str(backup))
print('  Preview: python3 ~/.config/starfield-terminal/welcome.py')
PY
