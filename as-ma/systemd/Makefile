
install-tb-dipoles:
	@printf "Intalling sirius-ioc-ma-tb-dipoles service...\n"
	cp -rf sirius-ioc-ma-tb-dipoles.service /etc/systemd/system/
	mkdir -p /fac/sirius-iocs/pvs
	systemctl daemon-reload

stop-tb-dipoles:
	@printf "Stopping sirius-ioc-ma-tb-dipoles...\n"
	systemctl stop sirius-ioc-ma-tb-dipoles.service

start-tb-dipoles:
	@printf "Starting sirius-ioc-ma-tb-dipoles...\n"
	systemctl start sirius-ioc-ma-tb-dipoles.service

uninstall-tb-dipoles: stop-tb-dipoles
	@printf "Uninstalling sirius-ioc-ma-tb-dipoles...\n"
	systemctl disable sirius-ioc-ma-tb-dipoles.service
	rm -rf /etc/systemd/system/sirius-ioc-ma-tb-dipoles.service
	systemctl daemon-reload
	systemctl reset-failed


install-tb-quadrupoles:
	@printf "Intalling sirius-ioc-ma-tb-quadrupoles service...\n"
	cp -rf sirius-ioc-ma-tb-quadrupoles.service /etc/systemd/system/
	mkdir -p /fac/sirius-iocs/pvs
	systemctl daemon-reload

stop-tb-quadrupoles:
	@printf "Stopping sirius-ioc-ma-tb-quadrupoles...\n"
	systemctl stop sirius-ioc-ma-tb-quadrupoles.service

start-tb-quadrupoles:
	@printf "Starting sirius-ioc-ma-tb-quadrupoles...\n"
	systemctl start sirius-ioc-ma-tb-quadrupoles.service

uninstall-tb-quadrupoles: stop-tb-quadrupoles
	@printf "Uninstalling sirius-ioc-ma-tb-quadrupoles...\n"
	systemctl disable sirius-ioc-ma-tb-quadrupoles.service
	rm -rf /etc/systemd/system/sirius-ioc-ma-tb-quadrupoles.service
	systemctl daemon-reload
	systemctl reset-failed


install-tb-correctors:
	@printf "Intalling sirius-ioc-ma-tb-correctors service...\n"
	cp -rf sirius-ioc-ma-tb-correctors.service /etc/systemd/system/
	mkdir -p /fac/sirius-iocs/pvs
	systemctl daemon-reload

stop-tb-correctors:
	@printf "Stopping sirius-ioc-ma-tb-correctors...\n"
	systemctl stop sirius-ioc-ma-tb-correctors.service

start-tb-correctors:
	@printf "Starting sirius-ioc-ma-tb-correctors...\n"
	systemctl start sirius-ioc-ma-tb-quadrupoles.service

uninstall-tb-correctors: stop-tb-correctors
	@printf "Uninstalling sirius-ioc-ma-tb-correctors...\n"
	systemctl disable sirius-ioc-ma-tb-correctors.service
	rm -rf /etc/systemd/system/sirius-ioc-ma-tb-correctors.service
	systemctl daemon-reload
	systemctl reset-failed



install: install-tb-dipoles install-tb-quadrupoles install-tb-correctors

stop: stop-tb-dipoles stop-tb-quadrupoles stop-tb-correctors

start: start-tb-dipoles start-tb-quadrupoles start-tb-correctors

uninstall: uninstall-tb-dipoles uninstall-tb-quadrupoles uninstall-tb-correctors
