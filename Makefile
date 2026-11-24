PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip
export OPENMINION_HOME ?= $(CURDIR)/.om-home
export OPENMINION_DATA_ROOT ?= $(CURDIR)/.om-home/.openminion
export PYTHONPATH := $(CURDIR)/src:$(PYTHONPATH)

.PHONY: venv test inspect doctor demo

venv:
	python3 -m venv .venv
	$(PIP) install -U pip
	$(PIP) install -e ".[dev]"

test:
	$(PYTHON) -m pytest -q

inspect:
	$(PYTHON) -m dossier inspect fixtures/samples/payroll_lure.eml

doctor:
	$(PYTHON) -m dossier doctor

demo:
	$(PYTHON) -m dossier inspect --format pretty fixtures/samples/payroll_lure.eml
	$(PYTHON) -m dossier inspect --format pretty fixtures/samples/wallet_seed_lure.txt
	$(PYTHON) -m dossier inspect --format pretty fixtures/samples/benign_meeting.txt
