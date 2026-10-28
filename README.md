# ✧ Starfield Terminal

**A little universe for your terminal.**

[![tests](https://github.com/yimleunggggg/starfield-terminal/actions/workflows/tests.yml/badge.svg)](https://github.com/yimleunggggg/starfield-terminal/actions/workflows/tests.yml)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A random constellation illustration and a dry one-liner above your prompt every time you open a new terminal tab. Optional Claude Code statusline. Optional Starship prompt presets — chosen by you, never applied for you.

[简体中文](README.zh-CN.md) · [Starship presets](docs/STARSHIP.md) · [Compatibility](#compatibility) · [Troubleshooting](#troubleshooting)

![Starfield Terminal welcome screen](docs/preview.png)

---

## What you get

Every new interactive tab prints **one** greeting picked from 12 entries, paired with **one** of 6 decorative constellation images. The greeting and the illustration are drawn independently, so the combinations rarely repeat.

- **12 greetings** — a heading image or styled text, a one-liner, and an italic sign-off, each with its own emoji.
- **6 constellation illustrations** — glow, lines and star labels, rendered as real PNGs through the Kitty graphics protocol on Ghostty.
- **12 bold heading sprites** — displayed large on wide Ghostty windows, falling back to text elsewhere.
- **Optional Claude Code statusline** — project, Git branch, model and context usage in two rows. One stable emoji per conversation.
- **Optional playful spinner** — every spinner verb built into your Claude Code, each with its own emoji, plus a few extras. Rebuilt from the binary you actually installed.
- **Optional Starship preset chooser** — a small interactive menu that applies an *official* Starship preset after backing up your existing `starship.toml`. Nothing is applied automatically.

**The installer only ever writes:** its own files under `~/.config/starfield-terminal/`, one marked block in your shell startup file, and — only with `--with-claude` — the `statusLine` key, or — only with `--with-spinner` — the `spinnerVerbs` key in `~/.claude/settings.json`. It does not touch your projects, your fonts, or your Ghostty config. The separate Starship chooser can also write `~/.config/starship.toml`, but only when you run it, and only after backing the file up.

---

## Requirements

| | |
| --- | --- |
| Python | 3.8 or newer (`python3 -V`) |
| Terminal | [Ghostty](https://ghostty.org/download) for images; any terminal for text |
| Shell | zsh or bash on macOS/Linux, PowerShell on Windows |

No pip packages, no network access, no fonts bundled.

---

## Four independent pieces

One installer, one config folder — but take only what you want.

| Piece | Turn it on | Needs | What it writes |
| --- | --- | --- | --- |
| **Greeting** | `bash scripts/install.sh` | Python 3.8+; Ghostty for images | `~/.config/starfield-terminal/`, one marked block in `~/.zshrc` or `~/.bashrc` |
| **Claude Code statusline** | `bash scripts/install.sh --with-claude` | Python 3.8+ (this also installs the greeting) | the same, plus `statusLine` in `~/.claude/settings.json` |
| **Playful spinner** | `bash scripts/install.sh --with-spinner` | Claude Code CLI; Python 3.8+ | the same, plus `spinnerVerbs` in `~/.claude/settings.json`, after a timestamped backup |
| **Starship preset** | `bash scripts/starship-presets.sh` | Starship already installed and initialised by you | `~/.config/starship.toml`, after a timestamped backup |

The first three are steps of the installer. The fourth is a separate script that runs only when you call it, and it refuses to run if `starship` is not on your `PATH`.

---

## Quick start

```bash
git clone https://github.com/yimleunggggg/starfield-terminal.git
cd starfield-terminal
bash scripts/install.sh
```

Then open a **new** Ghostty tab. That's it.

On a first interactive install the script asks one question — what the statusline should call this machine:

```
Name for the statusline [Your-MacBook-Pro]:
```

Press Enter to keep your computer's name, or type anything you like. Skip the question entirely with `--name="NOVA / LAB"`.

Prefer a ZIP? Download it from the green **Code** button, unzip, and run the same command inside the folder.

Add the Claude Code statusline too — this is a separate, opt-in step:

```bash
bash scripts/install.sh --with-claude
```

Restart Claude Code if the old statusline is still on screen.

Want emoji in Claude Code's spinner too? Same installer, another opt-in step:

```bash
bash scripts/install.sh --with-spinner
```

### See it without opening a tab

```bash
python3 ~/.config/starfield-terminal/welcome.py              # one random greeting
python3 ~/.config/starfield-terminal/welcome.py --gallery    # all six illustrations
python3 ~/.config/starfield-terminal/welcome.py --no-image   # text only
python3 ~/.config/starfield-terminal/welcome.py --seed 5     # reproducible pick
python3 ~/.config/starfield-terminal/welcome.py --diagnose   # why images do or don't render
python3 ~/.config/starfield-terminal/welcome.py --version
```

---

## Make it yours

Everything lives in `~/.config/starfield-terminal/`.

**Labels.** Two separate strings live in `config.json`:

- `label` — the line printed above each greeting. Defaults to `STARFIELD / TERMINAL`.
- `status_label` — the identity in the Claude Code statusline. Set from the name you typed at install time, and falls back to your computer's name.

```json
{
  "label": "NOVA / STUDIO",
  "status_label": "NOVA / LAB"
}
```

Remove `status_label` entirely to go back to the machine name. Use any text editor — `open -e` only exists on macOS.

**Greeting text.** Copy `examples/welcome-library.json` to `~/.config/starfield-terminal/welcome-library.json`. Each entry is a four-item array: `[emoji, heading, body, footer]`. Every row must be four strings — a single malformed row makes the whole file ignored, and the built-in twelve are used instead. Custom headings print as text rather than as sprite images.

**Illustrations.** Drop replacements into `~/.config/starfield-terminal/constellations/` (`celestial-01.png` … `celestial-06.png`) and `titles/` (`title-01.png` … `title-12.png`).

---

## The Claude Code statusline

Lines look like this:

```
🍳  NOVA / LAB  │ PROJECT  starfield-terminal  ·  GIT main
MODEL  Claude Fable 5.1  │  CTX  42%
```

- The emoji is derived from the session id, so it stays put for a conversation.
- `GIT` disappears when the current directory is not a Git repository.
- Context percentages from third-party gateways are marked `~` because those window sizes are often assumed rather than reported.
- Narrow panes drop the Git suffix first, then truncate the project name.

Disable it any time with `bash scripts/uninstall.sh` — run from the cloned folder, since the script lives in the repository. It restores your previous `statusLine`, but only if the current value still points at this project.

---

## Playful spinner (optional, separate)

Claude Code's working indicator picks a verb at random — `Baking`, `Cooking`, `Smooshing`, `Razzle-dazzling`. This option gives every verb built into your Claude Code its own emoji:

```
✳ 🥐 Baking…
```

```bash
bash scripts/install.sh --with-spinner
```

It reads the verb table out of the Claude Code you have installed (187 verbs in 2.1.x), adds an emoji to each, and keeps a handful of extras. Only `spinnerVerbs` in `~/.claude/settings.json` is changed; everything else in that file is preserved, and the old settings are copied to `~/.config/starfield-terminal/backups/` first.

**Why it uses `replace`, not `append`.** Claude Code's `append` mode joins your verbs onto the built-in list unchanged, so built-in words can never get an emoji. `replace` is the only mode where every verb shows an emoji — which also means the list is a snapshot. The script rebuilds it from your installed binary on every run, so after a Claude Code upgrade:

```bash
python3 ~/.config/starfield-terminal/claude-spinner.py --check   # says what is missing
python3 ~/.config/starfield-terminal/claude-spinner.py           # rebuilds the list
```

Remove it with `python3 ~/.config/starfield-terminal/claude-spinner.py --remove` or `bash scripts/uninstall.sh`; both restore whatever `spinnerVerbs` value was there before, and leave it alone if you have changed it since. `--dry-run` prints the configuration without writing, `--list` prints the native verbs found on this machine, and `--claude PATH` points at a non-standard install.

Works wherever the Claude Code CLI runs — macOS, Linux, Windows, any terminal — and does not need Ghostty, Starship, or the greeting. It is configured per machine, not synced. Your terminal font has to render emoji; if it does not, you will see boxes.

---

## Starship (optional, separate)

The rainbow prompt in the original screenshots is **[Starship](https://starship.rs/)**, an independent project. Starfield Terminal never installs Starship and never changes your prompt on its own. The optional chooser below writes exactly one preset, and only after backing up your `starship.toml` and asking you to confirm. If you already use Starship and want a new look:

```bash
bash scripts/starship-presets.sh --list
bash scripts/starship-presets.sh
```

The chooser offers four [official presets](https://starship.rs/presets/), backs up an existing `~/.config/starship.toml`, and asks before writing. Choosing `0` changes nothing, and it exits with a pointer to the install guide if `starship` is missing. Most Powerline presets need a Nerd Font, which this repository does not ship.

Details and non-interactive usage: [docs/STARSHIP.md](docs/STARSHIP.md).

---

## Compatibility

Only Ghostty draws the images. Every other terminal works too — it just gets the text layout.

| Where | Run | What you get |
| --- | --- | --- |
| macOS + Ghostty (zsh) | `bash scripts/install.sh` | Greeting, images, optional statusline |
| macOS Terminal.app / iTerm2 | `bash scripts/install.sh --all-terminals` | Greeting as text, optional statusline |
| Linux + Ghostty + bash | `bash scripts/install.sh --shell=bash` | Greeting, images |
| Linux, any other terminal | `bash scripts/install.sh --all-terminals` | Greeting as text |
| VS Code / JetBrains built-in terminal (macOS, Linux) | `bash scripts/install.sh --all-terminals` | Greeting as text |
| Windows Terminal + PowerShell | `.\scripts\install-windows.ps1` | Greeting as text; no statusline |
| Remote shell over SSH | nothing fires — see below | — |

Four things worth knowing:

- **Each machine installs separately.** Nothing syncs. `config.json`, the name you picked, and any custom artwork stay on the machine where you ran the installer — repeat it on your other machines.
- **SSH sessions are skipped in every mode.** Both the Ghostty and the `--all-terminals` hooks test for `SSH_CONNECTION`, so logging into a server never prints a greeting. Run `python3 ~/.config/starfield-terminal/welcome.py` there when you actually want one.
- **Images need two things at once:** Ghostty, and a window at least 84 columns wide. The illustrations use the Kitty graphics protocol, which Terminal.app and Windows Terminal do not implement.
- **tmux and screen are untested.** The greeting text prints; if the illustration goes missing, the multiplexer is the likely reason — it swallows the graphics escape.

---

## Troubleshooting

**A new tab shows nothing, or shows text but no image.**
Run `python3 ~/.config/starfield-terminal/welcome.py --diagnose` — it prints the terminal it detected, the column count, and which check failed. The usual causes: the default install only fires inside Ghostty for interactive, non-SSH shells (use `--all-terminals` elsewhere), and images also need a window at least 84 columns wide.

**Claude Code still shows the old statusline.**
Restart Claude Code. Confirm `~/.claude/settings.json` has a `statusLine` whose command points at `starfield-terminal/statusline.py`.

**Emoji or box characters look misaligned.**
That is a font issue, not a rendering one — pick a monospace font with good emoji metrics in your terminal settings.

**Two greetings appear per tab.**
You have another welcome hook in your shell startup file. Look for the `STARFIELD TERMINAL` marker block and remove any other greeting call around it.

**Updating to a newer version.**
`cd` into your clone, `git pull`, then `bash scripts/install.sh` — add `--with-claude` if you use the statusline and `--with-spinner` if you use the playful spinner, since each flag is the step that copies its own script. Your `config.json` and any custom `welcome-library.json` are left alone.

**Start over.**
`bash scripts/uninstall.sh` (from the cloned folder) removes the startup block and reverts the statusline. Your assets and backups stay in `~/.config/starfield-terminal/` for safety.

---

## Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-windows.ps1
```

Text-only greeting, no illustrations, no Starship or statusline changes. Undo with `.\scripts\uninstall-windows.ps1`.

---

## Contributing

Bug reports and pull requests are welcome — terminal compatibility fixes especially, and new constellation artwork that you have the rights to contribute.

```bash
python3 -m unittest discover -s tests -v
```

The suite installs into temporary `HOME` directories, so it never touches your real dotfiles.

Please never open an issue or PR containing your actual `~/.zshrc`, `~/.claude/settings.json`, API keys, or private Git credentials.

---

## License

MIT — see [LICENSE](LICENSE).

Ghostty and Starship are independent third-party projects. Starship's presets remain hosted and maintained by Starship; this repository only provides a selector that invokes your local `starship` binary. No fonts are bundled. The illustrations are decorative — the constellation names are real, the line geometry is not an accurate sky chart.
