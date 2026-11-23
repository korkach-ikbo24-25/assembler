.PHONY: test gen-examples run-vectors run-vector-basic clean

gen-examples:
	python tools/make_examples.py

run-vector-basic: gen-examples
	python -m src.cli examples/vector_basic.csv out_vec.bin --test
	python -m src.interpreter out_vec.bin dump_vec.json --start 0 --end 6

run-vectors: gen-examples
	@for f in examples/vector_*.csv ; do \
		bin=$${f%.csv}.bin ; dump=$${f%.csv}.json ; \
		python -m src.cli "$$f" "$$bin" ; \
		python -m src.interpreter "$$bin" "$$dump" --start 0 --end 6 ; \
		echo "-- $$f --" ; cat "$$dump" ; \
	done

clean:
	rm -f out*.bin dump*.json examples/*.bin examples/*.json
	find . -name '__pycache__' -type d -exec rm -rf {} +