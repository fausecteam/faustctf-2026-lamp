SERVICE := lamp
DESTDIR ?= dist_root
SERVICEDIR ?= /srv/$(SERVICE)

.PHONY: build install

build:
	echo nothing to build

install: build
	mkdir -p $(DESTDIR)$(SERVICEDIR)
	cp -r service/* $(DESTDIR)$(SERVICEDIR)
	mv $(DESTDIR)$(SERVICEDIR)/docker-compose.release.yml $(DESTDIR)$(SERVICEDIR)/docker-compose.yml
	mkdir -p $(DESTDIR)/etc/systemd/system/faustctf.target.wants/
	ln -s /etc/systemd/system/docker-compose@.service $(DESTDIR)/etc/systemd/system/faustctf.target.wants/docker-compose@$(SERVICE).service

