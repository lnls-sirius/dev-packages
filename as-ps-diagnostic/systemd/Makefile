
install-tb:
	@printf "Installing sirius-ioc-ps-diagnostic-tb service...\n"
	cp -rf sirius-ioc-ps-diagnostic-tb.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	systemctl daemon-reload

stop-tb:
	@printf "Stopping  sirius-ioc-ps-diagnostic-tb...\n"
	systemctl stop sirius-ioc-ps-diagnostic-tb.service

start-tb:
	@printf "Starting  sirius-ioc-ps-diagnostic-tb...\n"
	systemctl start sirius-ioc-ps-diagnostic-tb.service

uninstall-tb: stop-tb
	@printf "Uninstalling  sirius-ioc-ps-diagnostic-tb...\n"
	systemctl disable sirius-ioc-ps-diagnostic-tb.service
	rm -rf /etc/systemd/system/sirius-bbb-ioc-ps.service
	systemctl daemon-reload
	systemctl reset-failed


# --- ALL ACCELERATORS ---

install-services: install-tb

stop: stop-tb

start: start-tb

uninstall: uninstall-tb
