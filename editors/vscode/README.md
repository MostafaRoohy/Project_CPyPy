# CPy Formatter — VS Code Extension

Format the current Python file in the [CPy](../../README.md) personal style with a single keyboard
shortcut. The extension is a thin wrapper: it pipes the active editor buffer through
`python -m cpy format -` and replaces the document with the result, so all formatting behaviour comes
straight from the CPy Python package.

## Prerequisite

Install CPy into the Python environment VS Code uses:

```bash
pip install -e /path/to/CPy
```

Verify it runs:

```bash
echo "x=1" | python -m cpy format -
```

## Default shortcut

| Action          | Windows / Linux | macOS         |
| --------------- | --------------- | ------------- |
| CPy: Format File| `Ctrl+Alt+C`    | `Cmd+Alt+C`   |

The command is also available from the Command Palette as **CPy: Format File**.

## Settings

| Setting          | Default    | Description                                                              |
| ---------------- | ---------- | ----------------------------------------------------------------------- |
| `cpy.pythonPath` | `python`   | Interpreter used to run `-m cpy`. Use a full path to pin an environment.|
| `cpy.executable` | `""`       | Path to a standalone `cpy` binary; used instead of `python -m cpy`.     |
| `cpy.args`       | `[]`       | Extra args passed before `format -` (e.g. `["--config", "pyproject.toml"]`). |

## Running it locally (development)

1. Open this folder (`editors/vscode`) in VS Code.
2. Press `F5` to launch an **Extension Development Host**.
3. Open a Python file, press `Ctrl+Alt+C` (or `Cmd+Alt+C`), and watch it reformat.

## Packaging a `.vsix`

```bash
npm install -g @vscode/vsce
cd editors/vscode
vsce package
code --install-extension cpy-formatter-0.1.0.vsix
```

## Rebinding the shortcut

Open **Preferences: Open Keyboard Shortcuts**, search for `CPy: Format File`, and set your own chord.

## Troubleshooting

- **"could not run 'python'"** — set `cpy.pythonPath` to the full interpreter path (the one where you
  ran `pip install -e .`). The Python extension's selected interpreter path works well here.
- **Nothing happens / wrong style** — confirm `python -m cpy format -` works in a terminal with the
  same interpreter, and that your `pyproject.toml` `[tool.cpy]` rules are what you expect.
