"""Text accuracy benchmarks only: no copyrighted source pages in CI."""
import json
import pytest
from bio_book_chat_test.ocr_benchmark import compare_ocr_json
from bio_book_chat_test.cli import main


def sample(tmp_path, text="إنزيم (DNA) يُحلِّل الأحماض"):
    truth = {"source_pdf_sha256": "f" * 64, "pages": [
        {"source_page": 41, "text": text,
         "verified_from_image": True, "reviewer": "synthetic-test",
         "source_image_ref": "SYNTHETIC.png"}]}
    candidate = {"engine": "synthetic", "version": "0.0-test",
                 "pages": [{"source_page": 41, "text": text}]}
    ref, out = tmp_path / "ref.json", tmp_path / "candidate.json"
    ref.write_text(json.dumps(truth, ensure_ascii=False), encoding="utf-8")
    out.write_text(json.dumps(candidate, ensure_ascii=False), encoding="utf-8")
    return ref, out, truth, candidate


def test_exact_arabic_hamza_and_latin_equal(tmp_path):
    ref, out, _, _ = sample(tmp_path)
    score = compare_ocr_json(ref, out)
    assert score["micro_cer"] == 0
    assert score["micro_wer"] == 0
    assert score["approved"] is False


def test_arabic_hamza_is_not_silently_normalized(tmp_path):
    ref, out, _, candidate = sample(tmp_path, "إنزيم")
    candidate["pages"][0]["text"] = "انزيم"
    out.write_text(json.dumps(candidate, ensure_ascii=False), encoding="utf-8")
    score = compare_ocr_json(ref, out)
    assert score["micro_cer"] > 0
    assert score["micro_wer"] > 0
    assert not score["per_page"][0]["exact_text_match"]


def test_latin_mixed_term_omission_detected(tmp_path):
    ref, out, _, candidate = sample(tmp_path)
    candidate["pages"][0]["text"] = "إنزيم يُحلِّل الأحماض"
    out.write_text(json.dumps(candidate, ensure_ascii=False), encoding="utf-8")
    assert compare_ocr_json(ref, out)["micro_cer"] > 0


def test_rejects_unreviewed_reference(tmp_path):
    ref, out, truth, _ = sample(tmp_path)
    truth["pages"][0]["verified_from_image"] = False
    ref.write_text(json.dumps(truth, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="no independently verified"):
        compare_ocr_json(ref, out)


def test_missing_page_scores_as_total_omission(tmp_path):
    ref, out, truth, candidate = sample(tmp_path, "النبات")
    truth["pages"].append({"source_page": 42, "text": "الخلية",
         "verified_from_image": True, "reviewer": "synthetic-test",
         "source_image_ref": "SYNTHETIC42.png"})
    ref.write_text(json.dumps(truth, ensure_ascii=False), encoding="utf-8")
    score = compare_ocr_json(ref, out)
    assert score["missing_pages"] == [42]
    assert score["per_page"][1]["cer"] == 1


def test_cli_benchmark_saves_separate_scorecard(tmp_path):
    ref, out, _, _ = sample(tmp_path)
    report = tmp_path / "bench.json"
    assert main(["benchmark-ocr", str(ref), str(out), "--report", str(report)]) == 0
    assert json.loads(report.read_text(encoding="utf-8"))["docx_editability"] == "NOT_EVALUATED_BY_TEXT_BENCHMARK"
