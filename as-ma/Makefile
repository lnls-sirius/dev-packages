# Destination directory
DEST_DIR = /usr/local/bin/sirius-iocs

IOC_DIR = as-ma

CWD = $(shell pwd)


install: install-module-links install-service-links

install-module-links:
	@echo " --- install module links ---"
	sudo mkdir -p $(DEST_DIR)/$(IOC_DIR); sudo chmod g+w $(DEST_DIR)
	sudo ln -sf $(CWD)/as-ma.py $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/as_ma.py $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/main.py $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/pvs.py $(DEST_DIR)/$(IOC_DIR)/
	sudo chown -R fac.fac $(DEST_DIR)

install-service-links:
	@echo " --- install service links ---"
	sudo ln -sf $(CWD)/systemd/ioc-tb-ma-dipole-fam.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-tb-ma-corrector.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-tb-ma-multipole.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-tb-ma-dipole-fam.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/systemd/ioc-tb-ma-corrector.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/systemd/ioc-tb-ma-multipole.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/systemd/ioc-ts-ma-dipole-fam.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-ts-ma-corrector.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-ts-ma-multipole.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-ts-ma-dipole-fam.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/systemd/ioc-ts-ma-corrector.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/systemd/ioc-ts-ma-multipole.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo systemctl daemon-reload

start-ioc-ma: start-ioc-tb-ma start-ioc-ts-ma
stop-ioc-ma: stop-ioc-tb-ma stop-ioc-ts-ma

start-ioc-tb-ma: start-ioc-tb-ma-dipole-fam start-ioc-tb-ma-corrector start-ioc-tb-ma-multipole
stop-ioc-tb-ma: stop-ioc-tb-ma-dipole-fam stop-ioc-tb-ma-corrector stop-ioc-tb-ma-multipole

start-ioc-ts-ma: start-ioc-ts-ma-dipole-fam start-ioc-ts-ma-corrector start-ioc-ts-ma-multipole
stop-ioc-ts-ma: stop-ioc-ts-ma-dipole-fam stop-ioc-ts-ma-corrector stop-ioc-ts-ma-multipole


start-ioc-tb-ma-dipole-fam:
	@echo " --- start ioc-tb-ma-dipole-fam ---"
	sudo systemctl start ioc-tb-ma-dipole-fam.service

stop-ioc-tb-ma-dipole-fam:
	@echo " --- stop ioc-tb-ma-dipole-fam ---"
	sudo systemctl stop ioc-tb-ma-dipole-fam.service

start-ioc-tb-ma-corrector:
	@echo " --- start ioc-tb-ma-corrector ---"
	sudo systemctl start ioc-tb-ma-corrector.service

stop-ioc-tb-ma-corrector:
	@echo " --- stop ioc-tb-ma-corrector ---"
	sudo systemctl stop ioc-tb-ma-corrector.service

start-ioc-tb-ma-multipole:
	@echo " --- start ioc-tb-ma-multipole ---"
	sudo systemctl start ioc-tb-ma-multipole.service

stop-ioc-tb-ma-multipole:
	@echo " --- stop ioc-tb-ma-multipole ---"
	sudo systemctl stop ioc-tb-ma-multipole.service


start-ioc-ts-ma-dipole-fam:
	@echo " --- start ioc-ts-ma-dipole-fam ---"
	sudo systemctl start ioc-ts-ma-dipole-fam.service

stop-ioc-ts-ma-dipole-fam:
	@echo " --- stop ioc-ts-ma-dipole-fam ---"
	-sudo systemctl stop ioc-ts-ma-dipole-fam.service

start-ioc-ts-ma-corrector:
	@echo " --- start ioc-ts-ma-corrector ---"
	sudo systemctl start ioc-ts-ma-corrector.service

stop-ioc-ts-ma-corrector:
	@echo " --- stop ioc-ts-ma-corrector ---"
	sudo systemctl stop ioc-ts-ma-corrector.service

start-ioc-ts-ma-multipole:
	@echo " --- start ioc-ts-ma-multipole ---"
	sudo systemctl start ioc-ts-ma-multipole.service

stop-ioc-ts-ma-multipole:
	@echo " --- stop ioc-ts-ma-multipole ---"
	sudo systemctl stop ioc-ts-ma-multipole.service
