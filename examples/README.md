# Safe local experiment

Keep uploaded/scanned textbooks in local ignored `input/` only. The project CI generates its own synthetic PDF; it never needs copyrighted study materials. Run `bio2word inspect input/book.pdf --pages 7,8,10,14,16 --report runs/preflight.json` then read the JSON before conversion. Try `visual`, `editable`, `hybrid` separately and compare their limits as explained in `/docs/EXPERIMENTS.md`.
