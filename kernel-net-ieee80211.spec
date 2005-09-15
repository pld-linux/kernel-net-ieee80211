#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	smp		# don't build SMP module
%bcond_with	verbose		# verbose build (V=1)
#
%define		modname	ieee80211
Summary:	Linux kernel module for the ieee80211 networking stack
Summary(pl):	Modu³ j±dra Linuksa do stosu sieciowego ieee80211
Name:		kernel-net-%{modname}
Version:	1.0.3
%define		_rel	1
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://dl.sourceforge.net/ieee80211/%{modname}-%{version}.tgz
# Source0-md5:	49870c030278e3716194ff5b64f9cbaa
URL:		http://ieee80211.sourceforge.net/
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.8}
BuildRequires:	rpmbuild(macros) >= 1.153
BuildRequires:	sed >= 4.0
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
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

%description -n kernel-smp-net-%{modname}
Linux SMP kernel module for the ieee80211 networking stack.

%description -n kernel-smp-net-ieee80211 -l pl
Modu³ j±dra Linuksa SMP do stosu sieciowego ieee80211.

%package -n %{modname}-devel
Summary:	Development header files for the ieee80211 networking stack
Summary(pl):	Pliki nag³ówkowe do stosu sieciowego ieee80211
Release:	%{_rel}
Group:		Development/Libraries

%description -n %{modname}-devel
Development header files for the ieee80211 networking stack.

%description -n %{modname}-devel -l pl
Pliki nag³ówkowe do stosu sieciowego ieee80211.

%prep
%setup -q -n %{modname}-%{version}

%build
# kernel module(s)
rm -rf built
mkdir -p built/{nondist,smp,up}
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
	%if %{without dist_kernel}
                ln -sf %{_kernelsrcdir}/scripts
        %endif
	touch include/config/MARKER
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	mv *.ko built/$cfg
done

%install
rm -rf $RPM_BUILD_ROOT

cd built
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/drivers/net/wireless
install %{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}/*.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/net/wireless
%if %{with smp} && %{with dist_kernel}
install smp/*.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/net/wireless
%endif

cd ..
install -d $RPM_BUILD_ROOT%{_kernelsrcdir}/include/net
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
/lib/modules/%{_kernel_ver}/kernel/drivers/net/wireless/ieee80211*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-net-%{modname}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/drivers/net/wireless/ieee80211*.ko*
%endif

%files -n %{modname}-devel
%defattr(644,root,root,755)
%{_kernelsrcdir}/include/net/*
