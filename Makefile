define USEAGE 
This is the build script for openmolar packages.

USAGE
   make [options] target

OPTIONS
   DIST  (the target distribution - eg. unstable, testing, lucid etc.)
       default=unstable
       allowed values - anything.. 
       but if building a deb, have a pbuilder environment with this name
   NEW_CHANGELOG (run a gui to modify the global changelog)
       default=true

TARGETS
   deb_src
   deb
   deb_srcs
   debs

EXAMPLES

	make changelog
		update the changelog in the template debian directory
	make deb DIST=stable
		debian packages for debian stable (squeeze)
	make deb DIST=precise 
		create a debian binary package for ubuntu precise (12.04).
	make debs 
		makes debian package for all distributions and architectures
	make nightly_builds
		should be self explanatory?

endef
	
export USEAGE

ifeq ($(DIST), )
	DIST=unstable
endif

ifeq ($(NEW_CHANGELOG), )
	NEW_CHANGELOG=true
endif

PACKAGE=openmolar

CURRENT_MAKEFILE_LIST := $(MAKEFILE_LIST)
BUILD_SCRIPTS_DIR := $(abspath $(dir $(firstword $(CURRENT_MAKEFILE_LIST))))/
HEAD = $(shell $(BUILD_SCRIPTS_DIR)get_git_branch.py)/
BUILDS_DIR=$(HEAD)builds/

DIST_DIR=$(HEAD)dist/

#VERSION=`git describe | sed s/v//`
VERSION=`$(BUILD_SCRIPTS_DIR)get_version.py`

TARBALL_DIR=$(HEAD)tarballs/
TARBALL = $(shell ls -t $(TARBALL_DIR) | grep .tar.gz$$ | head -n1)
UNTARRED = $(shell echo $(TARBALL) | sed s/.tar.gz//)
ORIG = $(shell echo $(UNTARRED).orig.tar.gz | sed s/openmolar-/openmolar_/)

TMP_DIR=$(HEAD)tmp/

###################  Debian Packaging Stuff ####################################
#                                                                              #
DEB_CONF_DIR=$(BUILD_SCRIPTS_DIR)debian/
DEB_BUILDS_DIR=$(BUILDS_DIR)debs/$(DIST)/
DEBDISTS = testing unstable stable oldstable
CHANGELOG=$(DEB_BUILDS_DIR)$(shell ls -t $(DEB_BUILDS_DIR) | grep changes | head -n1)
#                                                                              #
##################  Debian packaging ends  #####################################


##################  Ubuntu Packaging Stuff #####################################
#            Updated April 2014 (EOL for 13.04 and 12.10)                      #
#            Also update ~/.pbuilderrc					       #
DEBDISTS += trusty saucy precise
#                                                                              #
##################  Ubuntu packaging ends  #####################################

.phony:
	make help

help:
	@echo "$$USEAGE"
	
clean_tmp:
	mkdir -p $(TMP_DIR)
	rm -rf $(TMP_DIR)*

changelog:
	@echo "call deb_maker.py -p$(PACKAGE) -s$(TARBALL_DIR) -d$(DEB_CONF_DIR)"
	$(BUILD_SCRIPTS_DIR)deb_maker.py -p$(PACKAGE) -s$(TARBALL_DIR) -d$(DEB_CONF_DIR) $(AUTO)

deb:
	make clean_tmp

	@echo "Making debian packages target distro = $(DIST)"
		
	@if [ "$(NEW_CHANGELOG)" = 'true' ]; then make changelog; fi
	
	cp -av $(TARBALL_DIR)$(TARBALL) $(TMP_DIR)
	
	cd $(TMP_DIR) ;\
	tar -zxf $(TARBALL); \
	mv $(TARBALL) $(ORIG)

	cd $(TMP_DIR)$(UNTARRED) ; \
	cp -av $(DEB_CONF_DIR) . ;\
	echo "modding changelog" ;\
	sed -i s/__DIST__/$(DIST)/g debian/changelog ;\
	sudo pdebuild --buildresult $(DEB_BUILDS_DIR) --pbuilderroot "sudo DIST=$(DIST)"
	
debsign:
	debsign $(DEB_BUILDS_DIR)*$(VERSION)*.changes -kF230408E 
	
debsigns:
	#make debsign DIST=<unstable|testing|stable|raring|quantal|precise|lucid> 
	
	$(foreach dist,$(DEBDISTS), \
		make debsign DIST=$(dist) ;\
	)
	
notes:
	#pdebuild --architecture <i386|amd64>  --buildresult /tmp --pbuilderroot "sudo DIST=<unstable|stable|testing|raring|quantal|precise|lucid> ARCH=<i386|amd64>"
	
debs:
	@echo "making all debian based packages.. first we need to update the changelogs for the 2 build systems"

	$(foreach dist,$(DEBDISTS), \
		make deb DIST=$(dist) NEW_CHANGELOG=False;\
	) 
	
pushdeb:
	cd ~/www/repos/apt/debian ;\
	reprepro include $(DIST) $(CHANGELOG) ; \
	#reprepro export
	
pushdebs:
	@echo "updating the local repo"
	$(foreach dist,$(DEBDISTS), \
		make DIST=$(dist) pushdeb; \
	)
	cd ~/www/repos/apt/debian ;\
	reprepro export

nightly_builds:
	make AUTO=--auto changelog
	make debs

update_pbuilder:
	$(foreach dist, $(DEBDISTS), \
		sudo DIST=${dist} ARCH=amd64 pbuilder --update --architecture amd64 \
		--distribution ${dist} --http-proxy http://localhost:3142 ; \
	)
	
create_pbuilder:
	$(foreach dist, $(DEBDISTS), \
		sudo DIST=${dist} ARCH=amd64 pbuilder --create --architecture amd64 \
		--distribution ${dist} --http-proxy http://localhost:3142 ; \
	)

test:
	@echo chosen package $(PACKAGE)
	@echo targetting distro $(DIST)
	@if [ $(NEW_CHANGELOG) = 'true' ]; then \
		echo changelog WILL be updated; \
	fi
	@echo DEBDISTS = $(DEBDISTS)
	@echo debconfdir = $(DEB_CONF_DIR)
	@echo Head = $(HEAD)
	@echo Dist = $(DIST)
	@echo DEB_BUILDS_DIR = $(DEB_BUILDS_DIR)
	@echo changelog = $(CHANGELOG)
	@echo tarball = $(TARBALL)
	@echo tmpdir = $(TMP_DIR)
