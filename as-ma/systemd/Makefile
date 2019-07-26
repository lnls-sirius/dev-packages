preparation:
	@printf "Preparing /home/sirius/iocs-log...\n"
	mkdir -p /home/sirius/iocs-log
	chown -R sirius.sirius /home/sirius/iocs-log







# --- TB ---
install-tb-ma: preparation
	@printf "Intalling sirius-ioc-tb-ma services...\n"
	cp -rf sirius-ioc-tb-ma-dipoles.service /etc/systemd/system/
	cp -rf sirius-ioc-tb-ma-quadrupoles.service /etc/systemd/system/
	cp -rf sirius-ioc-tb-ma-correctors.service /etc/systemd/system/

install-tb-pm: preparation
	@printf "Intalling sirius-ioc-tb-pm services...\n"
	cp -rf sirius-ioc-tb-pm-injsept.service /etc/systemd/system/

stop-tb-ma:
	@printf "Stopping sirius-ioc-tb-ma services...\n"
	systemctl stop sirius-ioc-tb-ma-correctors.service
	systemctl stop sirius-ioc-tb-ma-quadrupoles.service
	systemctl stop sirius-ioc-tb-ma-dipoles.service

stop-tb-pm:
	@printf "Stopping sirius-ioc-tb-pm services...\n"
	systemctl stop sirius-ioc-tb-pm-injsept.service

start-tb-ma: preparation
	@printf "Starting sirius-ioc-tb-ma services...\n"
	systemctl start sirius-ioc-tb-ma-dipoles.service
	systemctl start sirius-ioc-tb-ma-quadrupoles.service
	systemctl start sirius-ioc-tb-ma-correctors.service

start-tb-pm: preparation
	@printf "Starting sirius-ioc-tb-pm services...\n"
	systemctl start sirius-ioc-tb-pm-injsept.service

disable-tb-ma:
	@printf "Disabling sirius-ioc-tb-ma services...\n"
	systemctl disable sirius-ioc-tb-ma-dipoles.service
	systemctl disable sirius-ioc-tb-ma-quadrupoles.service
	systemctl disable sirius-ioc-tb-ma-correctors.service

disable-tb-pm:
	@printf "Disabling sirius-ioc-tb-pm services...\n"
	systemctl disable sirius-ioc-tb-pm-injsept.service

uninstall-tb-ma: stop-tb-ma disable-tb-ma
	@printf "Uninstalling sirius-ioc-tb-ma services...\n"
	rm -rf /etc/systemd/system/sirius-ioc-tb-ma-dipoles.service
	rm -rf /etc/systemd/system/sirius-ioc-tb-ma-quadrupoles.service
	rm -rf /etc/systemd/system/sirius-ioc-tb-ma-correctors.service
	systemctl daemon-reload
	systemctl reset-failed

uninstall-tb-pm: stop-tb-pm disable-tb-pm
	@printf "Uninstalling sirius-ioc-tb-pm services...\n"
	rm -rf /etc/systemd/system/sirius-ioc-tb-pm-injsept.service
	systemctl daemon-reload
	systemctl reset-failed


install-tb: install-tb-ma install-tb-pm
stop-tb: stop-tb-ma stop-tb-pm
start-tb: start-tb-ma start-tb-pm
uninstall-tb: uninstall-tb-ma uninstall-tb-pm
# --- BO ---
install-bo-ma: preparation
	@printf "Installing sirius-ioc-bo-ma services...\n"
	cp -rf sirius-ioc-bo-ma-dipoles.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ma-quadrupoles.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ma-sextupoles.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ma-correctors-ia01.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ma-correctors-ia02.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ma-correctors-ia04.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ma-correctors-ia05.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ma-correctors-ia07.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ma-correctors-ia08.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ma-correctors-ia10.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ma-correctors-ia11.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ma-correctors-ia13.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ma-correctors-ia14.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ma-correctors-ia16.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ma-correctors-ia17.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ma-correctors-ia20.service /etc/systemd/system/
	systemctl daemon-reload

install-bo-pm: preparation
	@printf "Installing sirius-ioc-bo-pm services...\n"
	cp -rf sirius-ioc-bo-pm-injkckr.service /etc/systemd/system/
	systemctl daemon-reload

stop-bo-ma:
	@printf "Stopping sirius-ioc-bo-ma services...\n"
	systemctl stop sirius-ioc-bo-ma-correctors-ia01.service
	systemctl stop sirius-ioc-bo-ma-correctors-ia02.service
	systemctl stop sirius-ioc-bo-ma-correctors-ia04.service
	systemctl stop sirius-ioc-bo-ma-correctors-ia05.service
	systemctl stop sirius-ioc-bo-ma-correctors-ia07.service
	systemctl stop sirius-ioc-bo-ma-correctors-ia08.service
	systemctl stop sirius-ioc-bo-ma-correctors-ia10.service
	systemctl stop sirius-ioc-bo-ma-correctors-ia11.service
	systemctl stop sirius-ioc-bo-ma-correctors-ia13.service
	systemctl stop sirius-ioc-bo-ma-correctors-ia14.service
	systemctl stop sirius-ioc-bo-ma-correctors-ia16.service
	systemctl stop sirius-ioc-bo-ma-correctors-ia17.service
	systemctl stop sirius-ioc-bo-ma-correctors-ia20.service
	systemctl stop sirius-ioc-bo-ma-sextupoles.service
	systemctl stop sirius-ioc-bo-ma-quadrupoles.service
	systemctl stop sirius-ioc-bo-ma-dipoles.service

stop-bo-pm:
	@printf "Stopping sirius-ioc-bo-pm services...\n"
	systemctl stop sirius-ioc-bo-pm-injkckr.service

start-bo-ma: preparation
	@printf "Starting sirius-ioc-bo-ma services...\n"
	systemctl start sirius-ioc-bo-ma-correctors-ia01.service
	systemctl start sirius-ioc-bo-ma-correctors-ia02.service
	systemctl start sirius-ioc-bo-ma-correctors-ia04.service
	systemctl start sirius-ioc-bo-ma-correctors-ia05.service
	systemctl start sirius-ioc-bo-ma-correctors-ia07.service
	systemctl start sirius-ioc-bo-ma-correctors-ia08.service
	systemctl start sirius-ioc-bo-ma-correctors-ia10.service
	systemctl start sirius-ioc-bo-ma-correctors-ia11.service
	systemctl start sirius-ioc-bo-ma-correctors-ia13.service
	systemctl start sirius-ioc-bo-ma-correctors-ia14.service
	systemctl start sirius-ioc-bo-ma-correctors-ia16.service
	systemctl start sirius-ioc-bo-ma-correctors-ia17.service
	systemctl start sirius-ioc-bo-ma-correctors-ia20.service
	systemctl start sirius-ioc-bo-ma-sextupoles.service
	systemctl start sirius-ioc-bo-ma-quadrupoles.service
	systemctl start sirius-ioc-bo-ma-dipoles.service

start-bo-pm: preparation
	@printf "Starting sirius-ioc-bo-pm services...\n"
	systemctl start sirius-ioc-bo-pm-injkckr.service




disable-bo-ma:
	@printf "Disabling sirius-ioc-bo-ma services...\n"
	systemctl disable sirius-ioc-bo-ma-correctors-ia01.service
	systemctl disable sirius-ioc-bo-ma-correctors-ia02.service
	systemctl disable sirius-ioc-bo-ma-correctors-ia04.service
	systemctl disable sirius-ioc-bo-ma-correctors-ia05.service
	systemctl disable sirius-ioc-bo-ma-correctors-ia07.service
	systemctl disable sirius-ioc-bo-ma-correctors-ia08.service
	systemctl disable sirius-ioc-bo-ma-correctors-ia10.service
	systemctl disable sirius-ioc-bo-ma-correctors-ia11.service
	systemctl disable sirius-ioc-bo-ma-correctors-ia13.service
	systemctl disable sirius-ioc-bo-ma-correctors-ia14.service
	systemctl disable sirius-ioc-bo-ma-correctors-ia16.service
	systemctl disable sirius-ioc-bo-ma-correctors-ia20.service
	systemctl disable sirius-ioc-bo-ma-sextupoles.service
	systemctl disable sirius-ioc-bo-ma-quadrupoles.service
	systemctl disable sirius-ioc-bo-ma-dipoles.service

disable-bo-pm:
	@printf "Disabling sirius-ioc-bo-pm services...\n"




uninstall-bo-ma: stop-bo-ma disable-bo-ma
	@printf "Uninstalling sirius-ioc-bo-ma services...\n"
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia01.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia02.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia04.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia05.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia07.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia08.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia10.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia11.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia13.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia14.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia16.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia17.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-correctors-ia20.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-sextupoles.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-quadrupoles.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ma-dipoles.service
	systemctl daemon-reload
	systemctl reset-failed

uninstall-bo-pm: stop-bo-pm disable-bo-pm
	@printf "Uninstalling sirius-ioc-bo-pm services...\n"
	rm -rf /etc/systemd/system/sirius-ioc-bo-pm-injkckr.service
	systemctl daemon-reload
	systemctl reset-failed


install-bo: install-bo-ma install-bo-pm
stop-bo: stop-bo-ma stop-bo-pm
start-bo: start-bo-ma start-bo-pm
uninstall-bo: uninstall-bo-ma uninstall-bo-pm
# --- ALL ACCELERATORS ---
install-services: install-tb install-bo
stop: stop-tb stop-bo
start: start-tb start-bo
uninstall: uninstall-tb uninstall-bo
