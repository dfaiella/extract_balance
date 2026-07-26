import json
from pathlib import Path

from extract_account_balance.storage import load_statement_history, save_statement_history, upsert_statement


def test_upsert_statement_deduplicates_records(tmp_path: Path):
    history = []
    record = {"date": "2024-01-01", "balance": 100.0, "filename": "statement.pdf", "description": "June 2024"}

    history = upsert_statement(history, "statement.pdf", "June 2024", [record])
    history = upsert_statement(history, "statement.pdf", "June 2024", [record])

    assert len(history) == 1
    assert len(history[0]["records"]) == 1
    assert history[0]["records"][0]["filename"] == "statement.pdf"
    assert history[0]["description"] == "June 2024"


def test_save_and_load_statement_history(tmp_path: Path):
    path = tmp_path / "records.json"
    history = [{"filename": "statement.pdf", "description": "June 2024", "records": [{"date": "2024-01-01", "balance": 100.0, "filename": "statement.pdf", "description": "June 2024"}]}]

    save_statement_history(history, path)
    loaded = load_statement_history(path)

    assert loaded == history


def test_save_statement_history_creates_backup_and_log(tmp_path: Path):
    history = [{"filename": "statement.pdf", "description": "June 2024", "records": [{"date": "2024-01-01", "balance": 100.0, "filename": "statement.pdf", "description": "June 2024"}]}]
    history_path = tmp_path / "statement_history.json"
    backup_path = tmp_path / "backups" / "statement_history.json"
    log_path = tmp_path / "activity.log"

    save_statement_history(history, history_path, backup_path=backup_path, log_path=log_path)

    assert history_path.exists()
    assert backup_path.exists()
    assert log_path.exists()
    assert json.loads(backup_path.read_text(encoding="utf-8")) == history
    assert "Saved statement history" in log_path.read_text(encoding="utf-8")


def test_upsert_statement_updates_existing_entry_for_same_statement():
    history = []
    first_records = [{"date": "2024-01-01", "balance": 100.0}]
    second_records = [{"date": "2024-01-01", "balance": 100.0}]

    history = upsert_statement(history, "statement.pdf", "June 2024", first_records)
    history = upsert_statement(history, "statement.pdf", "June 2024", second_records)

    assert len(history) == 1
    assert len(history[0]["records"]) == 1
    assert history[0]["records"][0]["date"] == "2024-01-01"
