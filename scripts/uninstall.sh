#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
import json,re
from pathlib import Path
home=Path.home()
target=home/'.config/starfield-terminal'
begin='# >>> STARFIELD TERMINAL >>>'
end='# <<< STARFIELD TERMINAL <<<' 
for rc in [home/'.zshrc',home/'.bashrc']:
    if not rc.exists(): continue
    original=rc.read_text(encoding='utf-8')
    updated, n=re.subn(r'(?ms)^'+re.escape(begin)+r'\n.*?^'+re.escape(end)+r'\n?', '', original)
    if n:
        rc.write_text(updated,encoding='utf-8')
        print('Removed startup hook from',rc)
settings=home/'.claude/settings.json'
state_file=target/'statusline-install-state.json'
spinner_state=target/'spinner-install-state.json'
if settings.is_file():
    data=json.loads(settings.read_text(encoding='utf-8'))
    changed=False
    if state_file.is_file():
        state=json.loads(state_file.read_text(encoding='utf-8'))
        current=data.get('statusLine') or {}
        # Only undo our own config, never revert someone else's later changes.
        if str(target/'statusline.py') in str(current.get('command','')):
            if state.get('had_statusline'):
                data['statusLine']=state.get('old_statusline')
            else:
                data.pop('statusLine',None)
            changed=True
            print('Restored prior Claude Code statusline setting')
        else:
            print('Claude Code statusline was changed since install; left untouched')
    if spinner_state.is_file():
        state=json.loads(spinner_state.read_text(encoding='utf-8'))
        if data.get('spinnerVerbs')==state.get('written'):
            if state.get('had_spinner'):
                data['spinnerVerbs']=state.get('old_spinner')
            else:
                data.pop('spinnerVerbs',None)
            changed=True
            spinner_state.unlink()
            print('Restored prior Claude Code spinner verbs')
        else:
            print('Claude Code spinner verbs were changed since install; left untouched')
    if changed:
        settings.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Assets and backups retained at',target)
print('Starship remains unchanged.')
PY
