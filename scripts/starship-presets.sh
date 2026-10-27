#!/usr/bin/env bash
# Optional Starship preset chooser: does not install Starship or modify shell hooks.
set -euo pipefail
PRESETS=(pastel-powerline catppuccin-powerline tokyo-night gruvbox-rainbow)
show() {
  cat <<'TXT'
Official Starship presets (not provided by this repository):
  1) pastel-powerline      Pastel / rainbow Powerline
  2) catppuccin-powerline  Soft Catppuccin palette
  3) tokyo-night           Cool dark palette
  4) gruvbox-rainbow       Warm retro rainbow
  0) Keep existing prompt; do nothing
Browse screenshots first: https://starship.rs/presets/
Nerd Font required/recommended for Powerline and Nerd Font symbols.
TXT
}
mode="${1:-}"
if [[ "$mode" == --list ]]; then show; exit 0; fi
if [[ "$mode" == --apply ]]; then
  [[ $# -eq 2 ]] || { echo 'Usage: scripts/starship-presets.sh --apply PRESET' >&2; exit 2; }
  choice="$2"
else
  show
  if [[ ! -t 0 ]]; then echo 'Interactive selection needs a terminal. Use --apply PRESET.' >&2; exit 2; fi
  read -r -p 'Choose 0–4: ' n
  case "$n" in
    0|'') echo 'No changes.'; exit 0;;
    1) choice=pastel-powerline;;
    2) choice=catppuccin-powerline;;
    3) choice=tokyo-night;;
    4) choice=gruvbox-rainbow;;
    *) echo 'Invalid option.' >&2; exit 2;;
  esac
fi
valid=0
for p in "${PRESETS[@]}"; do [[ "$p" == "$choice" ]] && valid=1; done
[[ "$valid" -eq 1 ]] || { echo 'Invalid preset; run --list.' >&2; exit 2; }
command -v starship >/dev/null || { echo 'Please install Starship first: https://starship.rs/guide/' >&2; exit 1; }
config="${STARSHIP_CONFIG:-$HOME/.config/starship.toml}"
mkdir -p "$(dirname "$config")"
# Generate output to a temporary file and move into place only on success.
# BSD mktemp only substitutes a template that ends in X's, so generate a random
# directory and write the candidate file inside it (no fixed temp name, no race).
tmpdir="$(mktemp -d "${TMPDIR:-/tmp}/starfield-starship-XXXXXX")"
tmp="$tmpdir/starship.toml"
trap 'rm -rf "$tmpdir"' EXIT
trap 'rm -f "$tmp"' EXIT
starship preset "$choice" -o "$tmp"
[[ -s "$tmp" ]] || { echo 'Starship did not output a config.' >&2; exit 1; }
if [[ -f "$config" ]]; then
  backup="$config.backup-$(date +%Y%m%d-%H%M%S)"
  cp -p "$config" "$backup"
  echo "Backed up: $backup"
fi
if [[ "$mode" != --apply ]]; then
  printf 'Apply %s to %s? This replaces the current Starship preset. [y/N] ' "$choice" "$config"
  read -r confirm
  [[ "$confirm" == y || "$confirm" == Y ]] || { echo 'Cancelled; original file not modified.'; exit 0; }
fi
mv "$tmp" "$config"
echo "Applied official preset: $choice"
echo 'Restart/reload your shell to view the change; no Starship installation performed.'
