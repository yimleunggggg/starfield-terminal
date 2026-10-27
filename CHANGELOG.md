# Changelog

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
