# VS Code Integration

CPy plugs into VS Code so you can reformat the current Python file in the CPy style with **one
keyboard shortcut**: `Ctrl+Alt+C` (Windows / Linux) or `Cmd+Alt+C` (macOS).

The integration is deliberately thin. The editor never reimplements any formatting — it pipes the
active buffer through the CPy CLI (`python -m cpy format -`, reading stdin and writing stdout) and
replaces the document with the result. The single source of truth for the style stays the Python
package.

```
VS Code buffer ──stdin──▶ python -m cpy format - ──stdout──▶ replace document
```

---

## 1. Prerequisite: install CPy

Install CPy into the Python environment VS Code uses:

```bash
pip install -e /path/to/CPy
```

Confirm the CLI works (this is exactly what the editor calls):

```bash
echo "x=1" | python -m cpy format -
```

---

## 2. The extension (recommended)

The extension lives in [`editors/vscode/`](../editors/vscode). It is plain JavaScript — no build step.

### Run it from source

1. Open `editors/vscode` in VS Code.
2. Press `F5` to launch an **Extension Development Host**.
3. Open any `.py` file and press `Ctrl+Alt+C` / `Cmd+Alt+C`.

### Install a packaged build

```bash
npm install -g @vscode/vsce
cd editors/vscode
vsce package
code --install-extension cpy-formatter-0.1.0.vsix
```

### Command and keybinding

- Command palette: **CPy: Format File**
- Default keybinding: `Ctrl+Alt+C` / `Cmd+Alt+C`, active only when a Python editor is focused.
- Rebind via **Preferences: Open Keyboard Shortcuts** → search `CPy: Format File`.

### Settings

| Setting          | Default  | Description                                                       |
| ---------------- | -------- | ---------------------------------------------------------------- |
| `cpy.pythonPath` | `python` | Interpreter used to run `-m cpy`. Set a full path to pin an env. |
| `cpy.executable` | `""`     | Standalone `cpy` binary to use instead of `python -m cpy`.       |
| `cpy.args`       | `[]`     | Extra args before `format -`, e.g. `["--config", "pyproject.toml"]`. |

The extension passes `--stdin-filename <path>` so CPy discovers the right `pyproject.toml`
`[tool.cpy]` configuration by walking up from the edited file.

---

## 3. No-extension fallback (Task + keybinding)

If you prefer not to install the extension, you can wire the CLI to a key with a task.

`.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "CPy: format current file",
            "type": "shell",
            "command": "python -m cpy format ${file}",
            "presentation": { "reveal": "silent" },
            "problemMatcher": []
        }
    ]
}
```

`keybindings.json` (Preferences: Open Keyboard Shortcuts (JSON)):

```json
{
    "key": "ctrl+alt+c",
    "command": "workbench.action.tasks.runTask",
    "args": "CPy: format current file",
    "when": "editorLangId == python"
}
```

This rewrites the file in place; VS Code reloads it automatically. The extension route is smoother
because it formats the in-memory buffer (works on unsaved edits and preserves the undo stack).

---

## 4. Troubleshooting

- **`could not run 'python'`** — point `cpy.pythonPath` at the full interpreter path where you ran
  `pip install -e .` (the interpreter the Python extension selects usually works).
- **Wrong / no formatting** — run `python -m cpy format -` in a terminal with the same interpreter to
  confirm behaviour, and check your `[tool.cpy]` `enabled_rules` / `disabled_rules`.
- **Syntax errors in the file** — CPy returns the input unchanged on unparseable source, so a failed
  format leaves your buffer exactly as it was.
