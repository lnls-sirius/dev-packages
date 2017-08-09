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
	sudo ln -sf $(CWD)/systemd/ioc-bo-ma-dipole-fam.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-bo-ma-corrector.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-bo-ma-multipole.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-bo-ma-dipole-fam.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/systemd/ioc-bo-ma-corrector.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/systemd/ioc-bo-ma-multipole.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/systemd/ioc-si-ma-dipole-fam.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-si-ma-corrector-slow.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-si-ma-corrector-fast.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-si-ma-multipole-fam.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-si-ma-quadrupole-trim.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-si-ma-dipole-fam.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/systemd/ioc-si-ma-corrector-slow.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/systemd/ioc-si-ma-corrector-fast.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/systemd/ioc-si-ma-multipole-fam.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/systemd/ioc-si-ma-quadrupole-trim.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo systemctl daemon-reload

start-ioc-ma: start-ioc-tb-ma start-ioc-ts-ma start-ioc-bo-ma start-ioc-si-ma
stop-ioc-ma: stop-ioc-tb-ma stop-ioc-ts-ma stop-ioc-bo-ma stop-ioc-si-ma

start-ioc-tb-ma: start-ioc-tb-ma-dipole-fam start-ioc-tb-ma-corrector start-ioc-tb-ma-multipole
stop-ioc-tb-ma: stop-ioc-tb-ma-dipole-fam stop-ioc-tb-ma-corrector stop-ioc-tb-ma-multipole

start-ioc-ts-ma: start-ioc-ts-ma-dipole-fam start-ioc-ts-ma-corrector start-ioc-ts-ma-multipole
stop-ioc-ts-ma: stop-ioc-ts-ma-dipole-fam stop-ioc-ts-ma-corrector stop-ioc-ts-ma-multipole

start-ioc-bo-ma: start-ioc-bo-ma-dipole-fam start-ioc-bo-ma-corrector start-ioc-bo-ma-multipole
stop-ioc-bo-ma: stop-ioc-bo-ma-dipole-fam stop-ioc-bo-ma-corrector stop-ioc-bo-ma-multipole

start-ioc-si-ma: start-ioc-si-ma-dipole-fam start-ioc-si-ma-corrector-slow start-ioc-si-ma-corrector-fast start-ioc-si-ma-multipole-fam start-ioc-si-ma-quadrupole-trim
stop-ioc-si-ma: stop-ioc-si-ma-dipole-fam stop-ioc-si-ma-corrector-slow stop-ioc-si-ma-corrector-fast stop-ioc-si-ma-multipole-fam stop-ioc-si-ma-quadrupole-trim


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


start-ioc-bo-ma-dipole-fam:
	@echo " --- start ioc-bo-ma-dipole-fam ---"
	sudo systemctl start ioc-bo-ma-dipole-fam.service

stop-ioc-bo-ma-dipole-fam:
	@echo " --- stop ioc-bo-ma-dipole-fam ---"
	-sudo systemctl stop ioc-bo-ma-dipole-fam.service

start-ioc-bo-ma-corrector:
	@echo " --- start ioc-bo-ma-corrector ---"
	sudo systemctl start ioc-bo-ma-corrector.service

stop-ioc-bo-ma-corrector:
	@echo " --- stop ioc-bo-ma-corrector ---"
	sudo systemctl stop ioc-bo-ma-corrector.service

start-ioc-bo-ma-multipole:
	@echo " --- start ioc-bo-ma-multipole ---"
	sudo systemctl start ioc-bo-ma-multipole.service

stop-ioc-bo-ma-multipole:
	@echo " --- stop ioc-bo-ma-multipole ---"
	sudo systemctl stop ioc-bo-ma-multipole.service


start-ioc-si-ma-dipole-fam:
	@echo " --- start ioc-si-ma-dipole-fam ---"
	sudo systemctl start ioc-si-ma-dipole-fam.service

stop-ioc-si-ma-dipole-fam:
	@echo " --- stop ioc-si-ma-dipole-fam ---"
	-sudo systemctl stop ioc-si-ma-dipole-fam.service

start-ioc-si-ma-corrector-slow:
	@echo " --- start ioc-si-ma-corrector-slow ---"
	sudo systemctl start ioc-si-ma-corrector-slow.service

stop-ioc-si-ma-corrector-slow:
	@echo " --- stop ioc-si-ma-corrector-slow ---"
	sudo systemctl stop ioc-si-ma-corrector-slow.service

start-ioc-si-ma-corrector-fast:
	@echo " --- start ioc-si-ma-corrector-fast ---"
	sudo systemctl start ioc-si-ma-corrector-fast.service

stop-ioc-si-ma-corrector-fast:
	@echo " --- stop ioc-si-ma-corrector-fast ---"
	sudo systemctl stop ioc-si-ma-corrector-fast.service

start-ioc-si-ma-multipole-fam:
	@echo " --- start ioc-si-ma-multipole-fam ---"
	sudo systemctl start ioc-si-ma-multipole-fam.service

stop-ioc-si-ma-multipole-fam:
	@echo " --- stop ioc-si-ma-multipole-fam ---"
	sudo systemctl stop ioc-si-ma-multipole-fam.service

start-ioc-si-ma-quadrupole-trim:
	@echo " --- start ioc-si-ma-quadrupole-trim ---"
	sudo systemctl start ioc-si-ma-quadrupole-trim.service

stop-ioc-si-ma-quadrupole-trim:
	@echo " --- stop ioc-si-ma-quadrupole-trim ---"
	sudo systemctl stop ioc-si-ma-quadrupole-trim.service
