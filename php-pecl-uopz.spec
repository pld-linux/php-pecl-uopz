#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	uopz
Summary:	User Operations for Zend
Name:		%{php_name}-pecl-%{modname}
Version:	2.0.7
Release:	1
License:	PHP 3.01
Group:		Development/Languages/PHP
Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	da0c3def649eec77191d005c53ee0a91
URL:		http://pecl.php.net/package/uopz
%{?with_tests:BuildRequires:    %{php_name}-cli}
BuildRequires:	%{php_name}-devel >= 4:5.4.0
BuildRequires:	rpmbuild(macros) >= 1.666
%if %{with tests}
BuildRequires:	%{php_name}-cli
BuildRequires:	%{php_name}-spl
BuildRequires:	%{php_name}-session
%endif
%{?requires_php_extension}
Provides:	php(uopz) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The uopz extension exposes Zend engine functionality normally used at
compilation and execution time in order to allow modification of the
internal structures that represent PHP code.

It supports the following activities:
- Overloading some Zend opcodes including exit/new and composure
  opcodes
- Renaming functions and methods
- Deletion of functions and methods
- Copying of functions and methods
- Redefinition of constants
- Deletion of constants
- Runtime composition and modification of classes

Note: All of the above activities are compatible with opcache,
including overloading ZEND_EXIT

%prep
%setup -qc
mv %{modname}-%{version}/* .

%build
phpize
%configure
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

cat <<'EOF' > run-tests.sh
#!/bin/sh
export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
%{__make} test \
	PHP_EXECUTABLE=%{__php} \
	PHP_TEST_SHARED_SYSTEM_EXTENSIONS="spl session" \
	RUN_TESTS_SETTINGS="-q $*"
EOF

chmod +x run-tests.sh
./run-tests.sh -w failed.log
test -f failed.log -a ! -s failed.log
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc README.md LICENSE
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
