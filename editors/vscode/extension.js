"use strict";

//#####################################################################################################
// CPy Formatter — VS Code extension
//
// Registers the "CPy: Format File" command (bound to Ctrl+Alt+C / Cmd+Alt+C). On invoke it pipes the
// active editor's buffer through `python -m cpy format -` and replaces the document with the result.
// The formatting logic lives entirely in the Python package, so this extension stays a thin shell.
//#####################################################################################################

const vscode = require("vscode");
const { spawn } = require("child_process");
const path = require("path");

//-----------------------------------------------------------------------------------------------------

function resolveCommand(document)
{
    const config = vscode.workspace.getConfiguration("cpy");
    const executable = config.get("executable", "").trim();
    const extraArgs = config.get("args", []);

    let command;
    let args;

    if (executable !== "")
    {
        command = executable;
        args = [...extraArgs, "format", "-"];
    }
    else
    {
        command = config.get("pythonPath", "python");
        args = ["-m", "cpy", ...extraArgs, "format", "-"];
    }

    // Discover pyproject.toml config relative to the file being formatted.
    const filePath = document.uri.fsPath;
    if (filePath)
    {
        args = args.concat(["--stdin-filename", filePath]);
    }

    return { command, args };
}

//-----------------------------------------------------------------------------------------------------

function runCpy(command, args, cwd, input)
{
    return new Promise((resolve, reject) =>
    {
        let child;
        try
        {
            child = spawn(command, args, { cwd });
        }
        catch (err)
        {
            reject(err);
            return;
        }

        let stdout = "";
        let stderr = "";

        child.stdout.on("data", (chunk) => { stdout += chunk; });
        child.stderr.on("data", (chunk) => { stderr += chunk; });

        child.on("error", (err) => { reject(err); });

        child.on("close", (code) =>
        {
            if (code === 0)
            {
                resolve(stdout);
            }
            else
            {
                const message = stderr.trim().split("\n")[0] || ("CPy exited with code " + code);
                reject(new Error(message));
            }
        });

        child.stdin.end(input);
    });
}

//-----------------------------------------------------------------------------------------------------

async function formatActiveFile()
{
    const editor = vscode.window.activeTextEditor;

    if (!editor)
    {
        vscode.window.showWarningMessage("CPy: no active editor to format.");
        return;
    }

    const document = editor.document;

    if (document.languageId !== "python")
    {
        vscode.window.showWarningMessage("CPy only formats Python files.");
        return;
    }

    const original = document.getText();

    if (original.length === 0)
    {
        return;
    }

    const { command, args } = resolveCommand(document);

    const workspaceFolder = vscode.workspace.getWorkspaceFolder(document.uri);
    const cwd = workspaceFolder
        ? workspaceFolder.uri.fsPath
        : (document.uri.fsPath ? path.dirname(document.uri.fsPath) : undefined);

    let formatted;
    try
    {
        formatted = await runCpy(command, args, cwd, original);
    }
    catch (err)
    {
        if (err && err.code === "ENOENT")
        {
            vscode.window.showErrorMessage(
                "CPy: could not run '" + command + "'. Check the cpy.pythonPath / cpy.executable setting."
            );
        }
        else
        {
            vscode.window.showErrorMessage("CPy: " + (err && err.message ? err.message : String(err)));
        }
        return;
    }

    if (formatted === original)
    {
        vscode.window.setStatusBarMessage("CPy: already formatted", 2000);
        return;
    }

    const fullRange = new vscode.Range(
        document.positionAt(0),
        document.positionAt(original.length)
    );

    await editor.edit((editBuilder) =>
    {
        editBuilder.replace(fullRange, formatted);
    });

    vscode.window.setStatusBarMessage("CPy: formatted", 2000);
}

//-----------------------------------------------------------------------------------------------------

function activate(context)
{
    context.subscriptions.push(
        vscode.commands.registerCommand("cpy.formatFile", formatActiveFile)
    );
}

function deactivate() {}

module.exports = { activate, deactivate };
