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
Summary:	Linux kernel module for the ieee80211 networking stack
Summary(pl):	Modu� j�dra Linuksa do stosu sieciowego ieee80211
Name:		kernel-net-%{modname}
Version:	1.1.12
%define		_rel	2
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://dl.sourceforge.net/ieee80211/%{modname}-%{version}.tgz
# Source0-md5:	20da3f23dad2356da8f14d8b3d88d58e
URL:		http://ieee80211.sourceforge.net/
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.14}
BuildRequires:	rpmbuild(macros) >= 1.153
BuildRequires:	sed >= 4.0
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Linux kernel module for the ieee80211 networking stack.

%description -l pl
Modu� j�dra Linuksa do stosu sieciowego ieee80211.

%package -n kernel-smp-net-%{modname}
Summary:	Linux SMP kernel module for the ieee80211 networking stack
Summary(pl):	Modu� j�dra Linuksa SMP do stosu sieciowego ieee80211
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod

%description -n kernel-smp-net-%{modname}
Linux SMP kernel module for the ieee80211 networking stack.

%description -n kernel-smp-net-ieee80211 -l pl
Modu� j�dra Linuksa SMP do stosu sieciowego ieee80211.

%package -n %{modname}-devel
Summary:	Development header files for the ieee80211 networking stack
Summary(pl):	Pliki nag��wkowe do stosu sieciowego ieee80211
Release:	%{_rel}@%{_kernel_ver_str}
%{?with_dist_kernel:%requires_releq kernel-module-build}
Group:		Development/Libraries

%description -n %{modname}-devel
Development header files for the ieee80211 networking stack.

%description -n %{modname}-devel -l pl
Pliki nag��wkowe do stosu sieciowego ieee80211.

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
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
%ifarch ppc ppc64
        install -d include/asm
        [ ! -d %{_kernelsrcdir}/include/asm-powerpc ] || ln -sf %{_kernelsrcdir}/include/asm-powerpc/* include/asm
        [ ! -d %{_kernelsrcdir}/include/asm-%{_target_base_arch} ] || ln -snf %{_kernelsrcdir}/include/asm-%{_target_base_arch}/* include/asm
%else
        ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
%endif
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
#	%if %{without dist_kernel}
                ln -sf %{_kernelsrcdir}/scripts
 #       %endif
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
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc
install %{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}/*.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc
%if %{with smp} && %{with dist_kernel}
install smp/*.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc
%endif

cd ..
install -d $RPM_BUILD_ROOT%{_kernelsrcdir}/include/net
install net/* \
	$RPM_BUILD_ROOT%{_kernelsrcdir}/include/net

# avoid conflicts with kernel modules:
cd $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc
for module in *.ko; do
	mv $module `basename $module | sed -e "s/\.ko//"`_current.ko
done
%if %{with smp} && %{with dist_kernel}
cd $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc
for module in *.ko; do
	mv $module `basename $module | sed -e "s/\.ko//"`_current.ko
done
%endif

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

%triggerpostun -n kernel-net-ieee80211 -- kernel-net-ieee80211 < 1.1.12-2
%banner kernel-net-ieee80211-1.1.12-1 <<'EOF'
Current kernel provides ieee80211* modules.
This package contains currently module named ieee80211*_current.

If you want to use this module do:
echo "alias ieee80211 ieee80211_current" >> /etc/modprobe.conf
echo "alias ieee80211_crypt ieee80211_crypt_current" >> /etc/modprobe.conf
echo "alias ieee80211_crypt_ccmp ieee80211_crypt_ccmp_current" >> /etc/modprobe.conf
echo "alias ieee80211_crypt_tkip ieee80211_crypt_tkip_current" >> /etc/modprobe.conf
echo "alias ieee80211_crypt_wep ieee80211_crypt_wep_current" >> /etc/modprobe.conf
EOF

%triggerpostun -n kernel-smp-net-ieee80211 -- kernel-smp-net-ieee80211 < 1.1.12-2
%banner kernel-smp-net-ieee80211-1.1.12-1 <<'EOF'
Current kernel provides ieee80211* modules.
This package contains currently module named ieee80211*_current.

If you want to use this module do:
echo "alias ieee80211 ieee80211_current" >> /etc/modprobe.conf
echo "alias ieee80211_crypt ieee80211_crypt_current" >> /etc/modprobe.conf
echo "alias ieee80211_crypt_ccmp ieee80211_crypt_ccmp_current" >> /etc/modprobe.conf
echo "alias ieee80211_crypt_tkip ieee80211_crypt_tkip_current" >> /etc/modprobe.conf
echo "alias ieee80211_crypt_wep ieee80211_crypt_wep_current" >> /etc/modprobe.conf
EOF

%files -n kernel-net-%{modname}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/ieee80211*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-net-%{modname}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/ieee80211*.ko*
%endif

%files -n %{modname}-devel
%defattr(644,root,root,755)
# should go to a versioned directory
%{_kernelsrcdir}/include/net/*
