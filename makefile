.PHONY: docs help py test win-a linux-a

include development.env
export

help:
	@echo Available commands:
	@echo - test: Run unit tests
	@echo - win-a: Activate virtual environment on Windows
	@echo - linux-a: Activate virtual environment on Linux
	@echo - py: Run Python with arguments
	@echo - help: Display this help message

docs:
	@mkdocs serve

py:
	python $(ARGS)

test:
	python -m unittest discover -v ./tests

win-a:
	cmd /C ".venv\Scripts\activate.bat"

linux-a:
	source .venv/bin/activate


