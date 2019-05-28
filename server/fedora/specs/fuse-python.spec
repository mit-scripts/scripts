Name:           fuse-python
Version:        0.3.1
Release:        1.%{scriptsversion}%{?dist}
Summary:        Python bindings for FUSE - filesystem in userspace

License:        LGPLv2
URL:            https://github.com/libfuse/python-fuse
Source0:        https://github.com/libfuse/python-fuse/archive/v%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  pkgconfig
BuildRequires:  fuse-devel
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

%global _description\
This package provides python bindings for FUSE. FUSE makes it possible\
to implement a filesystem in a userspace program.

%description %_description

%package -n python3-fuse
Summary: %summary
Provides:       python-fuse%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python3-fuse}
# Remove before F30
Provides: fuse-python%{?_isa} = %{version}-%{release}
Obsoletes: fuse-python < %{version}-%{release}

%description -n python3-fuse %_description

%prep
%setup -q

%build
%py3_build
mv -f Changelog Changelog.old
iconv -f iso8859-1 -t utf-8 < Changelog.old > Changelog

%install
%py3_install

%files -n python3-fuse
%license COPYING
%doc AUTHORS Changelog FAQ example README.1st
%doc README.new_fusepy_api README.new_fusepy_api.html README.package_maintainers
%{python2_sitearch}/*

%changelog
* Mon May 27 2019 Quentin Smith <quentin@mit.edu> - 0.3.1-1
- Updated for Python 3

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.1-24
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.1-23
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Apr 30 2018 Miro Hrončok <mhroncok@redhat.com> - 0.2.1-22
- Update Python macros to new packaging standards
  (See https://fedoraproject.org/wiki/Changes/Avoid_usr_bin_python_in_RPM_Build)

* Wed Feb 07 2018 Iryna Shcherbina <ishcherb@redhat.com> - 0.2.1-21
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.1-20
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Aug 19 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 0.2.1-19
- Python 2 binary package renamed to python2-fuse
  See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.1-18
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.1-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.1-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.1-15
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Wed May 11 2016 Kalev Lember <klember@redhat.com> - 0.2.1-14
- Fix python-fuse compatibility provides

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.1-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Jan 26 2016 Peter Lemenkov <lemenkov@gmail.com> 0.2.1-12
- Spec-file cleanups

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.1-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.1-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Jun 30 2014 Toshio Kuratomi <toshio@fedoraproject.org> - 0.2.1-9
- Replace python-setuptools-devel BR with python-setuptools

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 0.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Fri Apr 16 2010 Peter Lemenkov <lemenkov@gmail.com> 0.2.1-1
- Ver. 0.2.1 (bugfix release)
- Patch dropped (upstreamed)

* Wed Mar 10 2010 Peter Lemenkov <lemenkov@gmail.com> 0.2-13
- Fixed URL
- Added missing BR python-devel (this fixes rhbz #539185)

* Thu Sep 17 2009 Peter Lemenkov <lemenkov@gmail.com> 0.2-12
- rebuilt with new fuse

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.2-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.2-9
- Rebuild for Python 2.6

* Sun Apr 27 2008 Peter Lemenkov <lemenkov@gmail.com> 0.2-8
- Fix issue with libewf

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.2-7
- Autorebuild for GCC 4.3

* Thu Oct 18 2007 Michel Salim <michel.sylvan@gmail.com> 0.2-6
- Fix source URL
- Include examples

* Fri Oct  5 2007 Peter Lemenkov <lemenkov@gmail.com> 0.2-5
- Removed BR: python-devel (excessive since we BR: python-setuptool)
- Cleaned up mixed usage of macros and explicit commands ( __python and python)

* Fri Oct  5 2007 Peter Lemenkov <lemenkov@gmail.com> 0.2-4
- Changes according to http://fedoraproject.org/wiki/Packaging/Python/Eggs

* Sun Sep  9 2007 Jan ONDREJ (SAL) <ondrejj@salstar.sk> 0.2-3
- removed non used macros
- Changelog file converted to UTF-8

* Thu Sep  6 2007 Jan ONDREJ (SAL) <ondrejj@salstar.sk> 0.2-2
- changed permissions for sitearch files to 644
- added fuseparts dir to package
- added egg-info directory with it's content
- license changed to LGPLv2, according to documentation and sources
- added provides for python-fuse (remove it on rename)

* Sun Aug  5 2007 Peter Lemenkov <lemenkov@gmail.com> 0.2-1
- Ver. 0.2
- Cleanups

* Tue Jun 26 2007 Robin Norwood <rnorwood@redhat.com> - 0.2-pre3-2
- Put everything in python_sitearch, which should allow x86_64 builds

* Fri Jun 22 2007 Robin Norwood <rnorwood@redhat.com> - 0.2-pre3-1
- Initial build
