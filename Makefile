.PHONY: test

test:
	python -m pytest -q

# Example: make inspect PDF=input/book.pdf
inspect:
	bio2word inspect "$(PDF)" --pages 7,8,10,14,16 --report runs/preflight.json
