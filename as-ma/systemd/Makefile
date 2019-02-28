# --- TB ---

install-tb-dipoles:
	@printf "Intalling sirius-ioc-tb-ma-dipoles service...\n"
	cp -rf sirius-ioc-tb-ma-dipoles.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-tb-dipoles:
	@printf "Stopping sirius-ioc-tb-ma-dipoles...\n"
	systemctl stop sirius-ioc-tb-ma-dipoles.service

start-tb-dipoles:
	@printf "Starting sirius-ioc-tb-ma-dipoles...\n"
	systemctl start sirius-ioc-tb-ma-dipoles.service

uninstall-tb-dipoles: stop-tb-dipoles
	@printf "Uninstalling sirius-ioc-tb-ma-dipoles...\n"
	systemctl disable sirius-ioc-tb-ma-dipoles.service
	rm -rf /etc/systemd/system/sirius-ioc-tb-ma-dipoles.service
	systemctl daemon-reload
	systemctl reset-failed


install-tb-quadrupoles:
	@printf "Intalling sirius-ioc-tb-ma-quadrupoles service...\n"
	cp -rf sirius-ioc-tb-ma-quadrupoles.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-tb-quadrupoles:
	@printf "Stopping sirius-ioc-tb-ma-quadrupoles...\n"
	systemctl stop sirius-ioc-tb-ma-quadrupoles.service

start-tb-quadrupoles:
	@printf "Starting sirius-ioc-tb-ma-quadrupoles...\n"
	systemctl start sirius-ioc-tb-ma-quadrupoles.service

uninstall-tb-quadrupoles: stop-tb-quadrupoles
	@printf "Uninstalling sirius-ioc-tb-ma-quadrupoles...\n"
	systemctl disable sirius-ioc-tb-ma-quadrupoles.service
	rm -rf /etc/systemd/system/sirius-ioc-tb-ma-quadrupoles.service
	systemctl daemon-reload
	systemctl reset-failed


install-tb-correctors:
	@printf "Intalling sirius-ioc-tb-ma-correctors service...\n"
	cp -rf sirius-ioc-tb-ma-correctors.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-tb-correctors:
	@printf "Stopping sirius-ioc-tb-ma-correctors...\n"
	systemctl stop sirius-ioc-tb-ma-correctors.service

start-tb-correctors:
	@printf "Starting sirius-ioc-tb-ma-correctors...\n"
	systemctl start sirius-ioc-tb-ma-correctors.service

uninstall-tb-correctors: stop-tb-correctors
	@printf "Uninstalling sirius-ioc-tb-ma-correctors...\n"
	systemctl disable sirius-ioc-tb-ma-correctors.service
	rm -rf /etc/systemd/system/sirius-ioc-tb-ma-correctors.service
	systemctl daemon-reload
	systemctl reset-failed


install-tb-injsept:
	@printf "Intalling sirius-ioc-tb-pm-injsept service...\n"
	cp -rf sirius-ioc-tb-pm-injsept.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-tb-injsept:
	@printf "Stopping sirius-ioc-tb-pm-correctors...\n"
	systemctl stop sirius-ioc-tb-pm-injsept.service

start-tb-injsept:
	@printf "Starting sirius-ioc-tb-pm-injsept...\n"
	systemctl start sirius-ioc-tb-pm-injsept.service

uninstall-tb-injsept: stop-tb-injsept
	@printf "Uninstalling sirius-ioc-tb-pm-injsept...\n"
	systemctl disable sirius-ioc-tb-pm-injsept.service
	rm -rf /etc/systemd/system/sirius-ioc-tb-pm-injsept.service
	systemctl daemon-reload
	systemctl reset-failed



install-tb: install-tb-dipoles install-tb-quadrupoles install-tb-correctors install-tb-injsept

stop-tb: stop-tb-dipoles stop-tb-quadrupoles stop-tb-correctors stop-tb-injsept

start-tb: start-tb-dipoles start-tb-quadrupoles start-tb-correctors start-tb-injsept

uninstall-tb: uninstall-tb-dipoles uninstall-tb-quadrupoles uninstall-tb-correctors uninstall-tb-injsept


# --- BO ---

install-bo-correctors-01:
	@printf "Intalling sirius-ioc-bo-ma-correctors-01 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-01.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-01:
	@printf "Stopping sirius-ioc-bo-ma-correctors-01...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-01.service

start-bo-correctors-01:
	@printf "Starting sirius-ioc-bo-ma-correctors-01...\n"
	systemctl start sirius-ioc-bo-ma-correctors-01.service

uninstall-bo-correctors-01: stop-bo-correctors-01
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-01...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-01.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-01.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-02:
	@printf "Intalling sirius-ioc-bo-ma-correctors-02 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-02.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-02:
	@printf "Stopping sirius-ioc-bo-ma-correctors-02...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-02.service

start-bo-correctors-02:
	@printf "Starting sirius-ioc-bo-ma-correctors-02...\n"
	systemctl start sirius-ioc-bo-ma-correctors-02.service

uninstall-bo-correctors-02: stop-bo-correctors-02
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-02...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-02.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-02.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-03:
	@printf "Intalling sirius-ioc-bo-ma-correctors-03 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-03.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-03:
	@printf "Stopping sirius-ioc-bo-ma-correctors-03...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-03.service

start-bo-correctors-03:
	@printf "Starting sirius-ioc-bo-ma-correctors-03...\n"
	systemctl start sirius-ioc-bo-ma-correctors-03.service

uninstall-bo-correctors-03: stop-bo-correctors-03
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-03...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-03.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-03.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-04:
	@printf "Intalling sirius-ioc-bo-ma-correctors-04 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-04.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-04:
	@printf "Stopping sirius-ioc-bo-ma-correctors-04...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-04.service

start-bo-correctors-04:
	@printf "Starting sirius-ioc-bo-ma-correctors-04...\n"
	systemctl start sirius-ioc-bo-ma-correctors-04.service

uninstall-bo-correctors-04: stop-bo-correctors-04
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-04...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-04.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-04.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-05:
	@printf "Intalling sirius-ioc-bo-ma-correctors-05 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-05.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-05:
	@printf "Stopping sirius-ioc-bo-ma-correctors-05...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-05.service

start-bo-correctors-05:
	@printf "Starting sirius-ioc-bo-ma-correctors-05...\n"
	systemctl start sirius-ioc-bo-ma-correctors-05.service

uninstall-bo-correctors-05: stop-bo-correctors-05
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-05...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-05.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-05.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-06:
	@printf "Intalling sirius-ioc-bo-ma-correctors-06 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-06.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-06:
	@printf "Stopping sirius-ioc-bo-ma-correctors-06...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-06.service

start-bo-correctors-06:
	@printf "Starting sirius-ioc-bo-ma-correctors-06...\n"
	systemctl start sirius-ioc-bo-ma-correctors-06.service

uninstall-bo-correctors-06: stop-bo-correctors-06
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-06...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-06.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-06.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-07:
	@printf "Intalling sirius-ioc-bo-ma-correctors-07 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-07.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-07:
	@printf "Stopping sirius-ioc-bo-ma-correctors-07...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-07.service

start-bo-correctors-07:
	@printf "Starting sirius-ioc-bo-ma-correctors-07...\n"
	systemctl start sirius-ioc-bo-ma-correctors-07.service

uninstall-bo-correctors-07: stop-bo-correctors-07
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-07...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-07.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-07.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-08:
	@printf "Intalling sirius-ioc-bo-ma-correctors-08 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-08.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-08:
	@printf "Stopping sirius-ioc-bo-ma-correctors-08...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-08.service

start-bo-correctors-08:
	@printf "Starting sirius-ioc-bo-ma-correctors-08...\n"
	systemctl start sirius-ioc-bo-ma-correctors-08.service

uninstall-bo-correctors-08: stop-bo-correctors-08
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-08...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-08.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-08.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-09:
	@printf "Intalling sirius-ioc-bo-ma-correctors-09 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-09.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-09:
	@printf "Stopping sirius-ioc-bo-ma-correctors-09...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-09.service

start-bo-correctors-09:
	@printf "Starting sirius-ioc-bo-ma-correctors-09...\n"
	systemctl start sirius-ioc-bo-ma-correctors-09.service

uninstall-bo-correctors-09: stop-bo-correctors-09
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-09...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-09.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-09.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-10:
	@printf "Intalling sirius-ioc-bo-ma-correctors-10 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-10.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-10:
	@printf "Stopping sirius-ioc-bo-ma-correctors-10...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-10.service

start-bo-correctors-10:
	@printf "Starting sirius-ioc-bo-ma-correctors-10...\n"
	systemctl start sirius-ioc-bo-ma-correctors-10.service

uninstall-bo-correctors-10: stop-bo-correctors-10
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-10...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-10.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-10.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-11:
	@printf "Intalling sirius-ioc-bo-ma-correctors-11 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-11.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-11:
	@printf "Stopping sirius-ioc-bo-ma-correctors-11...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-11.service

start-bo-correctors-11:
	@printf "Starting sirius-ioc-bo-ma-correctors-11...\n"
	systemctl start sirius-ioc-bo-ma-correctors-11.service

uninstall-bo-correctors-11: stop-bo-correctors-11
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-11...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-11.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-11.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-12:
	@printf "Intalling sirius-ioc-bo-ma-correctors-12 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-12.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-12:
	@printf "Stopping sirius-ioc-bo-ma-correctors-12...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-12.service

start-bo-correctors-12:
	@printf "Starting sirius-ioc-bo-ma-correctors-12...\n"
	systemctl start sirius-ioc-bo-ma-correctors-12.service

uninstall-bo-correctors-12: stop-bo-correctors-12
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-12...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-12.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-12.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-13:
	@printf "Intalling sirius-ioc-bo-ma-correctors-13 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-13.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-13:
	@printf "Stopping sirius-ioc-bo-ma-correctors-13...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-13.service

start-bo-correctors-13:
	@printf "Starting sirius-ioc-bo-ma-correctors-13...\n"
	systemctl start sirius-ioc-bo-ma-correctors-13.service

uninstall-bo-correctors-13: stop-bo-correctors-13
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-13...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-13.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-13.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors: install-bo-correctors-01 install-bo-correctors-02 install-bo-correctors-03 install-bo-correctors-04 install-bo-correctors-05 install-bo-correctors-06 install-bo-correctors-07 install-bo-correctors-08 install-bo-correctors-09 install-bo-correctors-10 install-bo-correctors-11 install-bo-correctors-12 install-bo-correctors-13

stop-bo-correctors: stop-bo-correctors-01 stop-bo-correctors-02 stop-bo-correctors-03 stop-bo-correctors-04 stop-bo-correctors-05 stop-bo-correctors-06 stop-bo-correctors-07 stop-bo-correctors-08 stop-bo-correctors-09 stop-bo-correctors-10 stop-bo-correctors-11 stop-bo-correctors-12 stop-bo-correctors-13

start-bo-correctors: start-bo-correctors-01 start-bo-correctors-02 start-bo-correctors-03 start-bo-correctors-04 start-bo-correctors-05 start-bo-correctors-06 start-bo-correctors-07 start-bo-correctors-08 start-bo-correctors-09 start-bo-correctors-10 start-bo-correctors-11 start-bo-correctors-12 start-bo-correctors-13

uninstall-bo-correctors: uninstall-bo-correctors-01 uninstall-bo-correctors-02 uninstall-bo-correctors-03 uninstall-bo-correctors-04 uninstall-bo-correctors-05 uninstall-bo-correctors-06 uninstall-bo-correctors-07 uninstall-bo-correctors-08 uninstall-bo-correctors-09 uninstall-bo-correctors-10 uninstall-bo-correctors-11 uninstall-bo-correctors-12 uninstall-bo-correctors-13

install-bo-dipoles:
	@printf "Intalling sirius-ioc-bo-ma-dipoles service...\n"
	cp -rf sirius-ioc-bo-ma-dipoles.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-dipoles:
	@printf "Stopping sirius-ioc-bo-ma-dipoles...\n"
	systemctl stop sirius-ioc-bo-ma-dipoles.service

start-bo-dipoles:
	@printf "Starting sirius-ioc-bo-ma-dipoles...\n"
	systemctl start sirius-ioc-bo-ma-dipoles.service

uninstall-bo-dipoles: stop-bo-dipoles
	@printf "Uninstalling sirius-ioc-bo-ma-dipoles...\n"
	systemctl disable sirius-ioc-bo-ma-dipoles.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-dipoles.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-quadrupoles:
	@printf "Intalling sirius-ioc-bo-ma-quadrupoles service...\n"
	cp -rf sirius-ioc-bo-ma-quadrupoles.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-quadrupoles:
	@printf "Stopping sirius-ioc-bo-ma-quadrupoles...\n"
	systemctl stop sirius-ioc-bo-ma-quadrupoles.service

start-bo-quadrupoles:
	@printf "Starting sirius-ioc-bo-ma-quadrupoles...\n"
	systemctl start sirius-ioc-bo-ma-quadrupoles.service

uninstall-bo-quadrupoles: stop-bo-quadrupoles
	@printf "Uninstalling sirius-ioc-bo-ma-quadrupoles...\n"
	systemctl disable sirius-ioc-bo-ma-quadrupoles.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-quadrupoles.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-sextupoles:
	@printf "Intalling sirius-ioc-bo-ma-sextupoles service...\n"
	cp -rf sirius-ioc-bo-ma-sextupoles.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-sextupoles:
	@printf "Stopping sirius-ioc-bo-ma-sextupoles...\n"
	systemctl stop sirius-ioc-bo-ma-sextupoles.service

start-bo-sextupoles:
	@printf "Starting sirius-ioc-bo-ma-sextupoles...\n"
	systemctl start sirius-ioc-bo-ma-sextupoles.service

uninstall-bo-sextupoles: stop-bo-sextupoles
	@printf "Uninstalling sirius-ioc-bo-ma-sextupoles...\n"
	systemctl disable sirius-ioc-bo-ma-sextupoles.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-sextupoles.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo: install-bo-correctors install-bo-dipoles install-bo-quadrupoles install-bo-sextupoles

stop-bo: stop-bo-correctors stop-bo-dipoles stop-bo-quadrupoles stop-bo-sextupoles

start-bo: start-bo-correctors start-bo-dipoles start-bo-quadrupoles start-bo-sextupoles

uninstall-bo: uninstall-bo-correctors uninstall-bo-dipoles uninstall-bo-quadrupoles uninstall-bo-sextupoles



# --- ALL ACCELERATORS ---

install-services: install-tb install-bo

stop: stop-tb stop-bo

start: start-tb start-bo

uninstall: uninstall-tb uninstall-bo
