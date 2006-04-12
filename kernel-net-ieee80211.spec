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
%define		_rel	2
Summary:	Linux kernel module for the ieee80211 networking stack
Summary(pl):	Modu³ j±dra Linuksa do stosu sieciowego ieee80211
Name:		kernel-net-%{modname}
Version:	1.1.12
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://dl.sourceforge.net/ieee80211/%{modname}-%{version}.tgz
# Source0-md5:	20da3f23dad2356da8f14d8b3d88d58e
URL:		http://ieee80211.sourceforge.net/
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 3:2.6.14}
BuildRequires:	rpmbuild(macros) >= 1.153
BuildRequires:	sed >= 4.0
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Requires:	module-init-tools >= 3.2.2-2
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Linux kernel module for the ieee80211 networking stack.

%description -l pl
Modu³ j±dra Linuksa do stosu sieciowego ieee80211.

%package -n kernel-smp-net-%{modname}
Summary:	Linux SMP kernel module for the ieee80211 networking stack
Summary(pl):	Modu³ j±dra Linuksa SMP do stosu sieciowego ieee80211
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
Requires:	module-init-tools >= 3.2.2-2

%description -n kernel-smp-net-%{modname}
Linux SMP kernel module for the ieee80211 networking stack.

%description -n kernel-smp-net-ieee80211 -l pl
Modu³ j±dra Linuksa SMP do stosu sieciowego ieee80211.

%package -n %{modname}-devel
Summary:	Development header files for the ieee80211 networking stack
Summary(pl):	Pliki nag³ówkowe do stosu sieciowego ieee80211
Release:	%{_rel}@%{_kernel_ver_str}
%{?with_dist_kernel:%requires_releq kernel-module-build}
Group:		Development/Libraries

%description -n %{modname}-devel
Development header files for the ieee80211 networking stack.

%description -n %{modname}-devel -l pl
Pliki nag³ówkowe do stosu sieciowego ieee80211.

%prep
%setup -q -n %{modname}-%{version}
%{__sed} -i 's:<net\/ieee80211.h>:\"net\/ieee80211.h\":g' *.c

%build
# kernel module(s)
rm -rf built
mkdir -p built/{nondist,smp,up}
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
%if %{with dist_kernel}
	%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	mv *.ko built/$cfg
done

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc \
	$RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/%{_kernel_ver}{,smp} \
	$RPM_BUILD_ROOT%{_kernelsrcdir}/include/net

cd built
for MOD in ieee80211 ieee80211_crypt ieee80211_crypt_wep \
		ieee80211_crypt_ccmp ieee80211_crypt_tkip; do
	install %{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}/$MOD.ko \
		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/${MOD}_current.ko
	echo "alias $MOD ${MOD}_current" \
		>> $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/%{_kernel_ver}/ieee80211.conf
done

%if %{with smp} && %{with dist_kernel}
for MOD in ieee80211 ieee80211_crypt ieee80211_crypt_wep \
		ieee80211_crypt_ccmp ieee80211_crypt_tkip; do
	install smp/$MOD.ko \
		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/${MOD}_current.ko
	echo "alias $MOD ${MOD}_current" \
		>> $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/%{_kernel_ver}smp/ieee80211.conf
done
%endif

cd ..
install net/* \
	$RPM_BUILD_ROOT%{_kernelsrcdir}/include/net

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel-net-%{modname}
%depmod %{_kernel_ver}

%postun	-n kernel-net-%{modname}
%depmod %{_kernel_ver}

%post	-n kernel-smp-net-%{modname}
%depmod %{_kernel_ver}smp

%postun	-n kernel-smp-net-%{modname}
%depmod %{_kernel_ver}smp

%files -n kernel-net-%{modname}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/ieee80211*.ko*
%{_sysconfdir}/modprobe.d/%{_kernel_ver}/ieee80211.conf

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-net-%{modname}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/ieee80211*.ko*
%{_sysconfdir}/modprobe.d/%{_kernel_ver}smp/ieee80211.conf
%endif

%files -n %{modname}-devel
%defattr(644,root,root,755)
# should go to a versioned directory
%{_kernelsrcdir}/include/net/*
