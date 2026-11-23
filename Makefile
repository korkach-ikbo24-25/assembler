.PHONY: test run-spec run-vm clean

test:
	python -m unittest discover -s tests -v

run-spec:
	python -m src.cli examples/spec_tests.csv out.bin --test

run-vm: run-copy
	python -m src.interpreter out_copy.bin dump.json --start 0 --end 16

run-copy:
	python -m src.cli examples/copy_array.csv out_copy.bin

clean:
	rm -f out*.bin dump*.json
	find . -name '__pycache__' -type d -exec rm -rf {} +