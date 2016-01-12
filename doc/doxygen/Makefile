# Makefile for Doxygen documentation

DOXYFILE = Doxyfile

html:
	doxygen $(DOXYFILE)
	ln -s html/index.html documentation.html

clean:
	rm -rf html
	rm documentation.html
