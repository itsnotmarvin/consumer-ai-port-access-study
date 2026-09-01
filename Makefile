.PHONY: verify serve-report

PYTHON ?= python3
REPORT_PORT ?= 8000

# Read-only verification of the preserved collection, review, analysis, and report chain.
verify:
	$(PYTHON) tools/verify_archive.py

# Serve only the self-contained report directory on the local loopback interface.
serve-report:
	@test -f report/report.html || { echo "report/report.html is missing" >&2; exit 1; }
	@echo "Serving the archived report at http://127.0.0.1:$(REPORT_PORT)/report.html"
	$(PYTHON) -m http.server $(REPORT_PORT) --bind 127.0.0.1 --directory report
