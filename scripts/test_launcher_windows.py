import base64, os, subprocess, tempfile, json, hashlib, zipfile, sys
from pathlib import Path
repo=Path(__file__).resolve().parents[1]; r=repo.parent
version=json.loads((repo/'plugin.json').read_text(encoding='utf-8'))['version']
ps=r'''$ErrorActionPreference = 'Stop'
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
ps=ps.replace('__VERSION__',version)
encoded=base64.b64encode(ps.encode('utf-16le')).decode('ascii')
archive=repo/f'dist/robot-test-knowledge-{version}.zip'
payload=base64.b64encode(archive.read_bytes()).decode('ascii')
text=r'''@echo off
setlocal
set "ROBOT_SKILL_BUNDLE=%~f0"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat Text -OutputFormat Text -EncodedCommand '''+encoded+'''
set "ROBOT_SKILL_EXIT=%ERRORLEVEL%"
echo.
echo Log file: "%~f0.log"
echo Press any key to close this window.
pause >nul
exit /b %ROBOT_SKILL_EXIT%
:ROBOT_PACKAGE_DATA
'''+payload+'\n'
launcher=r/f'robot-test-knowledge-{version}-Install.cmd'
launcher.write_text(text,encoding='ascii',newline='\r\n')
# Test the actual CMD entry point without touching the real user's plugin directory.
with tempfile.TemporaryDirectory(prefix='robot-launcher-test-') as tmp:
    testroot=Path(tmp)
    env=dict(os.environ,ROBOT_SKILL_TEST_ROOT=str(testroot/'user'),ROBOT_SKILL_PYTHON=sys.executable)
    run=subprocess.run([os.environ.get('COMSPEC','C:/Windows/System32/cmd.exe'),'/d','/c',str(launcher)],input='\n',text=True,capture_output=True,env=env,timeout=45)
    print(run.stdout);assert run.returncode==0,(run.returncode,run.stderr)
    catalog=testroot/'user/.agents/plugins/marketplace.json';assert catalog.exists()
    assert len(json.loads(catalog.read_text(encoding='utf-8'))['plugins'])==1
    env['ROBOT_SKILL_PYTHON']=str(testroot/'missing-python.exe')
    failed=subprocess.run([os.environ.get('COMSPEC','C:/Windows/System32/cmd.exe'),'/d','/c',str(launcher)],input='\n',text=True,capture_output=True,env=env,timeout=45)
    assert failed.returncode!=0
    assert 'Installation stopped:' in failed.stdout
    assert 'Press any key' in failed.stdout
    print('Failure path retained error message and close prompt.')
report={'date':'2026-10-09','version':version,'package_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'installer_tests':7,'cmd_success_path':True,'cmd_failure_path':True,'scope':'temporary user root only; desktop plugin discovery not tested'}
(repo/'packaging/bundle-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))


