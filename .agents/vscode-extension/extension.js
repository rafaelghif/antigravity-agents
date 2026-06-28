const vscode = require('vscode');
const cp = require('child_process');
const path = require('path');
const fs = require('fs');

function activate(context) {
    let profileStatusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    profileStatusBarItem.command = 'aac.switchProfile';
    context.subscriptions.push(profileStatusBarItem);

    // Update status bar
    updateProfileStatus(profileStatusBarItem);

    // Watch git_profiles.json for changes
    const rootPath = vscode.workspace.workspaceFolders ? vscode.workspace.workspaceFolders[0].uri.fsPath : null;
    if (rootPath) {
        const profilesPath = path.join(rootPath, '.agents', 'git_profiles.json');
        if (fs.existsSync(profilesPath)) {
            fs.watchFile(profilesPath, () => {
                updateProfileStatus(profileStatusBarItem);
            });
        }
    }

    // Command: switchProfile
    let switchDisposed = vscode.commands.registerCommand('aac.switchProfile', () => {
        if (!rootPath) return;
        const profilesPath = path.join(rootPath, '.agents', 'git_profiles.json');
        if (!fs.existsSync(profilesPath)) {
            vscode.window.showErrorMessage('git_profiles.json not found. Run bootstrap first.');
            return;
        }
        try {
            const data = JSON.parse(fs.readFileSync(profilesPath, 'utf8'));
            const profiles = data.profiles || [];
            const items = profiles.map(p => ({
                label: p.name,
                description: p.email,
                detail: p.active ? 'Active Profile' : ''
            }));
            vscode.window.showQuickPick(items, { placeHolder: 'Select Git Profile to switch to' }).then(selection => {
                if (selection) {
                    const helperPath = path.join(rootPath, 'helper.sh');
                    cp.exec(`"${helperPath}" profile switch "${selection.label}"`, (err, stdout, stderr) => {
                        if (err) {
                            vscode.window.showErrorMessage(`Failed to switch profile: ${stderr || err.message}`);
                        } else {
                            vscode.window.showInformationMessage(`Successfully switched profile to: ${selection.label}`);
                            updateProfileStatus(profileStatusBarItem);
                        }
                    });
                }
            });
        } catch (e) {
            vscode.window.showErrorMessage(`Failed to parse profiles: ${e.message}`);
        }
    });
    context.subscriptions.push(switchDisposed);

    // Command: lockModule
    let lockDisposed = vscode.commands.registerCommand('aac.lockModule', () => {
        if (!rootPath) return;
        vscode.window.showInputBox({ prompt: 'Enter module name to lock' }).then(moduleName => {
            if (moduleName) {
                const helperPath = path.join(rootPath, 'helper.sh');
                cp.exec(`"${helperPath}" lock "${moduleName}"`, (err, stdout, stderr) => {
                    if (err) {
                        vscode.window.showErrorMessage(`Failed to lock: ${stderr || err.message}`);
                    } else {
                        vscode.window.showInformationMessage(stdout.trim());
                    }
                });
            }
        });
    });
    context.subscriptions.push(lockDisposed);
}

function updateProfileStatus(statusBarItem) {
    const rootPath = vscode.workspace.workspaceFolders ? vscode.workspace.workspaceFolders[0].uri.fsPath : null;
    if (rootPath) {
        const profilesPath = path.join(rootPath, '.agents', 'git_profiles.json');
        if (fs.existsSync(profilesPath)) {
            try {
                const data = JSON.parse(fs.readFileSync(profilesPath, 'utf8'));
                const active = (data.profiles || []).find(p => p.active);
                if (active) {
                    statusBarItem.text = `$(person) AAC: ${active.name}`;
                    statusBarItem.tooltip = `Active Profile: ${active.email}`;
                    statusBarItem.show();
                    return;
                }
            } catch (e) {}
        }
    }
    statusBarItem.text = `$(person) AAC: No Profile`;
    statusBarItem.show();
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
