.PHONY: clean

VERSION = 1.1.0
DIST_PATH = ./dist
PYTHON_BIN = python3.13
VENV_PATH = ./venv
VENV = . $(VENV_PATH)/bin/activate;

SRC := \
	$(wildcard dohome_api/*/*.py) \
	$(wildcard dohome_api/*.py)

.PHONY: publish
publish: clean build
	$(VENV) python3 -m twine upload --repository pypi dist/*
	git add Makefile
	git commit -m "chore: release v$(VERSION)"
	git tag "v$(VERSION)"
	git push
	git push --tags

.PHONY: clean
clean:
	rm -rf *.egg-info
	rm -rf build
	rm -rf dist

.PHONY: build
build:
	echo "$(VERSION)" > .version
	$(VENV) python -m build

.PHONY: install
install:
	$(VENV) pip install .
	$(VENV) pipx install .

.PHONY: lint
lint:
	$(VENV) ruff check dohome
	$(VENV) pylint dohome

.PHONY: test
test:
	$(VENV) pytest -o log_cli=true -vv tests/*.py

.PHONY: configure
configure:
	rm -rf $(VENV_PATH)
	$(PYTHON_BIN) -m venv $(VENV_PATH)
	$(VENV) pip install -r requirements.txt
