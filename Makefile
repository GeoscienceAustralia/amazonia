#
# This makefile installs the amazonia package and its dependencies
#
# To install Amazonia run "make install"
# See the readme.md for more information.
# Have fun!


.PHONEY:
build:
	python3 setup.py build

.PHONEY:
install:
	pip3 install -e . --user

.PHONEY:
uninstall:
	yes | pip3 uninstall amazonia

.PHONEY:
clean:
	rm -rf *.template *.json build dist *.egg-info
