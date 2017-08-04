# Destination directory
DEST_DIR = /usr/local/bin/sirius-iocs

IOC_DIR = as-ma

CWD = $(shell pwd)

FILES = as-ma.py \
        as_ma.py \
				main.py \
				pvs.py \
				VERSION \

install-scripts:
	@echo " --- install scripts ---"
	sudo mkdir -p $(DEST_DIR)/$(IOC_DIR); sudo chmod g+w $(DEST_DIR)
	sudo ln -sf $(CWD)/as-ma.py $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/as_ma.py $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/main.py $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/pvs.py $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/VERSION $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/systemd/ioc-as-ma-tb-dipole-fam.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo chown -R fac.fac $(DEST_DIR)

stop-services:
	@echo " --- stoping services ---"
	-sudo systemctl stop ioc-as-ma-tb-dipole-fam.service

install-services: install-scripts stop-services
	@echo " --- install services ---"
	sudo cp -rf systemd/ioc-as-ma-tb-dipole-fam.service /etc/systemd/system/
	sudo systemctl daemon-reload

start-services: install-scripts install-services
	@echo " --- start-services ---"
	sudo systemctl start ioc-as-ma-tb-dipole-fam.service
