# Destination directory
DEST_DIR = /usr/local/bin/sirius-iocs

IOC_DIR = as-ps-test

CWD = $(shell pwd)


install: install-module-links install-service-links

install-module-links:
	@echo " --- install module links ---"
	sudo mkdir -p $(DEST_DIR)/$(IOC_DIR); sudo chmod g+w $(DEST_DIR)
	sudo ln -sf $(CWD)/ps-test.py $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/ps_test.py $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/main.py $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/pvs.py $(DEST_DIR)/$(IOC_DIR)/
	sudo chown -R fac.fac $(DEST_DIR)

install-service-links:
	@echo " --- install service links ---"
	sudo ln -sf $(CWD)/systemd/ioc-as-ps-test.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-as-ps-test.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo systemctl daemon-reload


start-ioc-as-ps-test:
	@echo " --- start ioc-as-ps-test ---"
	sudo systemctl start ioc-as-ps-test.service

stop-ioc-as-ps-test:
	@echo " --- stop ioc-as-ps-test ---"
	sudo systemctl stop ioc-as-ps-test.service
