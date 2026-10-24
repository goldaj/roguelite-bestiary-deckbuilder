"""Regression tests for save-file corruption, import and deletion semantics."""
from __future__ import annotations

from pathlib import Path

from core.save_system import SaveData, SaveManager, SaveMetadata


def sample_save(manager: SaveManager, run_id: str = "run_original") -> SaveData:
    save = SaveData(
        metadata=SaveMetadata("1.0.0", "2026-10-24", run_id, 1, 0, 0, 0.0, ""),
        run_state={}, current_map={}, profile={"coins": 12}, settings={},
    )
    save.metadata.checksum = manager._calculate_checksum(save)
    return save


def test_import_recomputes_checksum_after_assigning_new_id(tmp_path: Path) -> None:
    manager = SaveManager(tmp_path / "saves")
    original = sample_save(manager)
    imported_path = tmp_path / "import.sav"
    manager._write_save_file(imported_path, original)

    new_id = manager.import_save(imported_path)
    assert new_id and new_id != original.metadata.run_id
    loaded = manager._read_save_file(manager.runs_dir / f"{new_id}.sav")
    assert loaded.metadata.run_id == new_id
    assert manager._verify_checksum(loaded)


def test_import_rejects_invalid_checksum(tmp_path: Path) -> None:
    manager = SaveManager(tmp_path / "saves")
    original = sample_save(manager)
    original.profile["coins"] = 999
    source = tmp_path / "tampered.sav"
    manager._write_save_file(source, original)

    assert manager.import_save(source) is None
    assert not list(manager.runs_dir.glob("*.sav"))


def test_restore_ignores_deleted_backups_and_corruption(tmp_path: Path) -> None:
    manager = SaveManager(tmp_path / "saves")
    original = sample_save(manager)
    manager._write_save_file(manager.backup_dir / "deleted_run_original_1.bak", original)
    assert manager._restore_from_backup("run_original") is None

    tampered = sample_save(manager)
    tampered.profile["coins"] = 999
    manager._write_save_file(manager.backup_dir / "run_original_2.bak", tampered)
    assert manager._restore_from_backup("run_original") is None

    manager._write_save_file(manager.backup_dir / "run_original_3.bak", original)
    assert manager._restore_from_backup("run_original") is not None
