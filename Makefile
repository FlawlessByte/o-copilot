.PHONY: help venv install run dev test clean

VENV ?= .venv
PY   := $(VENV)/bin/python
PIP  := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn

HOST ?= 127.0.0.1
PORT ?= 8000

help:
	@echo "Targets:"
	@echo "  make venv     - create local virtualenv in $(VENV)/"
	@echo "  make install  - install dependencies into $(VENV)/"
	@echo "  make run      - run FastAPI server (no reload)"
	@echo "  make dev      - run FastAPI server with --reload"
	@echo "  make test     - run unit tests (pytest)"
	@echo "  make clean    - remove $(VENV)/"

venv:
	@test -d "$(VENV)" || python -m venv "$(VENV)"
	@$(PY) -m pip install --upgrade pip >/dev/null

install: venv
	@$(PIP) install -r requirements.txt

run: install
	@$(UVICORN) app.main:app --host $(HOST) --port $(PORT)

dev: install
	@$(UVICORN) app.main:app --reload --host $(HOST) --port $(PORT)

test: install
	@$(PY) -m pytest -q

clean:
	@rm -rf "$(VENV)"
