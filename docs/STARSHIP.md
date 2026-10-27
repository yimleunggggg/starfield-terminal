# Optional Starship prompt styles

Starfield Terminal does **not** require Starship. The rainbow bar in the original screenshots came from [Starship](https://starship.rs/), an independent cross-shell prompt. Its themes and presets are owned by Starship and are not included as if they were original Starfield assets.

**Official preset gallery:** https://starship.rs/presets/

| Official preset | Character |
| --- | --- |
| Pastel Powerline | Pastel segmented rainbow bar, similar in spirit to the original screenshot |
| Catppuccin Powerline | Pastel segments with Catppuccin color palette |
| Tokyo Night | Cooler, darker high-contrast style |
| Gruvbox Rainbow | Warm retro segmented rainbow |

The Powerline presets require a properly configured Nerd Font for the glyphs. No fonts are bundled with this repository.

## macOS / Linux

Install Starship first using the [official guide](https://starship.rs/guide/). On macOS with Homebrew:

```bash
brew install starship
```

Initialize it **once** for your shell:

```bash
# zsh: add to ~/.zshrc (if not already present)
eval "$(starship init zsh)"

# bash: add to ~/.bashrc (if not already present)
eval "$(starship init bash)"
```

**Selection with safe backup:**

```bash
bash scripts/starship-presets.sh --list
bash scripts/starship-presets.sh
```

This asks which of four official styles to use, generates the selected preset using the locally installed Starship binary, backs up any existing `~/.config/starship.toml`, and requests confirmation before applying. Nothing happens if you select `0`.

**Non-interactive, explicitly requested application:**

```bash
bash scripts/starship-presets.sh --apply pastel-powerline
```

This will overwrite your current Starship config **after backing it up**. If you want to keep your current prompt, do not run it.

## Windows PowerShell

`scripts/starship-presets.sh` is a bash script and will not run under PowerShell. Use the manual steps below instead.

Install Starship using the [official guide](https://starship.rs/guide/). For example:

```powershell
winget install Starship.Starship
```

Initialize it once in your PowerShell `$PROFILE`:

```powershell
Invoke-Expression (&starship init powershell)
```

To try a preset, back up the config first:

```powershell
New-Item -ItemType Directory -Force "$HOME\.config" | Out-Null
$Config = "$HOME\.config\starship.toml"
if (Test-Path $Config) { Copy-Item $Config "$Config.backup-$(Get-Date -Format yyyyMMdd-HHmmss)" }
starship preset pastel-powerline -o $Config
```

Or choose another preset name from the [official gallery](https://starship.rs/presets/). A Nerd Font is needed for Powerline designs.

## Important

- The Starship configuration is independent from the welcome screen and from Claude Code statusline.
- The installer never touches `starship.toml`. Only `scripts/starship-presets.sh`, which you run yourself, writes it — after a timestamped backup and a confirmation prompt.
- A Starship preset will **not** look identical in every terminal: it depends on the font, background and shell prompt setup.
