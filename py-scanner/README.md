# py-scanner

A small CLI Python scanner for analyzing repositories and producing JSON reports.

**Quick overview**
- Scans repositories listed in a text file and outputs a JSON report.

**Prerequisites**
- Python 3.8 or newer
- Git (for cloning repositories during scans)

**Install (recommended: virtual environment)**
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# Install from the project root
pip install -e .
```

If the project uses `pyproject.toml` dependencies, you can also use
```bash
pip install .
```

Files you may find useful:
- [pyproject.toml](pyproject.toml)
- [scanner/reame.md](scanner/reame.md)
- [examples/repos.txt](examples/repos.txt)

**Usage**
Run the scanner as a module from the project root.

Basic example (Windows paths shown):
```powershell
python -m scanner scan -i .\examples\repos.txt -o py-report.json
```

Example with concurrency and cleanup:
```bash
python -m scanner scan -i repos.txt -o report.json --concurrency 4 --cleanup
```

Common flags (as used in examples):
- `-i` / `--input`: path to the input file containing repository URLs (one per line).
- `-o` / `--output`: path to the JSON report file to generate.
- `--concurrency`: number of repositories to scan in parallel (integer).
- `--cleanup`: remove cloned repositories after scanning (flag).

**Repository layout**
- `scanner/` — main package with CLI and scanner implementation.
  - `scanner/cli.py` — CLI entrypoints and argument parsing.
  - `scanner/scanner.py` — scanning logic.
  - `scanner/reporter.py` — report generation.
  - `scanner/reame.md` — short usage examples (note: file name spelled `reame.md`).
- `examples/` — sample input files such as `repos.txt`.

**Development notes**
- Run the CLI from the project root so relative paths like `examples/repos.txt` resolve correctly.
- Use `--concurrency` to speed up large lists; adjust based on CPU/network.

**Troubleshooting**
- If you see permission errors, ensure your virtual environment is active and you have write access to the output path.
- For network or git errors, confirm `git` is installed and reachable from your PATH.

