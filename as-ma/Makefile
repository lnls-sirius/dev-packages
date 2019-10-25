DISTPATH=$(shell python-sirius -c "import site; print(site.getsitepackages())" | cut -f2 -d"'")
PACKAGE:=$(shell basename $(shell pwd))
ISINST=$(shell sudo pip-sirius show $(PACKAGE) | wc -l )
EGGLINK=$(DISTPATH)/$(PACKAGE).egg-link
TMPFOLDER=/tmp/install-$(PACKAGE)

install: clean install-scripts install-services

develop: clean install-services
	sudo -H pip-sirius install -e ./

uninstall: clean uninstall-scripts uninstall-services

clean:
	git clean -fdX

install-scripts: clean
ifneq (, $(wildcard $(TMPFOLDER)))
	rm -rf /tmp/install-$(PACKAGE)
endif
	cp -rRL ../$(PACKAGE) /tmp/install-$(PACKAGE)
	cd /tmp/install-$(PACKAGE)/; sudo -H pip-sirius install ./
	rm -rf /tmp/install-$(PACKAGE)

install-services:
	cd systemd; sudo make install-services

uninstall-services:
	cd systemd; sudo make uninstall-services

uninstall-scripts:
ifneq (,$(wildcard $(EGGLINK)))
	sudo rm -r $(EGGLINK)
endif
ifneq ($(ISINST),0)
	sudo -H pip-sirius uninstall -y $(PACKAGE)
	sudo sed -i '/$(PACKAGE)/d' $(DISTPATH)/easy-install.pth
else
	echo 'already uninstalled $(PACKAGE)'
endif
