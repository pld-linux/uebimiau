Summary:	UebiMiau - Simple POP3 Mail Reader
Summary(pl):	UebiMiau - Prosty czytnik poczty POP3
Name:		uebimiau
Version:	2.7.8
%define		sub_ver	RC1
Release:	5.1.%{sub_ver}
License:	GPL
Group:		Applications/Mail
Vendor:		Aldoir Ventura <aldoir@users.sourceforge.net>
Source0:	http://www.uebimiau.org/downloads/%{name}-%{version}-%{sub_ver}-any.tar.gz
# Source0-md5:	20e355ef9535deb49b8866cd93b661af
Patch0:		uebimiau-attachment,readmsg.patch 		
URL:		http://www.uebimiau.org/
Requires:	php
Requires:	php-pcre
Requires:	webserver	
Provides:	webmail
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define         _uebimiaudir     %{_datadir}/%{name}

%description
UebiMiau is a web-based e-mail client written in PHP. It's have some
features, such as: Folders, View and Send Attachments, Preferences,
Search, Quota Limit, etc. UebiMiau does not require database or IMAP.

%description -l pl
UebiMiau jest napisanym w PHP klientem poczty elektronicznej. Jego
mo¿liwo¶ci, to m.in. obs³uga folderów, przegl±dania i wysy³ania
za³±czników, preferencji, wyszukiwania, quoty i inne. UebiMiau nie
wymaga bazy danych ani IMAP.

%prep
%setup -q -n %{name}-%{version}-%{sub_ver}-any
%patch0 -p1

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_sysconfdir}/{%{name},httpd}
install -d $RPM_BUILD_ROOT%{_uebimiaudir}/{database,extra,images,inc,langs,smarty,smarty/plugins,smarty/templates,themes,themes/default}

mv -f inc/config.{php,languages.php,security.php}	$RPM_BUILD_ROOT%{_sysconfdir}/%{name}
ln -sf %{_sysconfdir}/%{name}/config.php		$RPM_BUILD_ROOT%{_uebimiaudir}/inc/config.php
ln -sf %{_sysconfdir}/%{name}/config.languages.php	$RPM_BUILD_ROOT%{_uebimiaudir}/inc/config.languages.php
ln -sf %{_sysconfdir}/%{name}/config.security.php	$RPM_BUILD_ROOT%{_uebimiaudir}/inc/config.security.php

install *.php			$RPM_BUILD_ROOT%{_uebimiaudir}
install database/index.php	$RPM_BUILD_ROOT%{_uebimiaudir}/database
install extra/*			$RPM_BUILD_ROOT%{_uebimiaudir}/extra
install images/*		$RPM_BUILD_ROOT%{_uebimiaudir}/images
install inc/*			$RPM_BUILD_ROOT%{_uebimiaudir}/inc
install langs/*			$RPM_BUILD_ROOT%{_uebimiaudir}/langs
install smarty/*.php		$RPM_BUILD_ROOT%{_uebimiaudir}/smarty
install smarty/*.tpl		$RPM_BUILD_ROOT%{_uebimiaudir}/smarty
install smarty/plugins/*	$RPM_BUILD_ROOT%{_uebimiaudir}/smarty/plugins
install smarty/templates/*	$RPM_BUILD_ROOT%{_uebimiaudir}/smarty/templates
install themes/debug.tpl	$RPM_BUILD_ROOT%{_uebimiaudir}/themes
install themes/default/*	$RPM_BUILD_ROOT%{_uebimiaudir}/themes/default
echo    Alias "/%{name}" "%{_uebimiaudir}" >	$RPM_BUILD_ROOT%{_sysconfdir}/httpd/%{name}.conf

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

%triggerin -- %{name} < 2.7.8-5.RC1
set -x
echo "Moving your precious uebimiau configs contents to new location (/etc/%{name}/)."
CONFFILES="/home/*/httpd/html/uebimiau/inc/config*.php*"
for CONFFILE in $CONFFILES ; do
	cat "$CONFFILE" > %{_sysconfdir}/%{name}/$(basename "$CONFFILE")
echo "Done."
done || :

%files
%defattr(644,root,root,755)
%doc CHANGELOG.txt INSTALL.txt README.txt
%dir %{_sysconfdir}/%{name}
%attr(644,root,root) %config(noreplace) %verify(not size md5 mtime) %{_sysconfdir}/%{name}/*
%attr(644,root,root) %config(noreplace) %verify(not size md5 mtime) %{_sysconfdir}/httpd/%{name}.conf
%dir %{_uebimiaudir}
%{_uebimiaudir}/*.php
%{_uebimiaudir}/extra
%{_uebimiaudir}/images
%{_uebimiaudir}/inc
%{_uebimiaudir}/langs
%{_uebimiaudir}/smarty
%{_uebimiaudir}/themes
# FIX IT
%attr(775,http,http) %{_uebimiaudir}/database
