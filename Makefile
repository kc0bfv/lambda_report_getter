SRC := report_getter/report_getter.py
OUT_ZIP := report_getter.zip

${OUT_ZIP}: ${SRC}
	zip -j -u "$@" "$<"

test:
	python3 -m unittest "${SRC}"
