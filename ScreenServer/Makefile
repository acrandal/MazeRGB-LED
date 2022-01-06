
INSTALL_DIR=/usr/local/rgbScreenServer
SYSTEMD_DIR=/lib/systemd/system

install:
	cp maze.service $(SYSTEMD_DIR)/
	mkdir -p $(INSTALL_DIR)
	cp rgbScreenServer.py samplebase.py $(INSTALL_DIR)/

restart:
	service maze restart

status:
	service maze status

stop:
	service maze stop