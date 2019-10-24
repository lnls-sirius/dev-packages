install: clean install-scripts install-services

develop: clean install-services
	sudo ./setup.py develop

clean:
	git clean -fdX

install-scripts: clean
	sudo ./setup.py install --single-version-externally-managed --compile --force --record /dev/null

install-services:
	cd systemd; sudo make install-services
