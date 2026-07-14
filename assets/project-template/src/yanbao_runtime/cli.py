from __future__ import annotations

import argparse
import json
import sqlite3
import time
from pathlib import Path

from .store import StateStore


ARM_CONFIRMATION = "ARM-YANBAO"
DISARM_CONFIRMATION = "DISARM-YANBAO"


def _paths(root: Path) -> tuple[Path, Path]:
    return root / "data" / "state.sqlite3", root / "config.json"


def _store(root: Path) -> StateStore:
    database, _ = _paths(root)
    store = StateStore(database)
    store.initialize()
    return store


def _write_json(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="yanbao-runtime")
    parser.add_argument("--project-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init")
    sub.add_parser("status")
    sub.add_parser("inspect")
    sub.add_parser("backup")

    restore = sub.add_parser("restore-check")
    restore.add_argument("path")

    arm = sub.add_parser("arm")
    arm.add_argument("--confirm", required=True)

    disarm = sub.add_parser("disarm")
    disarm.add_argument("--confirm", required=True)

    sub.add_parser("run")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.project_root).resolve()
    database, config = _paths(root)

    if args.command == "init":
        root.mkdir(parents=True, exist_ok=True)
        store = _store(root)
        config.write_text(
            json.dumps(
                {
                    "version": 2,
                    "model_adapter": "unconfigured",
                    "life_adapter": "unconfigured",
                    "channel_adapter": "unconfigured",
                    "life_enabled": False,
                    "external_stimuli_enabled": False,
                    "daily_wake_opportunities": 2,
                    "max_proactive_per_day": 2,
                    "media_enabled": False,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        result = {"initialized": True, "armed": store.is_armed(), "database_integrity": store.integrity()}
        store.close()
        _write_json(result)
        return 0

    if args.command == "restore-check":
        check = StateStore(Path(args.path))
        result = {"database_integrity": check.integrity() == "ok"}
        check.close()
        _write_json(result)
        return 0

    store = _store(root)
    try:
        if args.command == "status":
            _write_json(
                {
                    "initialized": config.is_file(),
                    "armed": store.is_armed(),
                    "database_integrity": store.integrity() == "ok",
                }
            )
            return 0
        if args.command == "inspect":
            _write_json({"armed": store.is_armed(), "counts": store.counts()})
            return 0
        if args.command == "backup":
            target = root / "data" / "backups" / f"state-{int(time.time())}.sqlite3"
            store.backup(target)
            _write_json({"backup_created": True, "database_integrity": True})
            return 0
        if args.command == "arm":
            if args.confirm != ARM_CONFIRMATION:
                raise SystemExit("exact confirmation ARM-YANBAO required")
            store.set_armed(True)
            _write_json({"armed": True})
            return 0
        if args.command == "disarm":
            if args.confirm != DISARM_CONFIRMATION:
                raise SystemExit("exact confirmation DISARM-YANBAO required")
            store.set_armed(False)
            _write_json({"armed": False})
            return 0
        if args.command == "run":
            raise SystemExit("real model and channel adapters are not configured")
    finally:
        store.close()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
