export PATH   := $(CURDIR)/venv/bin:$(PATH)
export PS4    := \e[0m\e[32m==> \e[0m
export LC_ALL := C
MAKEFLAGS     += --warn-undefined-variables
MAKEFLAGS     += --no-builtin-rules
SHELL         := bash
.SHELLFLAGS   := -euxo pipefail -O extglob -O globstar -c
.ONESHELL:
.SILENT:
.SUFFIXES:

VENV   ?= true
ifeq (true,$(VENV))
PYENV  ?= pyenv exec python
PYTHON ?= python
PIP    := pip --disable-pip-version-check --no-input --require-virtualenv
else
PYENV  ?= python3
PYTHON ?= python3
PIP    := pip --disable-pip-version-check --no-input
endif
SCRIPT := redist.py
REDIST := $(PYTHON) $(SCRIPT)

.PHONY: all
all: format lint download build assemble verify test

.PHONY: download build assemble verify test
download build assemble verify test: venv/.make
	$(REDIST) $@

.PHONY: venv
venv: venv/.make
venv/.make: pyproject.toml
	$(PYENV) -m venv venv
	$(PIP) install --upgrade pip
	$(PIP) install .
	touch $@

.PHONY: format
format: venv/.make
ifdef CI
	black --check --fast $(SCRIPT)
else
	black --fast $(SCRIPT)
endif

.PHONY: lint
lint: venv/.make
	ruff check $(SCRIPT)
	pyright --lib $(SCRIPT)

.PHONY: clean
clean:
	rm -fr ./.*cache*/ ./*.egg-info/ ./{build,dist}/
