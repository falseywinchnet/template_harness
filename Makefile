.PHONY: help test doctor report paper formal clean

help:
	@echo "make test    - run the fast harness gates"
	@echo "make report  - refresh STATUS.md and NEXT.md"
	@echo "make paper   - build the optional manuscript PDF"
	@echo "make formal  - build the optional Lean project"

test:
	./h check
	./h doctor

doctor:
	./h doctor

report:
	./h report --write

paper:
	$(MAKE) -C paper

formal:
	cd formal && lake build

clean:
	$(MAKE) -C paper clean
