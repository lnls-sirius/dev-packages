# Destination directory
DEST_DIR = /usr/local/bin/sirius-iocs

IOC_DIR = as-ma

IOC_EXECS = $(shell cd systemd; ls *.bash)

FILES = as-ma.py \
        as_ma.py \
				main.py \
				pvs.py \
				VERSION \
				systemd/si-dipoles.bash \
				systemd/si-quadrupoles.bash


print:
	echo $(BASH_FILES)

install: install-files install-services
		
create-services:
	sudo cp systemd/*.service /etc/systemd/system/
	systemctl enable ioc-as-ma-si-dipoles.service
	systemctl enable ioc-as-ma-si-quadrupoles.service

install-files:
	sudo mkdir -p $(DEST_DIR)/$(IOC_DIR); sudo chmod g+w $(DEST_DIR)
	sudo cp -rfa $(FILES) $(DEST_DIR)/$(IOC_DIR)/
	sudo chown -R fac.fac $(DEST_DIR);

stop-services:
	sudo systemctl stop ioc-as-ma-si-dipoles.service 2>&1 > /dev/null
	sudo systemctl stop ioc-as-ma-si-quadrupoles.service 2>&1 > /dev/null

install-services: stop-services
	sudo cp -rf systemd/*.service /etc/systemd/system/
	@echo ""
	@echo "!!! enable service with 'sudo systemctl enable <service-unit>'"
	@echo "!!! start service with 'sudo systemctl start <service-unit>'"

uninstall-files:
	sudo rm -rf $(DEST_DIR)/$(IOC_DIR)
