"""Import cleanup must recheck the current source after confirmation."""
from unittest.mock import Mock

import pytest

import MethodenAnalyser3 as m


def prepare(monkeypatch, path, old_source, current_source):
    path.write_text(old_source, encoding="utf-8")
    result = m.analyze_file(str(path))
    monkeypatch.setattr(m, "_last_analysis_path", str(path))
    monkeypatch.setattr(m, "_last_analysis_result", result)
    dialogs = Mock()

    def confirm(*args):
        # A file may change while the previous findings are being confirmed.
        path.write_text(current_source, encoding="utf-8")
        return True

    dialogs.askyesno.side_effect = confirm
    monkeypatch.setattr(m, "messagebox", dialogs)
    return dialogs


@pytest.mark.parametrize("usage", [
    "print(os.getcwd())\n",
    '__all__ = ["os"]\n',
    'def f() -> "os.PathLike":\n    pass\n',
])
def test_newly_used_import_is_preserved(monkeypatch, tmp_path, usage):
    path = tmp_path / "source.py"
    current = "import os\n" + usage
    dialogs = prepare(monkeypatch, path, "import os\nx = 1\n", current)
    m.auto_fix_unused_imports(Mock())
    assert path.read_text(encoding="utf-8") == current
    assert not path.with_suffix(".py.bak").exists()
    dialogs.showerror.assert_not_called()


def test_new_unused_import_is_not_silently_added_to_approved_fix(monkeypatch, tmp_path):
    path = tmp_path / "source.py"
    old = "import os\nimport sys\nprint(sys.argv)\n"
    current = "import os\nimport sys\nprint(os.getcwd())\n"
    dialogs = prepare(monkeypatch, path, old, current)
    m.auto_fix_unused_imports(Mock())
    assert path.read_text(encoding="utf-8") == current
    assert not path.with_suffix(".py.bak").exists()
    dialogs.showerror.assert_not_called()


def test_only_still_unused_approved_import_is_removed(monkeypatch, tmp_path):
    path = tmp_path / "source.py"
    old = "import os\nimport sys\nx = 1\n"
    current = "import os\nimport sys\nprint(os.getcwd())\n"
    dialogs = prepare(monkeypatch, path, old, current)
    m.auto_fix_unused_imports(Mock())
    assert path.read_text(encoding="utf-8") == "import os\nprint(os.getcwd())\n"
    assert path.with_suffix(".py.bak").read_text(encoding="utf-8") == current
    dialogs.showerror.assert_not_called()
