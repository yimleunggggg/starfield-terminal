# Changelog

## v1.2.0 — Playful spinner

Claude Code's working indicator picks from ~190 built-in verbs (Baking, Cooking,
Smooshing, Razzle-dazzling…). This release adds an optional component that gives
every one of them an emoji.

- New `scripts/claude-spinner.py`, installed to
  `~/.config/starfield-terminal/claude-spinner.py` with `--with-spinner`. It
  reads the verb table out of the Claude Code binary you actually have
  installed, pairs every verb with an emoji, and writes `spinnerVerbs` in
  `~/.claude/settings.json` after backing the file up.
- It uses `replace` mode, because `append` joins the built-in verbs unchanged
  and they can never carry an emoji. The list is rebuilt from the installed
  binary on every run, so verbs added by a Claude Code upgrade appear after
  `--check` / a re-run.
- `--check` reports drift, `--remove` restores the previous value, `--dry-run`
  prints without writing, `--list` prints the native verbs, `--claude PATH`
  handles non-standard installs.
- `uninstall.sh` restores `spinnerVerbs` only if it still matches what this
  project wrote.
- Also keeps six extras that are not in Claude Code's own list.

## v1.1.0 — Diagnose why images are missing

- `welcome.py --diagnose` prints the terminal it detected (`TERM_PROGRAM`,
  `TERM`, `GHOSTTY_RESOURCES_DIR`), the column count, whether stdout is a
  terminal, whether colour is enabled, how many assets are installed, and the
  resulting verdict for constellation images and heading sprites. When a check
  fails it names the fix. Plain text, safe to paste into an issue.
- Troubleshooting now starts with that command instead of asking users to guess
  between "wrong terminal" and "window too narrow".

## v1.0.4 — Per-terminal instructions

No code changes. The compatibility table listed environments but never said what
a user on those environments should run.

- One table, one row per environment, each with the exact command: Ghostty,
  Terminal.app / iTerm2, Linux with bash, other Linux terminals, IDE terminals,
  Windows, and SSH.
- Four rules that were missing: installs are per machine with nothing synced;
  SSH sessions are skipped in every mode; images need Ghostty *and* an 84-column
  window; tmux and screen are untested.

## v1.0.3 — Documentation corrections

No code changes. The published instructions were wrong in five places:

- The Starship section claimed the project never configures Starship. The
  optional chooser does write `~/.config/starship.toml`; the text now says so,
  and states separately what the installer writes and what the chooser writes.
- The three pieces — greeting, Claude Code statusline, Starship preset — now
  have their own table with the command, the prerequisite, and the side effect
  of each.
- `label` and `status_label` are explained individually; only one of them used
  to be documented.
- A welcome library is rejected as a whole when any row is malformed, not entry
  by entry.
- Added update steps, noted that `uninstall.sh` runs from the cloned folder,
  and noted that the chooser is bash-only and will not run under PowerShell.

## v1.0.2 — Restore the spacer line

- The statusline prints a trailing U+2800 BRAILLE PATTERN BLANK. It renders as
  nothing but is not whitespace, so the host keeps the blank line between the
  statusline and its own indicators instead of trimming it.

## v1.0.1 — Choose your own name

- The installer asks one question on a first interactive install: what the
  statusline should call this machine. Press Enter to keep the computer name, or
  type your own. Re-running the installer never overwrites a choice you made.
- Non-interactive installs (CI, piped scripts) skip the question; use
  `--name="NOVA / LAB"` to set it explicitly.
- The computer-name fallback is no longer upper-cased or split on dashes, so a
  MacBook Pro reads `Yim的MacBook Pro` rather than `YIMDEMACBOOK / PRO`.

## v1.0.0 — Initial public release

- Terminal greeting for Ghostty: twelve rotating one-liners, six decorative PNG
  constellation charts, and twelve bold title sprites. Greeting and artwork are
  drawn independently.
- Generic public labeling by default. The Claude Code statusline identity falls
  back to the computer name; both labels are overridable in `config.json`.
- Optional Claude Code two-line statusline: project, Git branch, model, and
  context usage. Gateway-reported context percentages are marked as estimates.
- Optional Starship preset chooser: official presets only, interactive opt-in,
  timestamped backup of an existing `starship.toml`, nothing applied silently.
- Primary target is macOS + Ghostty. Terminal.app and iTerm2 get a text-only
  mode, Linux bash/zsh is expected to work, and Windows PowerShell has a
  text-only installer.
- Backup-first install and uninstall. Repeated installs keep a single startup
  hook. Uninstall restores the previous Claude Code statusline only while it
  still points at this project.
- Integration tests exercise install, uninstall, and preset selection against
  temporary HOME directories.

### Fixed before the first release

- The statusline identity was hard-coded and ignored `status_label` in
  `config.json`.
- `scripts/starship-presets.sh` used a `mktemp` template that BSD/macOS does not
  randomize, so concurrent runs shared one temporary path.
- The installer's Ghostty detection did not match the runtime check in
  `welcome.py`, which could leave the hook installed but silent.
