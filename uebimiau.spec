Summary:	UebiMiau - Simple POP3 Mail Reader
Summary(pl):	UebiMiau - Prosty czytnik poczty POP3
Name:		uebimiau
Version:	2.7
Release:	1
License:	GPL
Group:		Applications/Mail
Vendor:		Aldoir Ventura <aldoir@users.sourceforge.net>
Source0:	http://www.uebimiau.sili.com.br/downloads/%{name}-%{version}-latest.zip
URL:		http://www.uebimiau.sili.com.br
Requires:	webserver
Requires:	php
Provides:	webmail
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define         _uebimiaudir     /home/httpd/html/uebimiau

%description
UebiMiau is a web-based e-mail client written in PHP. It's have some
features, such as: Folders, View and Send Attachments, Preferences,
Search, Quota Limit, etc. UebiMiau does not require database or IMAP.

%description -l pl
UebiMaiu jest napisanym w PHP klientem poczty elektornicznej. Jego
mo¿liwo¶ci, to m.in obs³uga folderów, przegl±dania i wysy³ania
za³±czników, preferencji, wyszkiwania, quoty i inne. UebiMiau nie
wymaga bazy danych lub IMAP.

%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_uebimiaudir}/{database,extra,images,inc,langs,smarty,themes,themes/default,themes/neotech.net}

install *.php $RPM_BUILD_ROOT%{_uebimiaudir}
install database/index.php $RPM_BUILD_ROOT%{_uebimiaudir}/database
install extra/* $RPM_BUILD_ROOT%{_uebimiaudir}/extra
install images/* $RPM_BUILD_ROOT%{_uebimiaudir}/images
install inc/* $RPM_BUILD_ROOT%{_uebimiaudir}/inc
install langs/* $RPM_BUILD_ROOT%{_uebimiaudir}/langs
install smarty/* $RPM_BUILD_ROOT%{_uebimiaudir}/smarty
install themes/debug.tpl $RPM_BUILD_ROOT%{_uebimiaudir}/themes
install themes/default/* $RPM_BUILD_ROOT%{_uebimiaudir}/themes/default
install themes/neotech.net/* $RPM_BUILD_ROOT%{_uebimiaudir}/themes/neotech.net

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc CHANGELOG.txt INSTALL.txt README.txt
%attr(775,root,http) %{_uebimiaudir}/database
%attr(755,root,root) %config(noreplace) %verify(not size md5 mtime) %{_uebimiaudir}/inc/config.php
%dir %{_uebimiaudir}
%{_uebimiaudir}/*.php
%{_uebimiaudir}/extra
%{_uebimiaudir}/images
%{_uebimiaudir}/inc/lib.*
%{_uebimiaudir}/inc/class.*
%{_uebimiaudir}/inc/inc.*
%{_uebimiaudir}/langs
%{_uebimiaudir}/smarty
%{_uebimiaudir}/themes
