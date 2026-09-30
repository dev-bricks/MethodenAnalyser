"""Import cleanup must preserve neighboring statements and valid suites."""
import ast
from unittest.mock import Mock

import pytest

import MethodenAnalyser3 as m


@pytest.mark.parametrize("source", [
    "import os; answer = 42\n",
    "answer = 42; import os\n",
    "if True: import os; answer = 42\n",
    "if True:\n    import os\nanswer = 42\n",
    "def f():\n    import os\nanswer = 42\n",
    "label = 'Grüße'; import os; answer = 42\n",
    "from os import (\n    path,\n); answer = 42\n",
    "import os; import sys; answer = 42\n",
])
def test_auto_fix_preserves_code_and_parseability(monkeypatch, tmp_path, source):
    path = tmp_path / "source.py"
    path.write_text(source, encoding="utf-8")
    monkeypatch.setattr(m, "_last_analysis_path", str(path))
    monkeypatch.setattr(m, "_last_analysis_result", m.analyze_file(str(path)))
    dialogs = Mock()
    dialogs.askyesno.return_value = True
    monkeypatch.setattr(m, "messagebox", dialogs)
    m.auto_fix_unused_imports(Mock())
    dialogs.showerror.assert_not_called()
    fixed = path.read_text(encoding="utf-8")
    tree = ast.parse(fixed)
    assert not any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(tree))
    namespace = {}
    exec(compile(tree, str(path), "exec"), namespace)  # noqa: S102 -- fixed test fixtures only
    assert namespace["answer"] == 42
    if "label" in source:
        assert namespace["label"] == "Grüße"
    if "def f" in source:
        assert namespace["f"]() is None
    assert path.with_suffix(".py.bak").read_text(encoding="utf-8") == source
