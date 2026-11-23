.PHONY: test run-spec clean

test:
	python -m unittest discover -s tests -v

run-spec:
	python -m src.cli examples/spec_tests.csv out.bin --test

clean:
	rm -f out.bin
	find . -name '__pycache__' -type d -exec rm -rf {} +