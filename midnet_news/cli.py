from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .orchestrator import produce


def main(argv=None):
    root = Path.cwd()
    parser = argparse.ArgumentParser(prog="midnet", description="Create an auditable MidNet News draft production package.")
    parser.add_argument("--version", action="version", version=f"midnet {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("produce", help="Run input validation, subtitles, graphics, render, QC and packaging.")
    run.add_argument("--input", type=Path, default=root / "input", help="Input package directory (default: ./input)")
    run.add_argument("--output", type=Path, default=root / "production", help="Final output directory (default: ./production)")
    run.add_argument("--repo", type=Path, default=root, help="Project root containing config and brand assets")
    run.add_argument("--config", type=Path, default=root / "config/production.json")
    run.add_argument("--asr-model", default="small", help="faster-whisper model name (default: small)")
    args = parser.parse_args(argv)
    try:
        if args.command == "produce":
            report = produce(args.input, args.output, args.repo, args.config, args.asr_model)
            print(json.dumps({"status": report["status"], "output": str(args.output.resolve()),
                              "report": str((args.output / "productionReport.json").resolve()),
                              "drafts": str((args.repo / "workspace/drafts").resolve())}, indent=2))
            return 0 if report["status"] == "PASS" else 2
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(f"midnet: error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
