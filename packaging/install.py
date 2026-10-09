"""Register this unpacked plugin in a personal marketplace. No network or hardware."""
import argparse, hashlib, json, os, re, shutil, tempfile
from pathlib import Path
NAME = "robot-test-knowledge"
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def guard(root, target):
    root = root.absolute()
    target = target.absolute()
    if not target.is_relative_to(root):
        raise ValueError("destination outside selected user directory")
    for part in [target, *target.parents]:
        if part == root.parent:
            break
        if part.is_symlink():
            raise ValueError("refusing symlink destination: " + str(part))
def install(package, user_root, apply=False):
    package = Path(package).resolve()
    home = Path(user_root).absolute()
    manifest = json.loads((package/"plugin.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    if manifest["name"] != NAME or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("unexpected plugin identity")
    lock = json.loads((package/"package-manifest.json").read_text(encoding="utf-8"))
    names = lock["files"]
    if "plugin.json" not in names:
        raise ValueError("missing plugin manifest hash")
    payload = {}
    for name, sha in names.items():
        rel = Path(name)
        if rel.is_absolute() or ".." in rel.parts or "\\" in name:
            raise ValueError("unsafe package path")
        p = package/rel
        if p.is_symlink() or not p.is_file() or digest(p) != sha:
            raise ValueError("package checksum mismatch: " + name)
        if name == "plugin.json" or name.startswith("skills/"):
            payload[name] = p
    for skill in ("testcase-iteration", "pytest-generation"):
        if f"skills/{skill}/SKILL.md" not in payload:
            raise ValueError("missing skill " + skill)
    dest = home/".codex/plugins/local"/NAME/version
    catalog = home/".agents/plugins/marketplace.json"
    guard(home, dest); guard(home, catalog)
    data = json.loads(catalog.read_text(encoding="utf-8")) if catalog.exists() else {
        "name": "personal-plugins",
        "interface": {"displayName": "个人技能包"},
        "plugins": []
    }
    if not isinstance(data.get("plugins"), list):
        raise ValueError("existing marketplace has no plugins list")
    entry = {"name": NAME, "source": {"source": "local",
             "path": "./" + dest.relative_to(home).as_posix()},
             "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
             "category": "Productivity"}
    existing = [e for e in data["plugins"] if e.get("name") == NAME]
    if len(existing) > 1:
        raise ValueError("duplicate existing plugin entries")
    if existing:
        old = existing[0]
        oldpath = old.get("source", {}).get("path", "") if isinstance(old.get("source"), dict) else ""
        if not oldpath.startswith("./.codex/plugins/local/robot-test-knowledge/"):
            raise FileExistsError("same plugin name belongs to another source")
        data["plugins"] = [entry if e.get("name") == NAME else e for e in data["plugins"]]
    else:
        data["plugins"].append(entry)
    if dest.exists():
        current = {p.relative_to(dest).as_posix(): p for p in dest.rglob("*") if p.is_file()}
        if set(current) != set(payload) or any(digest(current[n]) != digest(p) for n,p in payload.items()):
            raise FileExistsError("installed version changed; refusing overwrite")
    if apply:
        if not dest.exists():
            dest.mkdir(parents=True)
            for name, p in payload.items():
                output = dest/name
                output.parent.mkdir(parents=True, exist_ok=True)
                with output.open("xb") as f:
                    f.write(p.read_bytes())
        catalog.parent.mkdir(parents=True, exist_ok=True)
        if catalog.exists():
            backup = catalog.with_name("marketplace.before-robot-test-knowledge.json")
            if not backup.exists():
                shutil.copy2(catalog, backup)
        fd, temp = tempfile.mkstemp(prefix="marketplace-", suffix=".json", dir=catalog.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
            os.replace(temp, catalog)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
    return {"applied": apply, "plugin_path": str(dest), "marketplace": str(catalog),
            "next": "Restart app, choose personal plugin source, install the plugin, then open a new chat."}
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--package", type=Path, default=Path(__file__).resolve().parent)
    p.add_argument("--user-root", type=Path, default=Path.home())
    p.add_argument("--apply", action="store_true")
    a = p.parse_args()
    try:
        print(json.dumps(install(a.package, a.user_root, a.apply), ensure_ascii=False, indent=2))
    except Exception as e:
        p.exit(1, "Installation stopped: " + str(e) + "\n")
