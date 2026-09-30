"""Auto-fix must preserve source bytes and existing recovery copies on failure."""
import stat
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import MethodenAnalyser3 as m


def prepare(monkeypatch, path, raw):
    path.write_bytes(raw)
    monkeypatch.setattr(m, "_last_analysis_path", str(path))
    monkeypatch.setattr(m, "_last_analysis_result", m.analyze_file(str(path)))
    dialogs = Mock()
    dialogs.askyesno.return_value = True
    monkeypatch.setattr(m, "messagebox", dialogs)
    return dialogs


def test_existing_backup_is_not_overwritten(monkeypatch, tmp_path):
    path = tmp_path / "source.py"
    raw = b"import os\nanswer = 42\n"
    dialogs = prepare(monkeypatch, path, raw)
    backup = path.with_suffix(".py.bak")
    backup.write_bytes(b"older recovery copy")
    m.auto_fix_unused_imports(Mock())
    dialogs.showerror.assert_not_called()
    assert path.read_text(encoding="utf-8") == "answer = 42\n"
    assert backup.read_bytes() == b"older recovery copy"
    assert path.with_suffix(".py.bak.1").read_bytes() == raw


@pytest.mark.parametrize("mode", [0o644, 0o444])
def test_publication_failure_preserves_original(monkeypatch, tmp_path, mode):
    path = tmp_path / "source.py"
    raw = b"import os\nanswer = 42\n"
    dialogs = prepare(monkeypatch, path, raw)
    path.chmod(mode)
    original_mode = stat.S_IMODE(path.stat().st_mode)
    def fail(*args):
        raise OSError("publication failed")
    monkeypatch.setattr(m.os, "replace", fail)
    m.auto_fix_unused_imports(Mock())
    assert path.read_bytes() == raw
    assert stat.S_IMODE(path.stat().st_mode) == original_mode
    assert dialogs.showerror.call_count == 1
    dialogs.showinfo.assert_not_called()
    assert not list(tmp_path.glob(".*.autofix-*"))
    path.chmod(0o644)


@pytest.mark.parametrize("newline", [b"\r\n", b"\n", b"\r"])
def test_backup_preserves_exact_newline_bytes(monkeypatch, tmp_path, newline):
    path = tmp_path / "source.py"
    raw = b"import os" + newline + b"answer = 42" + newline
    dialogs = prepare(monkeypatch, path, raw)
    m.auto_fix_unused_imports(Mock())
    dialogs.showerror.assert_not_called()
    assert path.with_suffix(".py.bak").read_bytes() == raw
    assert path.read_bytes() == b"answer = 42" + newline


@pytest.mark.parametrize("failure", ["partial", "fsync", "backup_link"])
def test_staging_failure_preserves_source_and_existing_backup(monkeypatch, tmp_path, failure):
    path = tmp_path / "source.py"
    raw = b"import os\nanswer = 42\n"
    dialogs = prepare(monkeypatch, path, raw)
    backup = path.with_suffix(".py.bak")
    backup.write_bytes(b"older backup")
    def fail(*args):
        raise OSError("injected failure")
    if failure == "partial":
        real_temp = m.tempfile.NamedTemporaryFile
        @contextmanager
        def partial_temp(*args, **kwargs):
            with real_temp(*args, **kwargs) as handle:
                yield SimpleNamespace(name=handle.name, flush=handle.flush, fileno=handle.fileno,
                                      write=lambda data: handle.write(data[:len(data) // 2]))
        monkeypatch.setattr(m.tempfile, "NamedTemporaryFile", partial_temp)
    elif failure == "fsync":
        monkeypatch.setattr(m.os, "fsync", fail)
    else:
        monkeypatch.setattr(m.os, "link", fail)
    m.auto_fix_unused_imports(Mock())
    assert path.read_bytes() == raw
    assert backup.read_bytes() == b"older backup"
    assert dialogs.showerror.call_count == 1
    dialogs.showinfo.assert_not_called()
    assert not list(tmp_path.glob(".*.autofix-*"))


def test_concurrently_created_backup_is_preserved(monkeypatch, tmp_path):
    path = tmp_path / "source.py"
    raw = b"import os\nanswer = 42\n"
    dialogs = prepare(monkeypatch, path, raw)
    real_link = m.os.link
    backup = path.with_suffix(".py.bak")
    def competing_link(source, target):
        if target == backup:
            backup.write_bytes(b"other writer")
        real_link(source, target)
    monkeypatch.setattr(m.os, "link", competing_link)
    m.auto_fix_unused_imports(Mock())
    dialogs.showerror.assert_not_called()
    assert backup.read_bytes() == b"other writer"
    assert path.with_suffix(".py.bak.1").read_bytes() == raw
    assert path.read_bytes() == b"answer = 42\n"


def test_detected_source_change_is_not_overwritten(monkeypatch, tmp_path):
    path = tmp_path / "source.py"
    raw = b"import os\nanswer = 42\n"
    newer = b"import os\nprint(os.getcwd())\n"
    dialogs = prepare(monkeypatch, path, raw)
    real_link = m.os.link
    def edit_during_backup(source, target):
        real_link(source, target)
        path.write_bytes(newer)
    monkeypatch.setattr(m.os, "link", edit_during_backup)
    m.auto_fix_unused_imports(Mock())
    assert path.read_bytes() == newer
    assert path.with_suffix(".py.bak").read_bytes() == raw
    assert dialogs.showerror.call_count == 1
    dialogs.showinfo.assert_not_called()
    assert not list(tmp_path.glob(".*.autofix-*"))


def test_success_preserves_file_mode(monkeypatch, tmp_path):
    path = tmp_path / "source.py"
    dialogs = prepare(monkeypatch, path, b"import os\nanswer = 42\n")
    path.chmod(0o755)
    original_mode = stat.S_IMODE(path.stat().st_mode)
    m.auto_fix_unused_imports(Mock())
    dialogs.showerror.assert_not_called()
    assert stat.S_IMODE(path.stat().st_mode) == original_mode


def test_removing_only_import_can_publish_empty_file(monkeypatch, tmp_path):
    path = tmp_path / "source.py"
    raw = b"import os\n"
    dialogs = prepare(monkeypatch, path, raw)
    m.auto_fix_unused_imports(Mock())
    dialogs.showerror.assert_not_called()
    assert path.read_bytes() == b""
    assert path.with_suffix(".py.bak").read_bytes() == raw


def test_mixed_newlines_preserve_untouched_bytes(monkeypatch, tmp_path):
    path = tmp_path / "source.py"
    raw = b"import os\r\nanswer = 42\nlabel = 'ok'\r"
    dialogs = prepare(monkeypatch, path, raw)
    m.auto_fix_unused_imports(Mock())
    dialogs.showerror.assert_not_called()
    assert path.read_bytes() == b"answer = 42\nlabel = 'ok'\r"
    assert path.with_suffix(".py.bak").read_bytes() == raw
