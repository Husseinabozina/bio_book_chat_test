"""Command line entrypoint for inspect -> convert -> audit workflow."""
import argparse
import json
from pathlib import Path
import sys

from .analysis import inspect_pdf
from .conversion import convert_pdf
from .quality import audit_docx
from .reviewed import render_reviewed_manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="bio2word", description="Arabic PDF-to-Word engineering lab")
    cmd = parser.add_subparsers(dest="action", required=True)
    inspect = cmd.add_parser("inspect", help="Analyze source PDF and extraction reliability")
    inspect.add_argument("pdf")
    inspect.add_argument("--pages", help="One-based numbers/ranges, e.g. 7,8,10,14,16")
    inspect.add_argument("--report", help="Save JSON report")
    convert = cmd.add_parser("convert", help="Create DOCX with explicitly declared fidelity mode")
    convert.add_argument("pdf")
    convert.add_argument("output")
    convert.add_argument("--pages")
    convert.add_argument("--mode", default="hybrid", choices=["visual", "editable", "hybrid"])
    convert.add_argument("--dpi", type=int, default=150)
    convert.add_argument("--allow-suspect-text", action="store_true", help="Unsafe override: known damaged font mapping may be copied")
    convert.add_argument("--report")
    reviewed = cmd.add_parser("reviewed", help="Build editable DOCX from a page-by-page source-verified manifest")
    reviewed.add_argument("manifest", help="JSON manifest whose texts were checked against source page images")
    reviewed.add_argument("output", help="Destination DOCX")
    reviewed.add_argument("--report", help="JSON report path")
    audit = cmd.add_parser("audit", help="Audit DOCX and optionally render with LibreOffice")
    audit.add_argument("docx")
    audit.add_argument("--source", help="Source PDF")
    audit.add_argument("--pages")
    audit.add_argument("--render", action="store_true")
    audit.add_argument("--report")
    args = parser.parse_args(argv)
    try:
        if args.action == "inspect":
            result = inspect_pdf(args.pdf, args.pages)
        elif args.action == "convert":
            result = convert_pdf(args.pdf, args.output, pages=args.pages, mode=args.mode,
                                 dpi=args.dpi, allow_suspect_text=args.allow_suspect_text)
        elif args.action == "reviewed":
            result = render_reviewed_manifest(args.manifest, args.output)
        else:
            result = audit_docx(args.docx, original_pdf=args.source, pages=args.pages, render=args.render)
        payload = json.dumps(result, ensure_ascii=False, indent=2)
        print(payload)
        if args.report:
            Path(args.report).parent.mkdir(parents=True, exist_ok=True)
            Path(args.report).write_text(payload+"\n", encoding="utf-8")
        return 0
    except (ValueError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
