#! /usr/bin/make -f
# :vim: filetype=make : -*- makefile; coding: utf-8; -*-

# Makefile
# Part of Bugs Everywhere, a distributed bug tracking system.
#
# Copyright (C) 2008-2012 Anton Batenev <abbat@abbat>
#                         Ben Finney <benf@cybersource.com.au>
#                         Chris Ball <cjb@laptop.org>
#                         Eric Kow <eric.kow@gmail.com>
#                         Gianluca Montecchi <gian@grys.it>
#                         Matěj Cepl <mcepl@redhat.com>
#                         W. Trevor King <wking@drexel.edu>
#
# This file is part of Bugs Everywhere.
#
# Bugs Everywhere is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option) any
# later version.
#
# Bugs Everywhere is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Bugs Everywhere.  If not, see <http://www.gnu.org/licenses/>.

SHELL = /bin/bash
RM = /bin/rm
RST2MAN = /usr/bin/rst2man
RST2HTML = /usr/bin/rst2html

#PATH = /usr/bin:/bin  # must include sphinx-build for 'sphinx' target.

#INSTALL_OPTIONS = "--prefix=/usr/local"
INSTALL_OPTIONS = "--user"

# Select the documentation you wish to build
DOC = sphinx man

# Directories with semantic meaning
DOC_DIR := doc
MAN_DIR := ${DOC_DIR}/man

MANPAGES = be.1
LIBBE_VERSION := libbe/_version.py
GENERATED_FILES := build $(LIBBE_VERSION)

MANPAGE_FILES = $(patsubst %,${MAN_DIR}/%,${MANPAGES})
MANPAGE_HTML =  $(patsubst %,${MAN_DIR}/%.html,${MANPAGES})
GENERATED_FILES += ${MANPAGE_FILES} ${MANPAGE_HTML}


.PHONY: all
all: build


.PHONY: build
build: $(LIBBE_VERSION)
	python setup.py build

.PHONY: doc
doc: $(DOC)

.PHONY: install
install: build doc
	python setup.py install ${INSTALL_OPTIONS}

test: build
	python test.py

.PHONY: clean
clean:
	$(RM) -rf ${GENERATED_FILES}
	$(MAKE) -C ${DOC_DIR} clean


.PHONY: libbe/_version.py
libbe/_version.py:
	echo "# -*- coding: utf-8 -*-" > $@
	git log -1 --encoding=UTF-8 --date=short --pretty='format:"Autogenerated by make libbe/_version.py"%nversion_info = {%n    "date":"%cd",%n    "revision":"%H",%n    "committer":"%cn"}%n' >> $@

.PHONY: man
man: ${MANPAGE_FILES}

%.1: %.1.txt
	$(RST2MAN) $< > $@
%.1.html: %.1.txt
	$(RST2HTML) $< > $@

.PHONY: sphinx
sphinx:
	$(MAKE) -C ${DOC_DIR} html
