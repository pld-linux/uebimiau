Summary:	UebiMiau - Simple POP3 Mail Reader
Summary(pl):	UebiMiau - Prosty czytnik poczty POP3
Name:		uebimiau
Version:	2.7.8
%define		sub_ver	RC1
Release:	6.%{sub_ver}
License:	GPL
Group:		Applications/Mail
Vendor:		Aldoir Ventura <aldoir@users.sourceforge.net>
Source0:	http://www.uebimiau.org/downloads/%{name}-%{version}-%{sub_ver}-any.tar.gz
# Source0-md5:	20e355ef9535deb49b8866cd93b661af
# Source0-size:	196571
Patch0:		%{name}-attachment,readmsg.patch
URL:		http://www.uebimiau.org/
BuildRequires:	sed >= 4.1.1
# BR: rpm - not for Ra where is wrong def. of %%{_sharedstatedir}.
BuildRequires:	rpm >= 4.3
Requires:	php
Requires:	php-pcre
Requires:	sed >= 4.1.1
Requires:	webserver
Provides:	webmail
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
UebiMiau is a web-based e-mail client written in PHP. It's have some
features, such as: Folders, View and Send Attachments, Preferences,
Search, Quota Limit, etc. UebiMiau does not require database or IMAP.

%description -l pl
UebiMiau jest napisanym w PHP klientem poczty elektronicznej. Jego
mo¿liwo¶ci, to m.in. obs³uga folderów, przegl±dania i wysy³ania
za³±czników, preferencji, wyszukiwania, quoty i inne. UebiMiau nie
wymaga bazy danych ani IMAP.

%define         _appdir     %{_datadir}/%{name}

%prep
%setup -q -n %{name}-%{version}-%{sub_ver}-any
%patch0 -p1

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{_sysconfdir}/{%{name},httpd},%{_sharedstatedir}/%{name}}
install -d $RPM_BUILD_ROOT%{_appdir}/{database,extra,images,inc,langs,smarty,smarty/plugins,smarty/templates,themes/default}

%{__sed} -i "s|\$temporary_directory = \"./database/\";|\$temporary_directory = \"%{_sharedstatedir}/%{name}/\";|" inc/config.php
mv -f inc/config.{php,languages.php,security.php}	$RPM_BUILD_ROOT%{_sysconfdir}/%{name}
ln -sf %{_sysconfdir}/%{name}/config.php		$RPM_BUILD_ROOT%{_appdir}/inc/config.php
ln -sf %{_sysconfdir}/%{name}/config.languages.php	$RPM_BUILD_ROOT%{_appdir}/inc/config.languages.php
ln -sf %{_sysconfdir}/%{name}/config.security.php	$RPM_BUILD_ROOT%{_appdir}/inc/config.security.php

install *.php			$RPM_BUILD_ROOT%{_appdir}
install database/index.php	$RPM_BUILD_ROOT%{_appdir}/database
install extra/*			$RPM_BUILD_ROOT%{_appdir}/extra
install images/*		$RPM_BUILD_ROOT%{_appdir}/images
install inc/*			$RPM_BUILD_ROOT%{_appdir}/inc
install langs/*			$RPM_BUILD_ROOT%{_appdir}/langs
install smarty/*.php		$RPM_BUILD_ROOT%{_appdir}/smarty
install smarty/*.tpl		$RPM_BUILD_ROOT%{_appdir}/smarty
install smarty/plugins/*	$RPM_BUILD_ROOT%{_appdir}/smarty/plugins
install smarty/templates/*	$RPM_BUILD_ROOT%{_appdir}/smarty/templates
install themes/debug.tpl	$RPM_BUILD_ROOT%{_appdir}/themes
install themes/default/*	$RPM_BUILD_ROOT%{_appdir}/themes/default
echo "Alias /%{name} %{_appdir}" >	$RPM_BUILD_ROOT%{_sysconfdir}/httpd/%{name}.conf

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
		echo 	"Now you *must* move by hand %{name} data (see \$temprorary_directory"
		echo	"in ${CDIR}/config.php.rpmsave where they are)\nto /var/lib/%{name}/ . "
		echo -e	"\n###############################################################################\n"
	fi
fi

%files
%defattr(644,root,root,755)
%doc CHANGELOG.txt INSTALL.txt README.txt
%dir %{_sysconfdir}/%{name}
%attr(644,root,root) %config(noreplace) %verify(not size md5 mtime) %{_sysconfdir}/%{name}/*
%attr(644,root,root) %config(noreplace) %verify(not size md5 mtime) %{_sysconfdir}/httpd/%{name}.conf
%dir %{_appdir}
%{_appdir}/*.php
%{_appdir}/database
%{_appdir}/extra
%{_appdir}/images
%{_appdir}/inc
%{_appdir}/langs
%{_appdir}/smarty
%dir %{_appdir}/themes
%{_appdir}/themes/debug.tpl
%{_appdir}/themes/default
%defattr(640,http,http,750)
%dir %{_sharedstatedir}/%{name}
