"""
Analyser – evaluates every rule against a repository.

Detection strategies (in order):
  1. Marker files & directories
  2. File extensions
  3. Content patterns inside specific files
  4. Dependency matching (package.json, requirements.txt, Gemfile, go.mod, Cargo.toml, composer.json)
  5. dotenv prefix scanning (.env, .env.local, .env.example, .env.*)
"""

from __future__ import annotations

import json
import os
import re
import logging
from pathlib import Path
from typing import Optional

from .rules import RULES, Rule, RuleMatch

logger = logging.getLogger("scanner")

# ── Dependency extraction helpers ──────────────────────────


def _extract_npm_deps(content: str) -> list[str]:
    """Extract package names from a package.json string."""
    try:
        pkg = json.loads(content)
        names: list[str] = []
        for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
            names.extend(pkg.get(key, {}).keys())
        return names
    except Exception:
        return []


def _extract_python_deps(content: str) -> list[str]:
    """Extract package names from requirements.txt / requirements-*.txt."""
    names: list[str] = []
    for line in content.splitlines():
        line = re.sub(r"#.*$", "", line).strip()
        if not line or line.startswith("-"):
            continue
        name = re.split(r"[><=!~;\[]", line)[0].strip()
        if name:
            names.append(name)
    return names


def _extract_ruby_deps(content: str) -> list[str]:
    """Extract gem names from a Gemfile."""
    return re.findall(r"""^\s*gem\s+['"]([^'"]+)['"]""", content, re.MULTILINE)


def _extract_go_deps(content: str) -> list[str]:
    """Extract Go module paths from go.mod."""
    return re.findall(r"^\s+([\w./-]+)\s+v", content, re.MULTILINE)


def _extract_cargo_deps(content: str) -> list[str]:
    """Extract crate names from Cargo.toml [dependencies]."""
    names: list[str] = []
    in_deps = False
    for line in content.splitlines():
        if re.match(r"^\[.*dependencies.*\]", line, re.IGNORECASE):
            in_deps = True
            continue
        if line.startswith("["):
            in_deps = False
            continue
        if in_deps:
            m = re.match(r"^(\S+)\s*=", line)
            if m:
                names.append(m.group(1))
    return names


def _extract_composer_deps(content: str) -> list[str]:
    """Extract composer package names from composer.json."""
    try:
        pkg = json.loads(content)
        names: list[str] = []
        names.extend(pkg.get("require", {}).keys())
        names.extend(pkg.get("require-dev", {}).keys())
        return names
    except Exception:
        return []


def _extract_docker_images(content: str) -> list[str]:
    """Extract docker image names from docker-compose / compose files."""
    images: list[str] = []
    for m in re.finditer(r"image:\s*['\"]?([^\s'\"#]+)", content):
        images.append(m.group(1).split(":")[0])
    return images


def _extract_env_var_names(content: str) -> list[str]:
    """Extract env-var names from .env-style files."""
    names: list[str] = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key = line.split("=", 1)[0].strip()
        if key:
            names.append(key)
    return names


# ── File-system provider ──────────────────────────────────


class FSProvider:
    """Provides file-system access for the analyser."""

    def __init__(self, root: str):
        self.root = root

    def list_dir(self, rel: str = ".") -> list[dict]:
        """List entries in a directory. Returns list of {path, name, is_dir}."""
        target = os.path.join(self.root, rel) if rel != "." else self.root
        if not os.path.isdir(target):
            return []
        entries = []
        try:
            for name in os.listdir(target):
                if name.startswith(".") and rel == ".":
                    # skip dot files at root — but allow .github etc. at deeper levels
                    # Actually mirror TS: always skip dot-prefixed entries
                    continue
                full = os.path.join(target, name)
                rel_path = name if rel == "." else f"{rel}/{name}"
                entries.append({
                    "path": rel_path,
                    "name": name,
                    "is_dir": os.path.isdir(full),
                })
        except PermissionError:
            pass
        return entries

    def read_file(self, rel_path: str) -> Optional[str]:
        """Read a file as UTF-8. Returns None on failure."""
        target = os.path.join(self.root, rel_path)
        try:
            with open(target, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return None

    def exists(self, rel_path: str) -> bool:
        target = os.path.join(self.root, rel_path)
        return os.path.exists(target)


# ── Main analyser ──────────────────────────────────────────


def analyse(repo_path: str) -> list[dict]:
    """
    Analyse a local repository and return a list of matched techs.
    Each item is {"name": str, "type": str}.
    """
    provider = FSProvider(repo_path)

    # 1. Build file index (root + 2 levels deep)
    all_paths: set[str] = set()
    root_names: set[str] = set()
    extensions: set[str] = set()

    root_entries = provider.list_dir(".")
    dirs: list[str] = []
    for e in root_entries:
        all_paths.add(e["path"])
        root_names.add(e["name"])
        if e["is_dir"]:
            dirs.append(e["name"])
        else:
            dot_idx = e["name"].rfind(".")
            if dot_idx > 0:
                extensions.add(e["name"][dot_idx:])

    # Walk 2 levels deep
    for d in dirs:
        children = provider.list_dir(d)
        for c in children:
            all_paths.add(c["path"])
            root_names.add(c["name"])
            if c["is_dir"]:
                grandchildren = provider.list_dir(c["path"])
                for gc in grandchildren:
                    all_paths.add(gc["path"])

    # 2. File content cache
    content_cache: dict[str, Optional[str]] = {}

    def read_cached(file_path: str) -> Optional[str]:
        if file_path in content_cache:
            return content_cache[file_path]
        content = provider.read_file(file_path)
        content_cache[file_path] = content
        return content

    # 3. Extract all dependencies upfront
    deps_map: dict[str, list[str]] = {
        "npm": [], "python": [], "ruby": [], "golang": [],
        "rust": [], "docker": [], "php": [],
    }

    pkg_json = read_cached("package.json")
    if pkg_json:
        deps_map["npm"] = _extract_npm_deps(pkg_json)

    # Python deps
    for f in ("requirements.txt", "requirements-dev.txt", "requirements-base.txt"):
        c = read_cached(f)
        if c:
            deps_map["python"].extend(_extract_python_deps(c))
    pyproject = read_cached("pyproject.toml")
    if pyproject:
        m = re.search(r"\[project\][\s\S]*?dependencies\s*=\s*\[([\s\S]*?)\]", pyproject)
        if m:
            deps_map["python"].extend(_extract_python_deps(m.group(1).replace('"', "")))

    gemfile = read_cached("Gemfile")
    if gemfile:
        deps_map["ruby"] = _extract_ruby_deps(gemfile)

    gomod = read_cached("go.mod")
    if gomod:
        deps_map["golang"] = _extract_go_deps(gomod)

    cargo_toml = read_cached("Cargo.toml")
    if cargo_toml:
        deps_map["rust"] = _extract_cargo_deps(cargo_toml)

    composer_json = read_cached("composer.json")
    if composer_json:
        deps_map["php"] = _extract_composer_deps(composer_json)

    # Docker images from compose files
    for f in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"):
        c = read_cached(f)
        if c:
            deps_map["docker"].extend(_extract_docker_images(c))
    # Dockerfile FROM lines
    dockerfile = read_cached("Dockerfile")
    if dockerfile:
        for m in re.finditer(r"^FROM\s+(\S+)", dockerfile, re.MULTILINE):
            deps_map["docker"].append(m.group(1).split(":")[0])

    # 4. Extract .env variable names
    env_var_names: list[str] = []
    for f in (".env", ".env.local", ".env.example", ".env.development", ".env.production", ".env.test"):
        c = read_cached(f)
        if c:
            env_var_names.extend(_extract_env_var_names(c))

    # 5. Evaluate every rule
    matched: list[dict] = []
    for rule in RULES:
        try:
            if _evaluate_rule(rule, all_paths, extensions, root_names, read_cached, provider, deps_map, env_var_names):
                matched.append({"name": rule.name, "type": rule.type})
        except Exception as err:
            logger.warning(f'Rule "{rule.id}" threw: {err}')

    return matched


# ── Rule evaluation ────────────────────────────────────────


def _evaluate_rule(
    rule: Rule,
    all_paths: set[str],
    extensions: set[str],
    root_names: set[str],
    read_cached,
    provider: FSProvider,
    deps_map: dict[str, list[str]],
    env_var_names: list[str],
) -> bool:
    m = rule.match

    # 1. File existence
    if m and m.files:
        for f in m.files:
            if f in root_names or f in all_paths:
                return True
            if provider.exists(f):
                return True

    # 2. Extension
    if m and m.extensions:
        for ext in m.extensions:
            if ext in extensions:
                return True

    # 3. Content patterns
    if m and m.content_patterns:
        for cp in m.content_patterns:
            content = read_cached(cp.file)
            if content is None:
                continue
            for pat in cp.patterns:
                if pat in content:
                    return True

    # 4. Dependency matching
    if rule.dependencies:
        for dep in rule.dependencies:
            pkg_list = deps_map.get(dep.type, [])
            if not pkg_list:
                continue
            for pkg in pkg_list:
                if pkg == dep.name:
                    return True

    # 5. dotenv prefix matching
    if rule.dotenv and env_var_names:
        for prefix in rule.dotenv:
            for v in env_var_names:
                if v.startswith(prefix):
                    return True

    return False
