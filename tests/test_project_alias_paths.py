"""Reports must keep paths relative when scanning through a directory alias."""
import os
import subprocess

import MethodenAnalyser3 as m


def test_project_directory_alias_keeps_report_paths_relative(tmp_path):
    target = tmp_path / "physical-project"
    target.mkdir()
    (target / "good.py").write_text("import os\nanswer = 42\n", encoding="utf-8")
    (target / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    alias = tmp_path / "project-alias"
    if os.name == "nt":
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(target)],
                                capture_output=True, check=False)
        assert result.returncode == 0, result.stderr
    else:
        alias.symlink_to(target, target_is_directory=True)
    result = m.analyze_project(str(alias))
    report = m.build_json_report("project", result)
    assert [entry["path"] for entry in report["files"]] == ["good.py"]
    assert [entry["path"] for entry in report["errors"]] == ["broken.py"]
    assert report["unused_imports"] == {"good.py": ["os"]}
    text = m.generate_project_report(result)
    assert ".." not in text
    assert str(target) not in text
