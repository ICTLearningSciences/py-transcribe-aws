PWD=$(shell pwd)
PROJECT_ROOT?=$(shell git rev-parse --show-toplevel 2> /dev/null)
WATSON_CREDENTIALS=secrets/watson_credentials.txt
WATSON_USERNAME?=$(shell if [ -f $(WATSON_CREDENTIALS) ]; then head -n 1 $(WATSON_CREDENTIALS); else echo ""; fi)
WATSON_PASSWORD?=$(shell if [ -f $(WATSON_CREDENTIALS) ]; then tail -n 1 $(WATSON_CREDENTIALS); else echo ""; fi)

# virtualenv used for pytest
VENV=.venv
$(VENV):
	$(MAKE) venv-create

.PHONY: format
format: $(VENV)
	$(VENV)/bin/black transcribe_aws tests

PHONY: test
test: $(VENV)
	$(VENV)/bin/py.test -vv $(args)

.PHONY: test-all
test-all: test-format test-lint test-types test

.PHONY: test-format
test-format: $(VENV)
	$(VENV)/bin/black --check transcribe_aws tests

.PHONY: test-lint
test-lint: $(VENV)
	$(VENV)/bin/flake8 .

.PHONY: test-types
test-types: $(VENV)
	. $(VENV)/bin/activate && mypy transcribe_aws

$(WATSON_CREDENTIALS):
	@echo "SET_USERNAME_HERE" > $(WATSON_CREDENTIALS)
	@echo "SET_PASSWORD_HERE" >> $(WATSON_CREDENTIALS)
	chmod 600 $(WATSON_CREDENTIALS)

# Removes all mentor files from the local file system
.PHONY clean:
clean:
	rm -rf .venv htmlcov .coverage 



.PHONY: venv-create
venv-create: virtualenv-installed
	[ -d $(VENV) ] || virtualenv -p python3 $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r ./requirements.test.txt

virtualenv-installed:
	$(PROJECT_ROOT)/bin/virtualenv_ensure_installed.sh
