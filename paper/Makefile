SHELL := /bin/sh

MANUSCRIPT := manuscript/main.tex
BUILD_DIR := build
OUTPUT := $(BUILD_DIR)/manuscript.pdf

.PHONY: all audit archive clean

all: $(OUTPUT) audit

audit: $(OUTPUT)
	cd .. && python3 scripts/audit_pdf.py --pdf paper/$(OUTPUT) --log paper/$(BUILD_DIR)/main.log

archive:
	cd .. && python3 scripts/build_release.py

$(OUTPUT): $(MANUSCRIPT) $(shell find manuscript -type f -name '*.tex')
	@command -v tectonic >/dev/null 2>&1 || { echo "tectonic is required"; exit 1; }
	@mkdir -p $(BUILD_DIR)
	cd manuscript && tectonic --keep-logs --outdir ../$(BUILD_DIR) main.tex
	mv $(BUILD_DIR)/main.pdf $(OUTPUT)

clean:
	rm -f $(BUILD_DIR)/main.aux $(BUILD_DIR)/main.log $(BUILD_DIR)/main.out $(OUTPUT)
