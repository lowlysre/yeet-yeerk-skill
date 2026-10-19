"""Eval harness for yeet-yeerk.

Runs each case twice via `copilot -p` (baseline vs. skill text prepended) and
scores prose for first-person pronouns, filler, apologies, and feelings.
Usage: python run_evals.py [--model MODEL] [--mode baseline|skill|both]
"""
import argparse
import json
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

def find_copilot() -> str:
    for d in os.environ["PATH"].split(os.pathsep):
        p = Path(d) / "copilot.ps1"
        if p.exists():
            return str(p)
    raise SystemExit("copilot.ps1 not found on PATH")


COPILOT = find_copilot()
HERE = Path(__file__).parent
SKILL = (HERE.parent / "skills" / "yeet-yeerk" / "SKILL.md").read_text(encoding="utf-8")

CHECKS = {
    "first_person": re.compile(r"\b(I(?!/O)|I'm|I'll|I've|I'd|me|my|mine|myself|we|we'll|we're|our|us|let's)\b", re.I),
    "filler": re.compile(r"\b(happy to help|let me|great question|sure[,!]|certainly[,!]|of course[,!]|glad to|hope this helps|feel free)\b", re.I),
    "apology": re.compile(r"\b(sorry|apologi[sz]e|apologies|unfortunately)\b", re.I),
    "feelings": re.compile(r"\b(excited|delighted|love to|enjoy|thrilled|appreciate)\b", re.I),
}


def prose(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`]*`", "", text)


def score(text: str) -> dict:
    p = prose(text)
    return {k: [m.group(0) for m in rx.finditer(p)] for k, rx in CHECKS.items()}


def ask(prompt: str, model: str) -> str:
    # copilot is a .ps1 shim on Windows; the prompt goes via stdin-free -p arg
    cmd = ["pwsh", "-NoProfile", "-File", COPILOT, "-p", prompt, "-s", "--model", model,
           "--no-custom-instructions", "--disable-builtin-mcps"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"copilot exited {r.returncode}: {r.stderr[:300]}")
    return r.stdout.strip()


def build(case: dict, mode: str) -> str:
    if mode == "baseline":
        return case["prompt"]
    return f"Apply this skill to every response:\n\n{SKILL}\n\n---\n\n{case['prompt']}"


def run(case: dict, mode: str, model: str) -> dict:
    out = ask(build(case, mode), model)
    s = score(out)
    return {"id": case["id"], "mode": mode, "pass": bool(out) and not any(s.values()), "violations": s, "output": out}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-haiku-4.5")
    ap.add_argument("--mode", default="both", choices=["baseline", "skill", "both"])
    a = ap.parse_args()
    cases = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    modes = ["baseline", "skill"] if a.mode == "both" else [a.mode]
    jobs = [(c, m) for m in modes for c in cases]
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(lambda j: run(j[0], j[1], a.model), jobs))
    (HERE / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    for m in modes:
        rs = [r for r in results if r["mode"] == m]
        print(f"\n== {m}: {sum(r['pass'] for r in rs)}/{len(rs)} passed")
        for r in rs:
            hits = {k: v for k, v in r["violations"].items() if v}
            print(f"  {'PASS' if r['pass'] else 'FAIL'} {r['id']} {hits if hits else ''}")


if __name__ == "__main__":
    main()
