#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	smp		# don't build SMP module
%bcond_with	verbose		# verbose build (V=1)
#
%ifarch sparc
%undefine	with_smp
%endif
#
%define		modname	ieee80211
%define		_rel	1
Summary:	Linux kernel module for the ieee80211 networking stack
Summary(de):	Linux Kernel Treiber für den ieee80211 Netz Stapel
Summary(pl):	Modu³ j±dra Linuksa do stosu sieciowego ieee80211
Name:		kernel%{_alt_kernel}-net-%{modname}
Version:	1.2.15
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://dl.sourceforge.net/ieee80211/%{modname}-%{version}.tgz
# Source0-md5:	499d5272fd1326ae65ebef80d9726e4d
URL:		http://ieee80211.sourceforge.net/
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.14}
BuildRequires:	rpmbuild(macros) >= 1.326
BuildRequires:	sed >= 4.0
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Requires:	module-init-tools >= 3.2.2-2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Linux kernel module for the ieee80211 networking stack.

%description -l de
Linux Kernel Modul für den ieee80211 Netz Stapel.

%description -l pl
Modu³ j±dra Linuksa do stosu sieciowego ieee80211.

%package -n kernel%{_alt_kernel}-smp-net-%{modname}
Summary:	Linux SMP kernel module for the ieee80211 networking stack
Summary(de):	Linux SMP Kernel Modul für den ieee80211 Netz Stapel
Summary(pl):	Modu³ j±dra Linuksa SMP do stosu sieciowego ieee80211
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
Requires:	module-init-tools >= 3.2.2-2

%description -n kernel%{_alt_kernel}-smp-net-%{modname}
Linux SMP kernel module for the ieee80211 networking stack.

%description -n kernel%{_alt_kernel}-smp-net-%{modname} -l de
Linux SMP Kernel Modul für den ieee80211 Netz Stapel.

%description -n kernel%{_alt_kernel}-smp-net-%{modname} -l pl
Modu³ j±dra Linuksa SMP do stosu sieciowego ieee80211.

%package -n %{modname}-devel
Summary:	Development header files for the ieee80211 networking stack
Summary(de):	Development Header Dateien für den ieee80211 Netz Stapel
Summary(pl):	Pliki nag³ówkowe do stosu sieciowego ieee80211
Release:	%{_rel}@%{_kernel_ver_str}
%{?with_dist_kernel:%requires_releq kernel-module-build}
Group:		Development/Libraries

%description -n %{modname}-devel
Development header files for the ieee80211 networking stack.

%description -n %{modname}-devel -l de
Development Header Dateien für den ieee80211 Netz Stapel.

%description -n %{modname}-devel -l pl
Pliki nag³ówkowe do stosu sieciowego ieee80211.

%prep
%setup -q -n %{modname}-%{version}
%{__sed} -i 's:<net/ieee80211.h>:"net/ieee80211.h":g' *.c

%build
%build_kernel_modules -m ieee80211,ieee80211_crypt{,_wep,_ccmp,_tkip}

%install
rm -rf $RPM_BUILD_ROOT

%install_kernel_modules -m ieee80211,ieee80211_crypt{,_wep,_ccmp,_tkip} -d misc -s current -n ieee80211

install -d $RPM_BUILD_ROOT%{_kernelsrcdir}/include/net
install net/* \
	$RPM_BUILD_ROOT%{_kernelsrcdir}/include/net

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-net-%{modname}
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-net-%{modname}
%depmod %{_kernel_ver}

%post	-n kernel%{_alt_kernel}-smp-net-%{modname}
%depmod %{_kernel_ver}smp

%postun	-n kernel%{_alt_kernel}-smp-net-%{modname}
%depmod %{_kernel_ver}smp

%files -n kernel%{_alt_kernel}-net-%{modname}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/ieee80211*-current.ko*
%{_sysconfdir}/modprobe.d/%{_kernel_ver}/ieee80211.conf

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-net-%{modname}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/ieee80211*-current.ko*
%{_sysconfdir}/modprobe.d/%{_kernel_ver}smp/ieee80211.conf
%endif

%files -n %{modname}-devel
%defattr(644,root,root,755)
# should go to a versioned directory
%{_kernelsrcdir}/include/net/*
