# TODO
# - proper webapps integration: make config not accessible from web
Summary:	UebiMiau - simple POP3 mail reader
Summary(pl.UTF-8):	UebiMiau - prosty czytnik poczty POP3
Name:		uebimiau
Version:	2.7.10
Release:	1
License:	GPL
Group:		Applications/Mail
Source0:	http://www.uebimiau.org/downloads/%{name}-%{version}-any.zip
# Source0-md5:	859cae1133aa088823d78acbbeb3baa2
Patch0:		%{name}-folders.patch
Patch1:		%{name}-smarty.patch
Patch2:		%{name}-pl-fixes.patch
Patch3:		%{name}-header.patch
Patch4:		%{name}-language.patch
URL:		http://www.uebimiau.org/
BuildRequires:	rpmbuild(macros) >= 1.461
BuildRequires:	sed >= 4.1.1
# BR: rpm - not for Ra where is wrong def. of %%{_sharedstatedir}.
BuildRequires:	rpm >= 4.3
BuildRequires:	unzip
Requires:	Smarty >= 2.6.10-3
Requires:	sed >= 4.1.1
Requires:	webapps
Provides:	webmail
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir		%{_datadir}/%{name}
%define		_smartydir	%{php_data_dir}/Smarty
%define		_sysconfdir	/etc/%{name}
%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_sysconfdir	%{_webapps}/%{_webapp}

%description
UebiMiau is a web-based e-mail client written in PHP. It has some
features, such as: Folders, View and Send Attachments, Preferences,
Search, Quota Limit, etc. UebiMiau does not require database or IMAP.

%description -l pl.UTF-8
UebiMiau jest napisanym w PHP klientem poczty elektronicznej. Jego
możliwości to m.in. obsługa folderów, przeglądania i wysyłania
załączników, preferencji, wyszukiwania, quoty i inne. UebiMiau nie
wymaga bazy danych ani IMAP.

%prep
%setup -q -n webmail

# undos the source
find . -name '*.php' -print0 | xargs -0 sed -i -e 's,\r$,,'

%patch -P0 -p1
%patch -P1 -p1
%patch -P2 -p1
%patch -P3 -p1
%patch -P4 -p1

# prepare apache config file
cat > apache.conf <<'EOF'
Alias /%{name} %{_appdir}
<Directory %{_appdir}>
	Order Allow,Deny
	Allow From All
</Directory>
EOF

%{__sed} -i "s|\$temporary_directory = \"database/\";|\$temporary_directory = \"%{_sharedstatedir}/%{name}/\";|" inc/config.php
for f in index.php badlogin.php error.php inc/inc.php; do
	%{__sed} -i "s|define(\"SMARTY_DIR\",\"./smarty/\");|define(\"SMARTY_DIR\",\"%{_smartydir}/\");|" $f
done

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_sharedstatedir}/%{name}}
install -d $RPM_BUILD_ROOT%{_appdir}/{database,extra,images,inc,langs,themes/uebimiau}

install *.php			$RPM_BUILD_ROOT%{_appdir}
install database/index.php	$RPM_BUILD_ROOT%{_appdir}/database
install extra/*			$RPM_BUILD_ROOT%{_appdir}/extra
install images/*		$RPM_BUILD_ROOT%{_appdir}/images
install inc/*			$RPM_BUILD_ROOT%{_appdir}/inc
install langs/*			$RPM_BUILD_ROOT%{_appdir}/langs
install themes/debug.tpl	$RPM_BUILD_ROOT%{_appdir}/themes
cp -a  themes/uebimiau/*	$RPM_BUILD_ROOT%{_appdir}/themes/uebimiau
install apache.conf 		$RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
install apache.conf 		$RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf

mv $RPM_BUILD_ROOT%{_appdir}/inc/config{,.languages,.security}.php	$RPM_BUILD_ROOT%{_sysconfdir}
ln -s %{_sysconfdir}/config.php		$RPM_BUILD_ROOT%{_appdir}/inc/config.php
ln -s %{_sysconfdir}/config.languages.php	$RPM_BUILD_ROOT%{_appdir}/inc/config.languages.php
ln -s %{_sysconfdir}/config.security.php	$RPM_BUILD_ROOT%{_appdir}/inc/config.security.php

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

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

%triggerpostun -- %{name} < 2.7.8-9.RC1.4.5
# rescue app config
for i in config.languages.php config.php config.security.php; do
	if [ -f /etc/%{name}/$i.rpmsave ]; then
		mv -f %{_sysconfdir}/$i{,.rpmnew}
		mv -f /etc/%{name}/$i.rpmsave %{_sysconfdir}/$i
	fi
done

# nuke very-old config location (this mostly for Ra)
if [ -f /etc/httpd/httpd.conf ]; then
	sed -i -e "/^Include.*%{name}.conf/d" /etc/httpd/httpd.conf
	httpd_reload=1
fi

# migrate from httpd (apache2) config dir
if [ -f /etc/httpd/%{name}.conf.rpmsave ]; then
	cp -f %{_sysconfdir}/httpd.conf{,.rpmnew}
	mv -f /etc/httpd/%{name}.conf.rpmsave %{_sysconfdir}/httpd.conf
	httpd_reload=1
fi

# migrate from apache-config macros
if [ -f /etc/%{name}/apache.conf.rpmsave ]; then
	if [ -d /etc/apache/webapps.d ]; then
		cp -f %{_sysconfdir}/apache.conf{,.rpmnew}
		cp -f /etc/%{name}/apache.conf.rpmsave %{_sysconfdir}/apache.conf
	fi

	if [ -d /etc/httpd/webapps.d ]; then
		cp -f %{_sysconfdir}/httpd.conf{,.rpmnew}
		cp -f /etc/%{name}/apache.conf.rpmsave %{_sysconfdir}/httpd.conf
	fi
	rm -f /etc/%{name}/apache.conf.rpmsave
fi

# place new config location, as trigger puts config only on first install, do it here.
if [ -L /etc/apache/conf.d/99_%{name}.conf ]; then
	rm -f /etc/apache/conf.d/99_%{name}.conf
	/usr/sbin/webapp register apache %{_webapp}
	apache_reload=1
fi
if [ -L /etc/httpd/httpd.conf/99_%{name}.conf ]; then
	rm -f /etc/httpd/httpd.conf/99_%{name}.conf
	/usr/sbin/webapp register httpd %{_webapp}
	httpd_reload=1
fi

if [ "$httpd_reload" ]; then
	%service httpd reload
fi
if [ "$apache_reload" ]; then
	%service apache reload
fi

%files
%defattr(644,root,root,755)
%doc docs/*
%attr(750,root,http) %dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
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
%{_appdir}/themes/uebimiau

%dir %attr(770,root,http) %{_sharedstatedir}/%{name}
