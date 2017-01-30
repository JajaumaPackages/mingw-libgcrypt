%?mingw_package_header

%global run_tests 0

Name:           mingw-libgcrypt
Version:        1.6.3
Release:        4%{?dist}
Summary:        MinGW Windows gcrypt encryption library

License:        LGPLv2+ and GPLv2+
Group:          Development/Libraries

URL:            ftp://ftp.gnupg.org/gcrypt/libgcrypt/
Source0:        libgcrypt-%{version}-hobbled.tar.xz
# The original libgcrypt sources now contain potentially patented ECC
# cipher support. We have to remove it in the tarball we ship with
# the hobble-libgcrypt script.
# (We replace it with RH approved ECC in Source4-5)
#Source0:       ftp://ftp.gnupg.org/gcrypt/libgcrypt/libgcrypt-%{version}.tar.bz2
#Source1:       ftp://ftp.gnupg.org/gcrypt/libgcrypt/libgcrypt-%{version}.tar.bz2.sig
Source2:        wk@g10code.com
Source3:        hobble-libgcrypt
# Approved ECC support (from 1.6.1)
Source4:        ecc-curves.c
Source5:        curves.c
Source6:        t-mpi-point.c

# Upstream is unwilling to accept this patch...
# https://bugs.g10code.com/gnupg/issue1360
Patch0:         libgcrypt-mingw64-use-correct-datatype-for-GetProcessWorkingSet.patch

# Workaround a bug in libtool:
# libgcrypt-use-correct-def-file.patch
Patch2:         libgcrypt-use-correct-def-file.patch

# The ASM code is written for the generic x86_64 target.
# For Win64 some minor changes are needed
Patch3:         libgcrypt-use-correct-asm-code-for-win64.patch

BuildArch:      noarch

BuildRequires:  mingw32-filesystem >= 95
BuildRequires:  mingw32-gcc
BuildRequires:  mingw32-binutils
BuildRequires:  mingw32-libgpg-error

BuildRequires:  mingw64-filesystem >= 95
BuildRequires:  mingw64-gcc
BuildRequires:  mingw64-binutils
BuildRequires:  mingw64-libgpg-error

BuildRequires:  autoconf automake libtool

%if %run_tests
BuildRequires:  wine
%endif


%description
Libgcrypt is a general purpose crypto library based on the code used
in GNU Privacy Guard.

This is a Windows cross-compiled version of the library.


# Win32
%package -n mingw32-libgcrypt
Summary:        MinGW Windows gcrypt encryption library

%description -n mingw32-libgcrypt
Libgcrypt is a general purpose crypto library based on the code used
in GNU Privacy Guard.

This is a Windows cross-compiled version of the library.

%package -n mingw32-libgcrypt-static
Summary:        Static library for mingw32-libgcrypt development
Requires:       mingw32-libgcrypt = %{version}-%{release}
Requires:       mingw32-libgpg-error-static

%description -n mingw32-libgcrypt-static
Static library for mingw32-libgcrypt development.

# Win64
%package -n mingw64-libgcrypt
Summary:        MinGW Windows gcrypt encryption library

%description -n mingw64-libgcrypt
Libgcrypt is a general purpose crypto library based on the code used
in GNU Privacy Guard.

This is a Windows cross-compiled version of the library.

%package -n mingw64-libgcrypt-static
Summary:        Static library for mingw64-libgcrypt development
Requires:       mingw64-libgcrypt = %{version}-%{release}
Requires:       mingw64-libgpg-error-static

%description -n mingw64-libgcrypt-static
Static library for mingw64-libgcrypt development.


%?mingw_debug_package


%prep
%setup -q -n libgcrypt-%{version}
%{SOURCE3}
%patch0 -p0 -b .win64
%patch2 -p0 -b .def
%patch3 -p1 -b .asm64
cp %{SOURCE4} cipher/
cp %{SOURCE5} %{SOURCE6} tests/

# Needed for the asm64 patch
autoreconf -i --force


%build
MINGW64_CONFIGURE_ARGS="ac_cv_sys_symbol_underscore=no --disable-padlock-support"
%mingw_configure --enable-shared --enable-static --enable-pubkey-ciphers='dsa elgamal rsa ecc'
%mingw_make %{?_smp_mflags}


%check
%if %run_tests
# Stupid Wine doesn't load DLLs from the PATH any
# more, so libtool scripts don't work.  As a result
# we need to use the following Big Hack.
make -C build_win32/tests check ||:
pushd build_win32/src/.libs
for t in $(pwd)/../../tests/*.exe; do
  wine $t
done
popd
%endif


%install
%mingw_make install DESTDIR=$RPM_BUILD_ROOT

# Remove info pages which duplicate what is in Fedora natively.
rm -rf $RPM_BUILD_ROOT%{mingw32_infodir}
rm -rf $RPM_BUILD_ROOT%{mingw64_infodir}

rm -rf $RPM_BUILD_ROOT%{mingw32_mandir}
rm -rf $RPM_BUILD_ROOT%{mingw64_mandir}

rm $RPM_BUILD_ROOT%{mingw32_libdir}/libgcrypt.def
rm $RPM_BUILD_ROOT%{mingw64_libdir}/libgcrypt.def

rm $RPM_BUILD_ROOT%{mingw32_libdir}/libgcrypt.la
rm $RPM_BUILD_ROOT%{mingw64_libdir}/libgcrypt.la


%files -n mingw32-libgcrypt
%doc COPYING COPYING.LIB
%{mingw32_bindir}/dumpsexp.exe
%{mingw32_bindir}/hmac256.exe
%{mingw32_bindir}/mpicalc.exe
%{mingw32_bindir}/libgcrypt-20.dll
%{mingw32_bindir}/libgcrypt-config
%{mingw32_libdir}/libgcrypt.dll.a
%{mingw32_includedir}/gcrypt.h
%{mingw32_datadir}/aclocal/libgcrypt.m4

%files -n mingw32-libgcrypt-static
%{mingw32_libdir}/libgcrypt.a

%files -n mingw64-libgcrypt
%doc COPYING COPYING.LIB
%{mingw64_bindir}/dumpsexp.exe
%{mingw64_bindir}/hmac256.exe
%{mingw64_bindir}/mpicalc.exe
%{mingw64_bindir}/libgcrypt-20.dll
%{mingw64_bindir}/libgcrypt-config
%{mingw64_libdir}/libgcrypt.dll.a
%{mingw64_includedir}/gcrypt.h
%{mingw64_datadir}/aclocal/libgcrypt.m4

%files -n mingw64-libgcrypt-static
%{mingw64_libdir}/libgcrypt.a


%changelog
* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.6.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Jan 05 2016 Richard Jones <rjones@redhat.com> - 1.6.3-3
- Use global instead of define.

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Apr 24 2015 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.6.3-1
- Update to 1.6.3
- Fixes CVE-2014-3591 CVE-2015-0837 (RHBZ #1198153 #1198156)

* Tue Dec 23 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.6.2-1
- Update to 1.6.2

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu May 29 2014 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.6.1-1
- Update to 1.6.1
- Add cleared ECC support
- Disable padlock support in Win64 for now (breaks compilation)

* Wed Nov 20 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.5.3-1
- Update to 1.5.3

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sun May 5 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.5.2-1
- Update to 1.5.2

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jan  2 2013 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.5.0-6
- Made the win64 asm code work properly

* Sun Oct 21 2012 Yaakov Selkowitz <yselkowitz@users.sourceforge.net> - 1.5.0-5
- Add static libraries
- Fix compile of assembly code for mingw64

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Apr 19 2012 Kalev Lember <kalevlember@gmail.com> - 1.5.0-3
- Rebuilt for %%mingw_configure arg parsing issue

* Sat Mar 31 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.5.0-2
- Simplify the use of mingw macros
- Improved the win64 patch a bit (shouldn't have any visible effects)

* Sun Mar 11 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.5.0-1
- Update to 1.5.0
- Added win64 support

* Fri Mar 09 2012 Kalev Lember <kalevlember@gmail.com> - 1.4.4-9
- Remove .la files

* Tue Mar 06 2012 Kalev Lember <kalevlember@gmail.com> - 1.4.4-8
- Renamed the source package to mingw-libgcrypt (#800428)
- Spec clean up

* Mon Feb 27 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 1.4.4-7
- Rebuild against the mingw-w64 toolchain
- Use correct .def file

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.4-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Feb 20 2009 Richard W.M. Jones <rjones@redhat.com> - 1.4.4-2
- Rebuild for mingw32-gcc 4.4

* Fri Feb  6 2009 Richard W.M. Jones <rjones@redhat.com> - 1.4.4-1
- Update to Fedora native version 1.4.4:
  . Remove potentially patented ECC support.
  . Do not abort when the fips mode kernel flag is inaccessible
    due to permissions (#470219).
- For review (Michel Alexandre Salim):
  . Remove *.def file.
  . Make description clearer.
  . Distribute the license files.
- The license for binaries is GPLv2+, so update the license field.
- Add check section (disabled by default).
- Why did we set PATH before configure? Removed.
- Added BR mingw32-dlfcn suggested by auto-buildrequires.

* Fri Jan 23 2009 Richard W.M. Jones <rjones@redhat.com> - 1.4.3-3
- Use _smp_mflags.
- Disable static libraries.

* Wed Sep 24 2008 Richard W.M. Jones <rjones@redhat.com> - 1.4.3-2
- Rename mingw -> mingw32.

* Mon Sep 22 2008 Daniel P. Berrange <berrange@redhat.com> - 1.4.3-1
- Update to 1.4.3 release

* Sun Sep 21 2008 Richard W.M. Jones <rjones@redhat.com> - 1.4.1-6
- Remove info pages.

* Thu Sep 11 2008 Daniel P. Berrange <berrange@redhat.com> - 1.4.1-5
- Set PATH so it finds gpg-error-config

* Wed Sep 10 2008 Richard W.M. Jones <rjones@redhat.com> - 1.4.1-4
- Remove static library.

* Thu Sep  4 2008 Richard W.M. Jones <rjones@redhat.com> - 1.4.1-3
- Use RPM macros from mingw-filesystem.

* Tue Sep  2 2008 Daniel P. Berrange <berrange@redhat.com> - 1.4.1-2
- List files explicitly and use custom CFLAGS

* Mon Jul  7 2008 Richard W.M. Jones <rjones@redhat.com> - 1.4.1-1
- Initial RPM release, largely based on earlier work from several sources.
