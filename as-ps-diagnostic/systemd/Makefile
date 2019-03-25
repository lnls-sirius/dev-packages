
install-tb:
	@printf "Installing sirius-ioc-tb-ps-diagnostic service...\n"
	cp -rf sirius-ioc-tb-ps-diagnostic.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	systemctl daemon-reload

stop-tb:
	@printf "Stopping  sirius-ioc-tb-ps-diagnostic...\n"
	systemctl stop sirius-ioc-tb-ps-diagnostic.service

start-tb:
	@printf "Starting  sirius-ioc-tb-ps-diagnostic...\n"
	systemctl start sirius-ioc-tb-ps-diagnostic.service

uninstall-tb: stop-tb
	@printf "Uninstalling  sirius-ioc-tb-ps-diagnostic...\n"
	systemctl disable sirius-ioc-tb-ps-diagnostic.service
	rm -rf /etc/systemd/system/sirius-bbb-ioc-ps.service
	systemctl daemon-reload
	systemctl reset-failed


# --- ALL ACCELERATORS ---

install-services: install-tb

stop: stop-tb

start: start-tb

uninstall: uninstall-tb
