# Destination directory
SERVICES = $(shell ls *.service | grep -v Makefile)

# test:
# 	for ser in $(SERVICES) ; do \
# 	echo $$ser ; \
# 	done

install-services:
	@echo " --- install services ---"
	for ser in $(SERVICES) ; do \
	  cp -rf $$ser /etc/systemd/system/ ; \
	done
	systemctl daemon-reload
	mkdir -p /home/fac/sirius-iocs/as-ma
	mkdir -p /home/fac/sirius-iocs/pvs
	chown -R fac.fac /home/fac/sirius-iocs/as-ma
	chown -R fac.fac /home/fac/sirius-iocs/pvs

stop-services:
	@echo " --- stop services ---"
	for ser in $(SERVICES) ; do \
	  systemctl stop $$ser ; \
	done

start-services: install-services
	@echo " --- start services ---"
	for ser in $(SERVICES) ; do \
	  #systemctl enable $$ser ; \
	  systemctl start $$ser  ; \
	done

uninstall-services: stop-services
	@echo " --- uninstall services ---"
	for ser in $(SERVICES) ; do \
	  systemctl disable $$ser ; \
		rm -rf /etc/systemd/system/$$ser ; \
	done
	systemctl daemon-reload
