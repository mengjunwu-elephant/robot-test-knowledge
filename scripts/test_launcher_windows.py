"""Explicit Windows launcher build/test; importing this module has no side effects."""
import argparse, base64, os, subprocess, tempfile, json, hashlib, zipfile, sys
from pathlib import Path

POWERSHELL=r'''$ErrorActionPreference = 'Stop'
$log = $env:ROBOT_SKILL_BUNDLE + '.log'
try {
    'Starting offline skill package installation.' | Set-Content -LiteralPath $log -Encoding UTF8
    $self = [IO.File]::ReadAllText($env:ROBOT_SKILL_BUNDLE)
    $parts = $self -split '(?m)^:ROBOT_PACKAGE_DATA\r?$', 2
    if ($parts.Count -ne 2) { throw 'Embedded package marker not found' }
    $bytes = [Convert]::FromBase64String($parts[1].Trim())
    $dir = Join-Path ([IO.Path]::GetTempPath()) ('robot-test-skills-' + [Guid]::NewGuid().ToString('N'))
    [IO.Directory]::CreateDirectory($dir) | Out-Null
    $archive = Join-Path $dir 'robot-test-knowledge-__VERSION__.zip'
    [IO.File]::WriteAllBytes($archive, $bytes)
    Add-Type -AssemblyName System.IO.Compression.FileSystem; [IO.Compression.ZipFile]::ExtractToDirectory($archive, $dir)
    $installer = Join-Path $dir 'robot-test-knowledge/install.py'
    $arguments = @('-X', 'utf8', $installer, '--apply')
    if ($env:ROBOT_SKILL_TEST_ROOT) { $arguments += @('--user-root', $env:ROBOT_SKILL_TEST_ROOT) }
    if ($env:ROBOT_SKILL_PYTHON) { $runner = $env:ROBOT_SKILL_PYTHON }
    elseif (Get-Command py -ErrorAction SilentlyContinue) { $runner = (Get-Command py).Source; $arguments = @('-3') + $arguments }
    elseif (Get-Command python -ErrorAction SilentlyContinue) { $runner = (Get-Command python).Source }
    else { throw 'Python 3.10 or newer is required' }
    $result = & $runner @arguments 2>&1
    $code = $LASTEXITCODE
    $result | Add-Content -LiteralPath $log -Encoding UTF8
    $result | ForEach-Object { Write-Host $_ }
    if ($code -ne 0) { throw ('Installer returned exit code ' + $code) }
    Write-Host 'Registration complete. Restart the app and install the plugin from your personal source.'
    exit 0
} catch {
    $message = 'Installation stopped: ' + $_.Exception.Message
    try { $message | Add-Content -LiteralPath $log -Encoding UTF8 } catch {}
    Write-Host $message
    Write-Host ('Log: ' + $log)
    exit 1
}
'''

def build_launcher(archive, launcher):
    archive=Path(archive);launcher=Path(launcher)
    with zipfile.ZipFile(archive) as z:
        version=json.loads(z.read('robot-test-knowledge/plugin.json'))['version']
    encoded=base64.b64encode(POWERSHELL.replace('__VERSION__',version).encode('utf-16le')).decode('ascii')
    payload=base64.b64encode(archive.read_bytes()).decode('ascii')
    text='@echo off\nsetlocal\nset "ROBOT_SKILL_BUNDLE=%~f0"\n"%SystemRoot%\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -NoProfile -InputFormat Text -OutputFormat Text -EncodedCommand '+encoded+'\nset "ROBOT_SKILL_EXIT=%ERRORLEVEL%"\necho.\necho Log file: "%~f0.log"\necho Press any key to close this window.\npause >nul\nexit /b %ROBOT_SKILL_EXIT%\n:ROBOT_PACKAGE_DATA\n'+payload+'\n'
    content=text.replace('\n','\r\n').encode('ascii')
    launcher.parent.mkdir(parents=True,exist_ok=True)
    if launcher.exists():
        if launcher.read_bytes()!=content:raise FileExistsError('refusing to replace launcher: '+str(launcher))
    else:
        with launcher.open('xb') as f:f.write(content)
    return launcher

def verify_launcher(archive):
    if os.name!='nt':raise RuntimeError('Windows is required for actual CMD validation')
    archive=Path(archive)
    with tempfile.TemporaryDirectory(prefix='robot-launcher-test-') as tmp:
        testroot=Path(tmp);launcher=build_launcher(archive,testroot/'Install.cmd')
        env=dict(os.environ,ROBOT_SKILL_TEST_ROOT=str(testroot/'user'),ROBOT_SKILL_PYTHON=sys.executable)
        run=subprocess.run([os.environ.get('COMSPEC','C:/Windows/System32/cmd.exe'),'/d','/c',str(launcher)],input='\n',text=True,capture_output=True,env=env,timeout=45)
        if run.returncode!=0:raise AssertionError((run.returncode,run.stdout,run.stderr))
        catalog=testroot/'user/.agents/plugins/marketplace.json'
        if len(json.loads(catalog.read_text(encoding='utf-8'))['plugins'])!=1:raise AssertionError('registration failed')
        env['ROBOT_SKILL_PYTHON']=str(testroot/'missing-python.exe')
        failed=subprocess.run([os.environ.get('COMSPEC','C:/Windows/System32/cmd.exe'),'/d','/c',str(launcher)],input='\n',text=True,capture_output=True,env=env,timeout=45)
        if failed.returncode==0 or 'Installation stopped:' not in failed.stdout or 'Press any key' not in failed.stdout:raise AssertionError('failure path lost diagnostic or close prompt')
    return {'package_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'cmd_success_path':True,'cmd_failure_path':True,'scope':'temporary user root; desktop discovery not tested'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',required=True,type=Path);p.add_argument('--launcher',type=Path);p.add_argument('--report',type=Path);a=p.parse_args()
    if a.report and (a.report.resolve()==a.archive.resolve() or a.launcher and a.report.resolve()==a.launcher.resolve()):p.error('report must be separate from inputs')
    result=verify_launcher(a.archive)
    if a.launcher:build_launcher(a.archive,a.launcher)
    text=json.dumps(result,ensure_ascii=False,indent=2)
    if a.report:a.report.write_text(text+'\n',encoding='utf-8')
    print(text)

if __name__=='__main__':main()
