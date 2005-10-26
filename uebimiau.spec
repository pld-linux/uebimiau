Summary:	UebiMiau - simple POP3 mail reader
Summary(pl):	UebiMiau - prosty czytnik poczty POP3
Name:		uebimiau
Version:	2.7.8
%define		_rc	RC1
%define		_rel 4.3
Release:	9.%{_rc}.%{_rel}
License:	GPL
Group:		Applications/Mail
Source0:	http://www.uebimiau.org/downloads/%{name}-%{version}-%{_rc}-any.tar.gz
# Source0-md5:	20e355ef9535deb49b8866cd93b661af
Patch0:		%{name}-bugfixes.patch
Patch1:		%{name}-folders.patch
Patch2:		%{name}-smarty.patch
Patch3:		%{name}-pl-fixes.patch
Patch4:		%{name}-focus.patch
URL:		http://www.uebimiau.org/
BuildRequires:	sed >= 4.1.1
BuildRequires:	rpmbuild(macros) >= 1.226
# BR: rpm - not for Ra where is wrong def. of %%{_sharedstatedir}.
BuildRequires:	rpm >= 4.3
Requires:	Smarty >= 2.6.10-3
Requires:	sed >= 4.1.1
Requires:	webserver
Provides:	webmail
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir		%{_datadir}/%{name}
%define		_smartydir	%{_datadir}/php/Smarty
%define		_sysconfdir	/etc/%{name}

%description
UebiMiau is a web-based e-mail client written in PHP. It has some
features, such as: Folders, View and Send Attachments, Preferences,
Search, Quota Limit, etc. UebiMiau does not require database or IMAP.

%description -l pl
UebiMiau jest napisanym w PHP klientem poczty elektronicznej. Jego
mo¿liwo¶ci to m.in. obs³uga folderów, przegl±dania i wysy³ania
za³±czników, preferencji, wyszukiwania, quoty i inne. UebiMiau nie
wymaga bazy danych ani IMAP.

%prep
%setup -q -n %{name}-%{version}-%{_rc}-any
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

# undos the source
find . -name '*.php' -print0 | xargs -0 sed -i -e 's,\r$,,'

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_sharedstatedir}/%{name}}
install -d $RPM_BUILD_ROOT%{_appdir}/{database,extra,images,inc,langs,themes/default}

%{__sed} -i "s|\$temporary_directory = \"./database/\";|\$temporary_directory = \"%{_sharedstatedir}/%{name}/\";|" inc/config.php
for f in index.php badlogin.php error.php inc/inc.php; do
	%{__sed} -i "s|define(\"SMARTY_DIR\",\"./smarty/\");|define(\"SMARTY_DIR\",\"%{_smartydir}/\");|" $f
done

install *.php			$RPM_BUILD_ROOT%{_appdir}
install database/index.php	$RPM_BUILD_ROOT%{_appdir}/database
install extra/*			$RPM_BUILD_ROOT%{_appdir}/extra
install images/*		$RPM_BUILD_ROOT%{_appdir}/images
install inc/*			$RPM_BUILD_ROOT%{_appdir}/inc
install langs/*			$RPM_BUILD_ROOT%{_appdir}/langs
install themes/debug.tpl	$RPM_BUILD_ROOT%{_appdir}/themes
install themes/default/*	$RPM_BUILD_ROOT%{_appdir}/themes/default
echo "Alias /%{name} %{_appdir}" > $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf

mv $RPM_BUILD_ROOT%{_appdir}/inc/config{,.languages,.security}.php	$RPM_BUILD_ROOT%{_sysconfdir}
ln -s %{_sysconfdir}/config.php		$RPM_BUILD_ROOT%{_appdir}/inc/config.php
ln -s %{_sysconfdir}/config.languages.php	$RPM_BUILD_ROOT%{_appdir}/inc/config.languages.php
ln -s %{_sysconfdir}/config.security.php	$RPM_BUILD_ROOT%{_appdir}/inc/config.security.php

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f %{_sysconfdir}/httpd/httpd.conf ] && ! grep -q "^Include.*%{name}.conf" %{_sysconfdir}/httpd/httpd.conf; then
	echo "Include %{_sysconfdir}/httpd/%{name}.conf" >> %{_sysconfdir}/httpd/httpd.conf
elif [ -d %{_sysconfdir}/httpd/httpd.conf ]; then
	ln -sf %{_sysconfdir}/httpd/%{name}.conf %{_sysconfdir}/httpd/httpd.conf/99_%{name}.conf
fi
if [ -f /var/lock/subsys/httpd ]; then
	%{_sbindir}/apachectl restart 1>&2
fi

%preun
if [ "$1" = "0" ]; then
	umask 027
	if [ -d %{_sysconfdir}/httpd/httpd.conf ]; then
		rm -f %{_sysconfdir}/httpd/httpd.conf/99_%{name}.conf
	else
		grep -v "^Include.*%{name}.conf" %{_sysconfdir}/httpd/httpd.conf > \
			%{_sysconfdir}/httpd/httpd.conf.tmp
		mv -f %{_sysconfdir}/httpd/httpd.conf.tmp %{_sysconfdir}/httpd/httpd.conf
		if [ -f /var/lock/subsys/httpd ]; then
			%{_sbindir}/apachectl restart 1>&2
		fi
	fi
fi

%triggerin -- apache1 >= 1.3.33-2
%apache_config_install -v 1 -c %{_sysconfdir}/apache.conf

%triggerun -- apache1 >= 1.3.33-2
%apache_config_uninstall -v 1

%triggerin -- apache >= 2.0.0
%apache_config_install -v 2 -c %{_sysconfdir}/apache.conf

%triggerun -- apache >= 2.0.0
%apache_config_uninstall -v 2

%triggerun -- %{name} < 2.7.8-5.RC1
RADIR=/home/httpd/html/uebimiau/inc
ACDIR=/home/services/httpd/html/uebimiau/inc
if [ -d "$RADIR" -o -d "$ACDIR" ] ; then
	echo -e	"\n###############################################################################\n"
	echo	"Moving %{name} contents of configuration files to new location in"
	echo	"(%{_sysconfdir}/%{name}/) ..."
	echo	"If something fails run sudo rpm -e --allmatches uebimiau and move configuration"
	echo	"files and contents of \$temprorary_directory by hand."
	if [ -d "${RADIR}" -a -d "${ACDIR}" ] ; then
		echo	"ERROR: Moving fails - system contains both directories:"
		echo	"$RADIR"
		echo	"$ACDIR"
		echo	"Remove by hand this one which does not contain proper configuration files and data."
		echo	"And try again."
		echo -e	"\n###############################################################################\n"
		exit 1
	fi
	if [ -d "$RADIR" ] ; then
		CDIR="$RADIR"
	elif [ -d "$ACDIR" ] ; then
		CDIR="$ACDIR"
	else
		echo "ERROR: Script failed - hgw."
		exit 1
	fi
	if [ -d "${CDIR}" ] ; then
		umask 022
		CFS=$(find "${CDIR}" -name "config*.php")
		for CF in $CFS ; do
			cat "$CF" > %{_sysconfdir}/%{name}/$(basename "$CF")
		done
		%{__sed} -i \
			"s|\$temporary_directory = \".*\"|\$temporary_directory = \"%{_sharedstatedir}/%{name}/\";|" \
			%{_sysconfdir}/%{name}/config.php
		chmod 644 %{_sysconfdir}/%{name}/*
		echo -e	"\n###############################################################################\n"
		echo	"Done."
		echo -e	"\n###############################################################################\n"
		echo	"Now you *must* move by hand %{name} data (see \$temprorary_directory"
		echo	"in ${CDIR}/config.php.rpmsave where they are)\nto /var/lib/%{name}/ . "
		echo -e	"\n###############################################################################\n"
	fi
fi

%triggerpostun -- uebimiau < 2.7.8-8.RC1.4.1
# migrate from old config location (only apache2, as there was no apache1 support)
if [ -f /etc/httpd/%{name}.conf.rpmsave ]; then
	cp -f %{_sysconfdir}/apache.conf{,.rpmnew}
	mv -f /etc/httpd/%{name}.conf.rpmsave %{_sysconfdir}/apache.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd reload 1>&2
	fi
fi

# nuke very-old config location (this mostly for Ra)
if [ ! -d /etc/httpd/httpd.conf ]; then
	sed -i -e "/^Include.*%{name}.conf/d" /etc/httpd/httpd.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd reload 1>&2
	fi
fi

# place new config location, as trigger puts config only on first install, do it here.
# apache1
if [ -d /etc/apache/conf.d ]; then
	ln -sf %{_sysconfdir}/apache.conf /etc/apache/conf.d/99_%{name}.conf
	if [ -f /var/lock/subsys/apache ]; then
		/etc/rc.d/init.d/apache reload 1>&2
	fi
fi
# apache2
if [ -d /etc/httpd/httpd.conf ]; then
	ln -sf %{_sysconfdir}/apache.conf /etc/httpd/httpd.conf/99_%{name}.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd reload 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc CHANGELOG.txt INSTALL.txt README.txt
%attr(750,root,http) %dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*.php

%dir %{_appdir}
%{_appdir}/*.php
%{_appdir}/database
%{_appdir}/extra
%{_appdir}/images
%{_appdir}/inc
%{_appdir}/langs
%dir %{_appdir}/themes
%{_appdir}/themes/debug.tpl
%{_appdir}/themes/default

%dir %attr(770,root,http) %{_sharedstatedir}/%{name}
