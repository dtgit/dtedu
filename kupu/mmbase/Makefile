# $Id: Makefile,v 1.8 2005/09/08 08:30:31 michiel Exp $


KUPU_HOME=..
XSLTPROC = /usr/bin/env xsltproc

XSL_DEBUG = --param debug true\(\)
XSLTPROC_PARAMS = --nonet --novalid --xinclude
XSL_FILE=$(KUPU_HOME)/make.xsl
XSLJSPX_FILE=$(KUPU_HOME)/make-jspx.xsl
I18N=$(KUPU_HOME)/kupu-i18n.jar

LANGS=nl de fr it eo
#type in i18n: msginit -l <locale> -i messages.po


all: index.jspx body.jspx head.jspx


index.jspx: mmbase-kupu-i18n.jar *.kupu  Makefile
	$(XSLTPROC) $(XSLTPROC_PARAMS) -o $@  $(XSLJSPX_FILE) dist-mmbase.kupu

body.jspx: mmbase-kupu-i18n.jar *.kupu  Makefile
	$(XSLTPROC) $(XSLTPROC_PARAMS) -o $@  $(XSLJSPX_FILE) body-mmbase.kupu

head.jspx: mmbase-kupu-i18n.jar *.kupu  Makefile
	$(XSLTPROC) $(XSLTPROC_PARAMS) -o $@  $(XSLJSPX_FILE) head-mmbase.kupu

$(I18N):
	@$(MAKE) -C $(KUPU_HOME) kupu-i18n.jar	

.PHONY:
messages: *.js clean
	rm -f phony.js
	grep -r "fmt:message" *.jspx *.kupu | sed 's/.*key="\(.*\)".*/_("\1");/g' | uniq > phony.js
	mkdir -p i18n
	xgettext --from-code=UTF-8 -L java -k_ -p i18n -j *.js -o en.po
	for LOCALE in $(LANGS) ; do \
	   msgmerge --update --backup=off i18n/$${LOCALE}.po i18n/en.po; \
	done

mmbase-kupu-i18n.jar: i18n/*.po
	mkdir -p resourcebundle
	for LOCALE in $(LANGS) en ; do \
	    msgfmt --java2  -D . -d resourcebundle -r org.mmbase.kupu.Messages -l $${LOCALE} i18n/$${LOCALE}.po; \
	done
	jar cf $@ -C resourcebundle org

clean:
	rm -f index.jspx
	rm -f mmbase-kupu-i18n.jar
	rm -rf resourcebundle
	@$(MAKE) -C $(KUPU_HOME) clean
