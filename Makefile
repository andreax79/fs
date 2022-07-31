SHELL=/bin/bash -e

help:
	@echo "- make coverage     Run test coverage"
	@echo "- make test         Run tests"
	@echo "- make lint         Run lint"
	@echo "- make black        Format code"
	@echo "- make clean        Clean"
	@echo "- make venv         Create virtual environment"
	@echo "- make tag          Create version tag"

coverage:
	@coverage run --source=fs/gitfs -m pytest && python3 -m coverage report -m

test:
	@pytest

lint:
	@flake8 fs/gitfs

black:
	@black fs setup.py tests

tag:
	@git tag "v$$(cat fs/gitfs/VERSION)"

clean:
	-rm -rf build dist
	-rm -rf *.egg-info
	-rm -rf bin lib share pyvenv.cfg

venv:
	python3 -m virtualenv .
	. bin/activate; pip install -Ur requirements.txt
	. bin/activate; pip install -Ur requirements-dev.txt
