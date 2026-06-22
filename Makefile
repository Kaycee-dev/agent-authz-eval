PYTHON ?= python

.PHONY: writeup-pdf
writeup-pdf:
	$(PYTHON) scripts/build_writeup_pdf.py
