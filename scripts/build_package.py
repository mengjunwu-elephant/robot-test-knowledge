"""Build a deterministic plugin ZIP from an explicit whitelist."""
import hashlib, json, re, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
NAMES = ("testcase-iteration", "pytest-generation")
def build(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT/"plugin.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("invalid version")
    entries = {"plugin.json": (ROOT/"plugin.json").read_bytes(),
               "install.py": (ROOT/"packaging/install.py").read_bytes(),
               "Install.cmd": (ROOT/"packaging/Install.cmd").read_bytes(),
               "INSTALL.md": (ROOT/"packaging/INSTALL.md").read_bytes(),
               "update.py": (ROOT/"packaging/update.py").read_bytes(),
               "Update.cmd": (ROOT/"packaging/Update.cmd").read_bytes()}
    for name in NAMES:
        folder = ROOT/"skills"/name
        for p in folder.rglob("*"):
            if p.is_symlink():
                raise ValueError("symlink in skill")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
                entries[p.relative_to(ROOT).as_posix()] = p.read_bytes()
    lock = {"name": manifest["name"], "version": version,
            "files": {n: hashlib.sha256(b).hexdigest() for n,b in sorted(entries.items())}}
    entries["package-manifest.json"] = (json.dumps(lock, ensure_ascii=False, indent=2)+"\n").encode("utf-8")
    archive = output/f"robot-test-knowledge-{version}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for name, content in sorted(entries.items()):
            info = zipfile.ZipInfo("robot-test-knowledge/"+name, date_time=(2026,10,9,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, content)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output/"SHA256SUMS.txt").write_text(digest+"  "+archive.name+"\n", encoding="utf-8")
    return archive
if __name__ == "__main__":
    print(build(ROOT/"dist"))
