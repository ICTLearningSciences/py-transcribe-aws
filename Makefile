# virtualenv used for pytest
VENV=.venv
$(VENV):
	$(MAKE) $(VENV)-update

.PHONY: $(VENV)-update
$(VENV)-update: virtualenv-installed
	[ -d $(VENV) ] || virtualenv -p python3.8 $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r ./requirements.test.txt

virtualenv-installed:
	./bin/virtualenv_ensure_installed.sh

# Removes all mentor files from the local file system
.PHONY: clean
clean:
	rm -rf .venv htmlcov .coverage 

.PHONY: deps-update
deps-update: $(VENV)
	. $(VENV)/bin/activate && pip-upgrade requirements*

.PHONY: format
format: $(VENV)
	$(VENV)/bin/black transcribe_aws tests


LICENSE:
	@echo "you must have a LICENSE file" 1>&2
	exit 1

LICENSE_HEADER:
	@echo "you must have a LICENSE_HEADER file" 1>&2
	exit 1

.PHONY: license
license: LICENSE LICENSE_HEADER $(VENV)
	. $(VENV)/bin/activate \
		&& python -m licenseheaders -t LICENSE_HEADER -d transcribe_aws $(args) \
		&& python -m licenseheaders -t LICENSE_HEADER -d tests $(args)

PHONY: test
test: $(VENV)
	$(VENV)/bin/py.test -vv $(args)

.PHONY: test-all
test-all: test-format test-lint test-types test test-license

.PHONY: test-format
test-format: $(VENV)
	$(VENV)/bin/black --check transcribe_aws tests


.PHONY: test-license
test-license:
	args="--check" $(MAKE) license

.PHONY: test-lint
test-lint: $(VENV)
	$(VENV)/bin/flake8 .

.PHONY: test-types
test-types: $(VENV)
	. $(VENV)/bin/activate && mypy transcribe_aws
