PACKAGE:=$(shell basename $(shell pwd))
PREFIX ?=
PIP ?= pip
ifeq ($(CONDA_PREFIX),)
	PREFIX=sudo -H
	PIP=pip-sirius
endif

install: uninstall
	$(PREFIX) $(PIP) install --no-use-pep517 --no-deps ./
#	$(PREFIX) $(PIP) install --no-deps ./
	$(PREFIX) git clean -fdX

uninstall:
	$(PREFIX) $(PIP) uninstall -y $(PACKAGE)

develop-install: develop-uninstall
	$(PIP) install --no-use-pep517 --no-deps -e ./
#	$(PIP) install --no-deps -e ./

# known issue: It will fail to uninstall scripts
#  if they were installed in develop mode
develop-uninstall:
	$(PIP) uninstall -y $(PACKAGE)

test:
	pytest tests/

dist: ## Build setuptools dist
	python setup.py sdist bdist_wheel

distupload: ## Upload package dist to PyPi
	python -m twine upload --verbose dist/*

distinstall: ## Install package from PyPi
	python -m pip install $(PACKAGE)==$(shell cat "VERSION")

disttestupload: ##  Upload package dist to Test PyPi
	python -m twine upload --verbose --repository testpypi dist/*

disttestinstall: ##  Install package from Test PyPi
	python -m pip install --index-url https://test.pypi.org/simple/ --no-deps $(PACKAGE)==$(shell cat "VERSION")

disttest: dist disttestupload disttestinstall test ## Build the package, upload to Test PyPi, install from PyPi and run tests
