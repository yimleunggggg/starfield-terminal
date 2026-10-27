# ✧ Starfield Terminal · 星图终端

**给终端一片自己的小宇宙。**

每开一个新的终端标签页，在你的提示符上方随机出现一张星图插画和一句英文冷幽默。可选 Claude Code 双行状态栏；可选 Starship 提示符预设 —— 由你自己挑，程序绝不替你改。

[English README](README.md) · [Starship 预设](docs/STARSHIP.md) · [兼容性](#兼容性) · [遇到问题](#遇到问题)

[![tests](https://github.com/yimleunggggg/starfield-terminal/actions/workflows/tests.yml/badge.svg)](https://github.com/yimleunggggg/starfield-terminal/actions/workflows/tests.yml)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

![终端欢迎画面示意](docs/preview.png)

---

## 会看到什么

每次打开交互式终端，随机抽取**一条**欢迎语（共 12 组），配**一张**星图（共 6 款）。文案和插画是分开随机抽的，所以组合很难重复。

- **12 组欢迎语**：标题、正文、斜体收尾，各带一个 emoji。
- **6 款星图插画**：星点、连线、星座名，在 Ghostty 上通过 Kitty 图形协议以真实 PNG 显示。
- **12 张加粗标题图**：Ghostty 宽窗口下显示大号标题，窄窗口和其他终端自动退回文字。
- **可选 Claude Code 双行状态栏**：项目、Git 分支、模型、上下文占用。同一会话内 emoji 固定。
- **可选 Starship 预设选择器**：在 4 款**官方**预设里挑一个，写入前先备份你现有的 `starship.toml`。不选就不动。

**本项目只会写入：** `~/.config/starfield-terminal/` 下自己的文件、shell 启动文件里一个带标记的代码块，以及仅在 `--with-claude` 时修改 `~/.claude/settings.json` 的 `statusLine` 键。不碰你的项目目录、不装字体、不改 Ghostty 配置。

---

## 环境要求

| | |
| --- | --- |
| Python | 3.8 或更高（`python3 -V`） |
| 终端 | 想看图需要 [Ghostty](https://ghostty.org/download)；纯文字任何终端都行 |
| Shell | macOS / Linux 用 zsh 或 bash，Windows 用 PowerShell |

不需要 pip 安装任何包，不联网，不附带字体。

---

## 快速开始

```bash
git clone https://github.com/yimleunggggg/starfield-terminal.git
cd starfield-terminal
bash scripts/install.sh
```

然后**新开一个** Ghostty 标签页，就装好了。

第一次在终端里安装时，脚本只会问一个问题 —— 状态栏上怎么称呼这台机器：

```
Name for the statusline [你的-MacBook-Pro]:
```

直接回车就沿用电脑名称，也可以随便输入你喜欢的名字（比如 `NOVA / LAB`、`工作室`）。不想被问，装的时候加 `--name="NOVA / LAB"` 跳过。

想用 ZIP 也可以：点绿色的 **Code** 按钮下载，解压后进入文件夹运行同一条命令。

如果还想要 Claude Code 状态栏，这是**另一步**，需要单独选择：

```bash
bash scripts/install.sh --with-claude
```

如果状态栏没变，重启 Claude Code。

### 不开标签页也能看效果

```bash
python3 ~/.config/starfield-terminal/welcome.py              # 随机一条
python3 ~/.config/starfield-terminal/welcome.py --gallery    # 六款星图全看
python3 ~/.config/starfield-terminal/welcome.py --no-image   # 纯文字
python3 ~/.config/starfield-terminal/welcome.py --seed 5     # 固定随机种子
python3 ~/.config/starfield-terminal/welcome.py --version
```

---

## 改成你自己的

所有东西都在 `~/.config/starfield-terminal/` 下。

**标签文字。** 状态栏左上角的身份就是你安装时输入的名字 —— 没输入则沿用电脑名称。之后想改，编辑 `config.json`：

```json
{
  "label": "NOVA / STUDIO",
  "status_label": "NOVA / LAB"
}
```

删掉 `status_label` 就回到默认的机器名。`open -e` 是 macOS 命令，Linux / Windows 请用自己习惯的编辑器。

**欢迎语文案。** 把 `examples/welcome-library.json` 复制到 `~/.config/starfield-terminal/welcome-library.json`。每一项是四元数组：`[emoji, 标题, 正文, 收尾]`。格式不对的条目会被忽略，整体退回内置文案。自定义标题以文字显示，不使用标题图片。

**插画。** 把替换文件放进 `~/.config/starfield-terminal/constellations/`（`celestial-01.png` 到 `celestial-06.png`）和 `titles/`（`title-01.png` 到 `title-12.png`）。

---

## Claude Code 状态栏

长这样：

```
🍳  NOVA / LAB  │ PROJECT  starfield-terminal  ·  GIT main
MODEL  Claude Fable 5.1  │  CTX  42%
```

- emoji 由会话 ID 推导，所以一次对话里不会变。
- 当前目录不是 Git 仓库时，`GIT` 段自动隐藏。
- 第三方网关的上下文百分比会带 `~`，因为那类窗口大小往往是估算而非真实上报。
- 窗口变窄时先丢 Git 段，再截断项目名。

随时可以用 `bash scripts/uninstall.sh` 关掉。它会还原你之前的 `statusLine` —— 但只在当前值仍然指向本项目时才还原，不会覆盖你后来的改动。

---

## Starship（可选，独立项目）

原图上那条彩虹提示符来自 **[Starship](https://starship.rs/)**，是完全独立的第三方项目。本项目不安装它、不配置它、也不会覆盖它。如果你本来就在用 Starship，想换个样子：

```bash
bash scripts/starship-presets.sh --list
bash scripts/starship-presets.sh
```

选择器提供 4 款[官方预设](https://starship.rs/presets/)，写入前备份现有的 `~/.config/starship.toml`，并询问确认。输入 `0` 什么都不改。多数 Powerline 预设需要 Nerd Font，本项目不附带字体。

详细说明和非交互用法见 [docs/STARSHIP.md](docs/STARSHIP.md)。

---

## 兼容性

| 环境 | 欢迎语 | PNG 星图 | Claude 状态栏 |
| --- | --- | --- | --- |
| macOS + Ghostty + zsh | 支持 | 支持，窗口需 ≥ 84 列 | 可选 |
| Linux + Ghostty + bash/zsh | 预期可用，未逐一发行版验证 | 预期可用 | 可选 |
| macOS Terminal.app / iTerm2 + zsh | 仅文字（`--all-terminals`） | 文字回退 | 可选 |
| Windows Terminal + PowerShell | 仅文字 | 不提供 | 不安装 |

Ghostty 和 Windows Terminal 是两个不同的终端。星图依赖 Kitty 图形协议，Terminal.app 和 Windows Terminal 没有实现它，所以在这些环境里会显示彩色文字 —— 这是设计行为，不是故障。

```bash
bash scripts/install.sh --all-terminals   # macOS Terminal.app / iTerm2
bash scripts/install.sh --shell=bash      # Linux 且你的 shell 是 bash
```

---

## 遇到问题

**新开标签页什么都没有。**
默认安装只在 Ghostty 里生效，且只对交互式、非 SSH 的会话生效。先看 `echo $TERM_PROGRAM` 和 `echo $GHOSTTY_RESOURCES_DIR`。用的是别的终端？加 `--all-terminals` 重装。

**有文字但没有图。**
星图需要 Ghostty，并且窗口宽度 ≥ 84 列。把窗口拉宽，或者用 `--force-image` 验证。

**Claude Code 还是旧状态栏。**
重启 Claude Code。确认 `~/.claude/settings.json` 里的 `statusLine` 指向 `starfield-terminal/statusline.py`。

**emoji 或框线字符错位。**
这是字体问题，不是渲染问题 —— 在终端设置里换一款等宽字体即可。

**每个标签页出现两份欢迎语。**
你的 shell 启动文件里还有别的欢迎脚本。搜 `STARFIELD TERMINAL` 标记块，把周围其他的欢迎调用删掉。

**想重来。**
`bash scripts/uninstall.sh` 会移除启动块并还原状态栏。资源文件和备份会保留在 `~/.config/starfield-terminal/`，方便你回滚。

---

## Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-windows.ps1
```

只有文字欢迎语，不装星图，不改 Starship 和状态栏。卸载用 `.\scripts\uninstall-windows.ps1`。

---

## 参与贡献

欢迎提交 issue 和 PR —— 尤其是终端兼容性修复，以及你拥有版权的新星图素材。

```bash
python3 -m unittest discover -s tests -v
```

测试会装进临时 `HOME` 目录，不会碰你真实的 dotfiles。

提 issue 或 PR 时，**请不要**贴上真实的 `~/.zshrc`、`~/.claude/settings.json`、API Key 或私有 Git 凭据。

---

## 开源协议

MIT，见 [LICENSE](LICENSE)。

Ghostty、Starship 是独立第三方项目。Starship 的预设由 Starship 官方维护，本仓库只提供一个调用你本地 `starship` 命令的选择器。项目不附带任何字体文件。星图是装饰性插画 —— 星座名字是真的，连线的几何形状不是准确的星图。
