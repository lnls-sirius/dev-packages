# Destination directory
DEST_DIR = /usr/local/bin/sirius-iocs

IOC_DIR = ps-test


FILES = ps-test.py \
        ps_test.py \
	main.py \
	pvs.py \
	VERSION \

install-scripts:
	@echo " --- install scripts ---"
	sudo mkdir -p $(DEST_DIR)/$(IOC_DIR); sudo chmod g+w $(DEST_DIR)
	sudo cp -rfa $(FILES) $(DEST_DIR)/$(IOC_DIR)/
	sudo cp -fa systemd/ioc-ps-test.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo chown -R fac.fac $(DEST_DIR);

stop-services:
	@echo " --- stoping services ---"
	-sudo systemctl stop ioc-ps-test.service

install-services: install-scripts stop-services
	@echo " --- install services ---"
	sudo cp -rf systemd/ioc-ps-test.service /etc/systemd/system/
	sudo systemctl daemon-reload

start-services: install-scripts install-services
	@echo " --- start-services ---"
	sudo systemctl start ioc-ps-test.service
