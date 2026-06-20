from __future__ import annotations

from agent_authz_eval.report import main


def test_report_all_verifies_committed_artifacts(capsys):
    exit_code = main(["all"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "report all: PASS" in output
    assert "- consolidated_csv: PASS" in output
    assert "- findings_json: PASS" in output
    assert "- figures_data: PASS" in output
