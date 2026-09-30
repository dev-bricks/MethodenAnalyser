"""UTF-8 BOM is a valid Python signature and must survive import cleanup."""
import codecs
import json
import subprocess
import sys
import warnings
from pathlib import Path
from unittest.mock import Mock

import pytest

import MethodenAnalyser3 as m


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
def test_analysis_accepts_utf8_bom_without_fallback(tmp_path, newline):
    path = tmp_path / "signed.py"
    source = newline.join(["import os", "label = 'Grüße'", "print(label)", ""])
    path.write_bytes(source.encode("utf-8-sig"))
    with warnings.catch_warnings(record=True) as caught:
        result = m.analyze_file(str(path))
    assert not caught
    assert result.unused_imports == ["os"]


@pytest.mark.parametrize("source,expected", [
    ("import os\r\nanswer = 42\r\n", "answer = 42\r\n"),
    ("label = 'Grüße'; import os; answer = 42\n", "label = 'Grüße'; pass; answer = 42\n"),
    ("import os\n", ""),
])
def test_auto_fix_preserves_bom_and_exact_backup(monkeypatch, tmp_path, source, expected):
    path = tmp_path / "signed.py"
    raw = source.encode("utf-8-sig")
    path.write_bytes(raw)
    monkeypatch.setattr(m, "_last_analysis_path", str(path))
    monkeypatch.setattr(m, "_last_analysis_result", m.analyze_source(source))
    dialogs = Mock()
    dialogs.askyesno.return_value = True
    monkeypatch.setattr(m, "messagebox", dialogs)
    m.auto_fix_unused_imports(Mock())
    dialogs.showerror.assert_not_called()
    assert path.read_bytes() == expected.encode("utf-8-sig")
    assert path.read_bytes().startswith(codecs.BOM_UTF8)
    assert path.with_suffix(".py.bak").read_bytes() == raw
    assert not list(tmp_path.glob(".*.autofix-*"))


def test_cli_reports_bom_file_findings(tmp_path):
    path = tmp_path / "signed.py"
    path.write_bytes("import os\nprint('Grüße')\n".encode("utf-8-sig"))
    report = tmp_path / "report.json"
    script = Path(m.__file__).resolve()
    result = subprocess.run([sys.executable, str(script), "--lang", "de", "--file", str(path),
                             "--json-output", str(report)], capture_output=True, check=False)
    assert result.returncode == m.EXIT_FINDINGS, result.stderr
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["unused_imports"] == {"signed.py": ["os"]}
