DISTPATH=$(shell python -c "import site; print(site.getsitepackages())" | cut -f2 -d"'")
PACKAGE:=$(shell basename $(shell pwd))
ISINST=$(shell pip show $(PACKAGE) | wc -l )
TMPFOLDER=/tmp/install-$(PACKAGE)

.PHONY = clean install uninstall test dist distupload distinstall disttest dist distupload distinstall disttest  disttestupload disttestinstall

clean:
	git clean -fdX

develop: uninstall
	pip-sirius install --no-deps -e ./

install: uninstall
ifneq (, $(wildcard $(TMPFOLDER)))
	rm -rf /tmp/install-$(PACKAGE)
endif
	cp -rRL ../$(PACKAGE) /tmp/install-$(PACKAGE)
	cd /tmp/install-$(PACKAGE)/; pip install --no-deps ./
	rm -rf /tmp/install-$(PACKAGE)

# known issue: It will fail to uninstall scripts if they were installed in develop mode
uninstall: clean
ifneq ($(ISINST),0)
	pip uninstall -y $(PACKAGE)
else
	echo 'already uninstalled $(PACKAGE)'
endif

test:
	python setup.py test

dist: clean
	python setup.py sdist bdist_wheel

distupload:
	python -m twine upload --verbose dist/*

distinstall:
	python -m pip install $(PACKAGE)==$(shell cat "VERSION")

disttestupload:
	python -m twine upload --verbose --repository testpypi dist/*

disttestinstall:
	python -m pip install --index-url https://test.pypi.org/simple/ --no-deps $(PACKAGE)==$(shell cat "VERSION")

disttest: dist disttestupload disttestinstall test
