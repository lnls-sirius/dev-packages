# Makefile for Doxygen documentation

DOXYFILE = Doxyfile
LOCAL_DIR = as-high-level-timing
PROJECT_DIR = $(LNLS_SIRIUS)/hla/machine_apps/$(LOCAL_DIR)/$(LOCAL_DIR)
DOC_DIR = $(LNLS_SIRIUS)/hla/machine_apps/$(LOCAL_DIR)/doc/doxygen
PROJECT_NUMBER = $(shell cat $(PROJECT_DIR)/VERSION)

html:
	( cat $(DOXYFILE) ; \
	  echo "PROJECT_NUMBER=$(PROJECT_NUMBER)" ; \
		echo "INPUT = $(PROJECT_DIR) $(DOC_DIR)" ) | doxygen -
	ln -s html/index.html documentation.html

clean:
	rm -rf html
	rm documentation.html
