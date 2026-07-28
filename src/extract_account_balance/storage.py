import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any


def get_user_data_dir() -> Path:
    home = Path.home()
    if os.name == "nt":
        app_dir = home / "AppData" / "Local" / "AccountBalanceViewer"
    else:
        app_dir = home / ".account_balance_viewer"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_history_path() -> Path:
    return get_user_data_dir() / "statement_history.json"


def get_backup_dir() -> Path:
    backup_dir = get_user_data_dir() / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def get_activity_log_path() -> Path:
    return get_user_data_dir() / "activity.log"


def get_imported_dir() -> Path:
    imported_dir = get_user_data_dir() / "Imported"
    imported_dir.mkdir(parents=True, exist_ok=True)
    return imported_dir


def save_records(records: List[Dict[str, float | str]], path: str | Path | None = None) -> Path:
    if path is None:
        path = Path("records.json")
    output_path = Path(path)
    output_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return output_path


def load_records(path: str | Path | None = None) -> List[Dict[str, float | str]]:
    if path is None:
        path = Path("records.json")
    data_path = Path(path)
    if not data_path.exists():
        return []
    return json.loads(data_path.read_text(encoding="utf-8"))


def save_statement_history(
    history: List[Dict[str, Any]],
    path: str | Path | None = None,
    backup_path: str | Path | None = None,
    log_path: str | Path | None = None,
) -> Path:
    if path is None:
        path = get_history_path()
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(history, indent=2), encoding="utf-8")

    if backup_path is None:
        backup_path = get_backup_dir() / output_path.name
    backup_target = Path(backup_path)
    backup_target.parent.mkdir(parents=True, exist_ok=True)
    backup_target.write_text(json.dumps(history, indent=2), encoding="utf-8")

    if log_path is None:
        log_path = get_activity_log_path()
    log_target = Path(log_path)
    log_target.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with log_target.open("a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] Saved statement history to {output_path} (backup: {backup_target})\n")

    return output_path


def load_statement_history(path: str | Path | None = None) -> List[Dict[str, Any]]:
    if path is None:
        path = get_history_path()
    data_path = Path(path)
    if not data_path.exists():
        return []
    return json.loads(data_path.read_text(encoding="utf-8"))


def copy_imported_pdf(source_path: str | Path) -> Path:
    source = Path(source_path)
    if not source.exists():
        raise FileNotFoundError(f"Source PDF does not exist: {source}")

    target_dir = get_imported_dir()
    target_path = target_dir / source.name
    target_path.write_bytes(source.read_bytes())
    return target_path


def append_activity_log(message: str, log_path: str | Path | None = None) -> Path:
    if log_path is None:
        log_path = get_activity_log_path()
    log_target = Path(log_path)
    log_target.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with log_target.open("a", encoding="utf-8") as handle:
        handle.write(f"[{timestamp}] {message}\n")
    return log_target


def upsert_statement(
    history: List[Dict[str, Any]],
    filename: str,
    description: str,
    records: List[Dict[str, Any]],
    year: int | None = None,
) -> List[Dict[str, Any]]:
    normalized_records = []
    seen = set()
    for record in records:
        record_copy = dict(record)
        record_copy.setdefault("filename", filename)
        record_copy.setdefault("description", description)
        record_copy["filename"] = filename
        record_copy["description"] = description
        key = (record_copy.get("date"), record_copy.get("balance"))
        if key not in seen:
            seen.add(key)
            normalized_records.append(record_copy)

    for entry in history:
        entry_filename = str(entry.get("filename", ""))
        entry_description = str(entry.get("description", ""))
        same_statement = (
            entry_filename.lower() == filename.lower()
            or entry_description.lower() == description.lower()
            or entry_filename.lower().split(".")[0] == filename.lower().split(".")[0]
        )
        if same_statement and entry.get("records"):
            entry["records"] = normalized_records
            entry["filename"] = filename
            entry["description"] = description
            if year is not None:
                entry["year"] = year
            return history

    entry = {
        "filename": filename,
        "description": description,
        "records": normalized_records,
    }
    if year is not None:
        entry["year"] = year
    history.append(entry)
    return history
