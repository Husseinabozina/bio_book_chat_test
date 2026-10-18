"""Do not lose adopted engineering decisions when changing the converter."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def test_all_19_engineering_decisions_are_recorded():
    doc = (ROOT / "docs/ENGINEERING_DECISIONS.md").read_text(encoding="utf-8")
    for n in range(1, 20):
        assert f"ADR-{n:02d}" in doc
    assert "Not yet implemented" in doc
    assert "VERIFIED IN WORD" in doc


def test_mandatory_policy_and_release_cli_are_wired():
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    cli = (ROOT / "src/bio_book_chat_test/cli.py").read_text(encoding="utf-8")
    assert "docs/ENGINEERING_DECISIONS.md" in agents
    assert "release-check" in agents
    assert 'cmd.add_parser("release-check"' in cli
    assert 'result["decision"] == "BLOCKED"' in cli


def test_evidence_template_is_explicitly_unapproved():
    spec = json.loads((ROOT / "docs/RELEASE_EVIDENCE_TEMPLATE.json").read_text(encoding="utf-8"))
    assert spec["schema_version"] == 1
    assert spec["reviews"]["source_text"]["status"] == "pending"
    assert spec["word_compatibility"]["result"] == "not_tested"
