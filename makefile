.PHONY: coverage docs help py test win-a linux-a

include development.env
export

help:
	@echo Dandy Makefile:

coverage:
	pip install coverage
	coverage run --data-file=.coverage/data/.coverage -m unittest discover -v ./tests
	coverage html --data-file=.coverage/data/.coverage -d .coverage/report

docs:
	mkdocs serve

py:
	python $(ARGS)

test:
	python -m unittest discover -v ./tests

win-a:
	cmd /C ".venv\Scripts\activate.bat"

linux-a:
	source .venv/bin/activate


