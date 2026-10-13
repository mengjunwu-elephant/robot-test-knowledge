"""Build a deterministic plugin ZIP from an explicit whitelist."""
import argparse, hashlib, io, json, re, subprocess, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
NAMES = ("testcase-iteration", "pytest-generation")
TEXT_SUFFIXES = {".json", ".md", ".py", ".yaml", ".yml"}

def package_bytes(path):
    """Keep release payload identical across Windows and Linux checkouts."""
    data = path.read_bytes()
    if path.suffix.lower() == ".cmd":
        return data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    if path.suffix.lower() in TEXT_SUFFIXES:
        return data.replace(b"\r\n", b"\n")
    return data

def build(output, channel="candidate"):
    if channel not in ("candidate", "release"):raise ValueError("invalid build channel")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT/"plugin.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("invalid version")
    entries = {"plugin.json": package_bytes(ROOT/"plugin.json"),
               "install.py": package_bytes(ROOT/"packaging/install.py"),
               "Install.cmd": package_bytes(ROOT/"packaging/Install.cmd"),
               "INSTALL.md": package_bytes(ROOT/"packaging/INSTALL.md"),
               "update.py": package_bytes(ROOT/"packaging/update.py"),
               "Update.cmd": package_bytes(ROOT/"packaging/Update.cmd")}
    for name in NAMES:
        folder = ROOT/"skills"/name
        for p in folder.rglob("*"):
            if p.is_symlink():
                raise ValueError("symlink in skill")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
                entries[p.relative_to(ROOT).as_posix()] = package_bytes(p)
    source_hash = hashlib.sha256("".join(n+"\0"+hashlib.sha256(b).hexdigest()+"\n" for n,b in sorted(entries.items())).encode()).hexdigest()
    try:
        revision = subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],stderr=subprocess.DEVNULL).decode().strip()
        dirty = bool(subprocess.check_output(['git','-C',str(ROOT),'status','--porcelain'],stderr=subprocess.DEVNULL).strip())
    except (OSError,subprocess.CalledProcessError):
        revision = None; dirty = None
    identity = {'schema_version':1,'version':version,'channel':channel,'source_revision':revision,'working_tree_dirty':dirty,'payload_sha256':source_hash}
    entries['build-info.json'] = (json.dumps(identity,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    lock = {"name": manifest["name"], "version": version,
            "files": {n: hashlib.sha256(b).hexdigest() for n,b in sorted(entries.items())}}
    entries["package-manifest.json"] = (json.dumps(lock, ensure_ascii=False, indent=2)+"\n").encode("utf-8")
    suffix = "" if channel=="release" else "-candidate-"+(revision[:12] if revision else "unknown")+("-dirty" if dirty else "")+"-"+source_hash[:12]
    archive = output/f"robot-test-knowledge-{version}{suffix}.zip"
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for name, content in sorted(entries.items()):
            info = zipfile.ZipInfo("robot-test-knowledge/"+name, date_time=(2026,10,9,0,0,0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, content)
    payload = buffer.getvalue()
    if archive.exists():
        if archive.read_bytes()!=payload:raise FileExistsError('refusing to overwrite a different package: '+str(archive))
    else:
        with archive.open('xb') as f:f.write(payload)
    digest = hashlib.sha256(payload).hexdigest()
    (output/"SHA256SUMS.txt").write_text(digest+"  "+archive.name+"\n", encoding="utf-8")
    return archive
if __name__ == "__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--channel",choices=["candidate","release"],default="candidate");parser.add_argument("--output",type=Path);args=parser.parse_args()
    print(build(args.output or ROOT/"dist"/args.channel,args.channel))
