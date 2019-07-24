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
	@printf "Stopping sirius-ioc-tb-pm-injsept...\n"
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

install-bo-correctors-ia01:
	@printf "Intalling sirius-ioc-bo-ma-correctors-ia01 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-ia01.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-ia01:
	@printf "Stopping sirius-ioc-bo-ma-correctors-ia01...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-ia01.service

start-bo-correctors-ia01:
	@printf "Starting sirius-ioc-bo-ma-correctors-ia01...\n"
	systemctl start sirius-ioc-bo-ma-correctors-ia01.service

uninstall-bo-correctors-ia01: stop-bo-correctors-ia01
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-ia01...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-ia01.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia01.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-ia02:
	@printf "Intalling sirius-ioc-bo-ma-correctors-ia02 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-ia02.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-ia02:
	@printf "Stopping sirius-ioc-bo-ma-correctors-ia02...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-ia02.service

start-bo-correctors-ia02:
	@printf "Starting sirius-ioc-bo-ma-correctors-ia02...\n"
	systemctl start sirius-ioc-bo-ma-correctors-ia02.service

uninstall-bo-correctors-ia02: stop-bo-correctors-ia02
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-ia02...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-ia02.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia02.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-ia04:
	@printf "Intalling sirius-ioc-bo-ma-correctors-ia04 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-ia04.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-ia04:
	@printf "Stopping sirius-ioc-bo-ma-correctors-ia04...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-ia04.service

start-bo-correctors-ia04:
	@printf "Starting sirius-ioc-bo-ma-correctors-ia04...\n"
	systemctl start sirius-ioc-bo-ma-correctors-ia04.service

uninstall-bo-correctors-ia04: stop-bo-correctors-ia04
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-ia04...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-ia04.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia04.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-ia05:
	@printf "Intalling sirius-ioc-bo-ma-correctors-ia05 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-ia05.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-ia05:
	@printf "Stopping sirius-ioc-bo-ma-correctors-ia05...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-ia05.service

start-bo-correctors-ia05:
	@printf "Starting sirius-ioc-bo-ma-correctors-ia05...\n"
	systemctl start sirius-ioc-bo-ma-correctors-ia05.service

uninstall-bo-correctors-ia05: stop-bo-correctors-ia05
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-ia05...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-ia05.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia05.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-ia07:
	@printf "Intalling sirius-ioc-bo-ma-correctors-ia07 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-ia07.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-ia07:
	@printf "Stopping sirius-ioc-bo-ma-correctors-ia07...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-ia07.service

start-bo-correctors-ia07:
	@printf "Starting sirius-ioc-bo-ma-correctors-ia07...\n"
	systemctl start sirius-ioc-bo-ma-correctors-ia07.service

uninstall-bo-correctors-ia07: stop-bo-correctors-ia07
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-ia07...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-ia07.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia07.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-ia08:
	@printf "Intalling sirius-ioc-bo-ma-correctors-ia08 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-ia08.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-ia08:
	@printf "Stopping sirius-ioc-bo-ma-correctors-ia08...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-ia08.service

start-bo-correctors-ia08:
	@printf "Starting sirius-ioc-bo-ma-correctors-ia08...\n"
	systemctl start sirius-ioc-bo-ma-correctors-ia08.service

uninstall-bo-correctors-ia08: stop-bo-correctors-ia08
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-ia08...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-ia08.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia08.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-ia10:
	@printf "Intalling sirius-ioc-bo-ma-correctors-ia10 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-ia10.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-ia10:
	@printf "Stopping sirius-ioc-bo-ma-correctors-ia10...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-ia10.service

start-bo-correctors-ia10:
	@printf "Starting sirius-ioc-bo-ma-correctors-ia10...\n"
	systemctl start sirius-ioc-bo-ma-correctors-ia10.service

uninstall-bo-correctors-ia10: stop-bo-correctors-ia10
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-ia10...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-ia10.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia10.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-ia11:
	@printf "Intalling sirius-ioc-bo-ma-correctors-ia11 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-ia11.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-ia11:
	@printf "Stopping sirius-ioc-bo-ma-correctors-ia11...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-ia11.service

start-bo-correctors-ia11:
	@printf "Starting sirius-ioc-bo-ma-correctors-ia11...\n"
	systemctl start sirius-ioc-bo-ma-correctors-ia11.service

uninstall-bo-correctors-ia11: stop-bo-correctors-ia11
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-ia11...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-ia11.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia11.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-ia13:
	@printf "Intalling sirius-ioc-bo-ma-correctors-ia13 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-ia13.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-ia13:
	@printf "Stopping sirius-ioc-bo-ma-correctors-ia13...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-ia13.service

start-bo-correctors-ia13:
	@printf "Starting sirius-ioc-bo-ma-correctors-ia13...\n"
	systemctl start sirius-ioc-bo-ma-correctors-ia13.service

uninstall-bo-correctors-ia13: stop-bo-correctors-ia13
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-ia13...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-ia13.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia13.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-ia14:
	@printf "Intalling sirius-ioc-bo-ma-correctors-ia14 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-ia14.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-ia14:
	@printf "Stopping sirius-ioc-bo-ma-correctors-ia14...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-ia14.service

start-bo-correctors-ia14:
	@printf "Starting sirius-ioc-bo-ma-correctors-ia14...\n"
	systemctl start sirius-ioc-bo-ma-correctors-ia14.service

uninstall-bo-correctors-ia14: stop-bo-correctors-ia14
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-ia14...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-ia14.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia14.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-ia16:
	@printf "Intalling sirius-ioc-bo-ma-correctors-ia16 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-ia16.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-ia16:
	@printf "Stopping sirius-ioc-bo-ma-correctors-ia16...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-ia16.service

start-bo-correctors-ia16:
	@printf "Starting sirius-ioc-bo-ma-correctors-ia16...\n"
	systemctl start sirius-ioc-bo-ma-correctors-ia16.service

uninstall-bo-correctors-ia16: stop-bo-correctors-ia16
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-ia16...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-ia16.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia16.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-ia17:
	@printf "Intalling sirius-ioc-bo-ma-correctors-ia17 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-ia17.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-ia17:
	@printf "Stopping sirius-ioc-bo-ma-correctors-ia17...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-ia17.service

start-bo-correctors-ia17:
	@printf "Starting sirius-ioc-bo-ma-correctors-ia17...\n"
	systemctl start sirius-ioc-bo-ma-correctors-ia17.service

uninstall-bo-correctors-ia17: stop-bo-correctors-ia17
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-ia17...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-ia17.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia17.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors-ia20:
	@printf "Intalling sirius-ioc-bo-ma-correctors-ia20 service...\n"
	cp -rf sirius-ioc-bo-ma-correctors-ia20.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-correctors-ia20:
	@printf "Stopping sirius-ioc-bo-ma-correctors-ia20...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-ia20.service

start-bo-correctors-ia20:
	@printf "Starting sirius-ioc-bo-ma-correctors-ia20...\n"
	systemctl start sirius-ioc-bo-ma-correctors-ia20.service

uninstall-bo-correctors-ia20: stop-bo-correctors-ia20
	@printf "Uninstalling sirius-ioc-bo-ma-correctors-ia20...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-ia20.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia20.service
	systemctl daemon-reload
	systemctl reset-failed

install-bo-correctors: install-bo-correctors-ia01 install-bo-correctors-ia02 install-bo-correctors-ia04 install-bo-correctors-ia05 install-bo-correctors-ia07 install-bo-correctors-ia08 install-bo-correctors-ia10 install-bo-correctors-ia11 install-bo-correctors-ia13 install-bo-correctors-ia14 install-bo-correctors-ia16 install-bo-correctors-ia17 install-bo-correctors-ia20

stop-bo-correctors: stop-bo-correctors-ia01 stop-bo-correctors-ia02 stop-bo-correctors-ia04 stop-bo-correctors-ia05 stop-bo-correctors-ia07 stop-bo-correctors-ia08 stop-bo-correctors-ia10 stop-bo-correctors-ia11 stop-bo-correctors-ia13 stop-bo-correctors-ia14 stop-bo-correctors-ia16 stop-bo-correctors-ia17 stop-bo-correctors-ia20

start-bo-correctors: start-bo-correctors-ia01 start-bo-correctors-ia02 start-bo-correctors-ia04 start-bo-correctors-ia05 start-bo-correctors-ia07 start-bo-correctors-ia08 start-bo-correctors-ia10 start-bo-correctors-ia11 start-bo-correctors-ia13 start-bo-correctors-ia14 start-bo-correctors-ia16 start-bo-correctors-ia17 start-bo-correctors-ia20

uninstall-bo-correctors: uninstall-bo-correctors-ia01 uninstall-bo-correctors-ia02 uninstall-bo-correctors-ia04 uninstall-bo-correctors-ia05 uninstall-bo-correctors-ia07 uninstall-bo-correctors-ia08 uninstall-bo-correctors-ia10 uninstall-bo-correctors-ia11 uninstall-bo-correctors-ia13 uninstall-bo-correctors-ia14 uninstall-bo-correctors-ia16 uninstall-bo-correctors-ia17 uninstall-bo-correctors-ia20

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

install-bo-injkckr:
	@printf "Intalling sirius-ioc-bo-pm-injkckr service...\n"
	cp -rf sirius-ioc-bo-pm-injkckr.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs
	chown -R sirius.sirius /home/sirius/iocs
	systemctl daemon-reload

stop-bo-injkckr:
	@printf "Stopping sirius-ioc-bo-pm-injkckr...\n"
	systemctl stop sirius-ioc-bo-pm-injkckr.service

start-bo-injkckr:
	@printf "Starting sirius-ioc-bo-pm-injkckr...\n"
	systemctl start sirius-ioc-bo-pm-injkckr.service

uninstall-bo-injkckr: stop-bo-injkckr
	@printf "Uninstalling sirius-ioc-bo-pm-injkckr...\n"
	systemctl disable sirius-ioc-bo-pm-injkckr.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-pm-injkckr.service
	systemctl daemon-reload
	systemctl reset-failed


install-bo: install-bo-correctors install-bo-dipoles install-bo-quadrupoles install-bo-sextupoles install-bo-injkckr

stop-bo: stop-bo-correctors stop-bo-dipoles stop-bo-quadrupoles stop-bo-sextupoles stop-bo-injkckr

start-bo: start-bo-correctors start-bo-dipoles start-bo-quadrupoles start-bo-sextupoles start-bo-injkckr

uninstall-bo: uninstall-bo-correctors uninstall-bo-dipoles uninstall-bo-quadrupoles uninstall-bo-sextupoles uninstall-bo-injkckr



# --- ALL ACCELERATORS ---

install-services: install-tb install-bo

stop: stop-tb stop-bo

start: start-tb start-bo

uninstall: uninstall-tb uninstall-bo
