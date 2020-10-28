DISTPATH=$(shell python -c "import site; print(site.getsitepackages())" | cut -f2 -d"'")
PACKAGE:=$(shell basename $(shell pwd))
ISINST=$(shell pip show $(PACKAGE) | wc -l )
TMPFOLDER=/tmp/install-$(PACKAGE)

.PHONY = clean install uninstall test dist distupload distinstall disttest dist distupload distinstall disttest  disttestupload disttestinstall

## -------------------------
## siriuspy - Makefile help
## -------------------------

help:  ## Show this help.
	@grep '##' Makefile| sed -e '/@/d' | sed -r 's,(.*?:).*##(.*),\1\2,g'

clean: ## Clean repository via "git clean -fdX"
	git clean -fdX

develop: uninstall ## Install in editable mode (i.e. setuptools "develop mode")
	pip install --no-deps -e ./

install: uninstall ## Install packge using the local repository
ifneq (, $(wildcard $(TMPFOLDER)))
	rm -rf /tmp/install-$(PACKAGE)
endif
	cp -rRL ../$(PACKAGE) /tmp/install-$(PACKAGE)
	cd /tmp/install-$(PACKAGE)/; pip install --no-deps ./
	rm -rf /tmp/install-$(PACKAGE)

# known issue: It will fail to uninstall scripts if they were installed in develop mode
uninstall: clean ## Remove package
ifneq ($(ISINST),0)
	pip uninstall -y $(PACKAGE)
else
	echo 'already uninstalled $(PACKAGE)'
endif

test: ## Run tests
	python setup.py test

dist: clean ## Build setuptools dist
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
