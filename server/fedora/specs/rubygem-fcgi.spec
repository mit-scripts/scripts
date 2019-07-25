# Generated from fcgi-0.9.1.gem by gem2rpm -*- rpm-spec -*-
%global gem_name fcgi

Name: rubygem-%{gem_name}
Version: 0.9.2.1
Release: 1.scripts.%{scriptsversion}%{?dist}
Summary: FastCGI library for Ruby
Group: Development/Languages
License: BSDL
URL: http://github.com/alphallc/ruby-fcgi-ng
Source0: https://rubygems.org/gems/%{gem_name}-%{version}.gem
Requires: ruby(release)
Requires: ruby(rubygems) 
Requires: fcgi-devel
BuildRequires: gcc
BuildRequires: ruby(release)
BuildRequires: rubygems-devel 
BuildRequires: ruby-devel 
BuildRequires: fcgi-devel
Provides: rubygem(%{gem_name}) = %{version}

%description
FastCGI is a language independent, scalable, open extension to CGI that
provides high performance without the limitations of server specific APIs.
This version aims to be compatible with both 1.8.x and 1.9.x versions of Ruby,
and also will be ported to 2.0.x.


%package doc
Summary: Documentation for %{name}
Group: Documentation
Requires: %{name} = %{version}-%{release}
BuildArch: noarch

%description doc
Documentation for %{name}

%prep
gem unpack %{SOURCE0}

%setup -q -D -T -n  %{gem_name}-%{version}

gem spec %{SOURCE0} -l --ruby > %{gem_name}.gemspec

%build
# Create the gem as gem install only works on a gem file
gem build %{gem_name}.gemspec

# %%gem_install compiles any C extensions and installs the gem into ./%gem_dir
# by default, so that we can move it into the buildroot in %%install
%gem_install

%install
mkdir -p %{buildroot}%{gem_dir}
cp -pa .%{gem_dir}/* \
        %{buildroot}%{gem_dir}/

mkdir -p %{buildroot}%{gem_extdir_mri}/lib
# TODO: move the extensions
# mv %{buildroot}%{gem_instdir}/lib/shared_object.so %{buildroot}%{gem_extdir_mri}/lib/



%files
%dir %{gem_instdir}
%{gem_libdir}
%exclude %{gem_instdir}/ext
%{gem_extdir_mri}
%exclude %{gem_cache}
%{gem_spec}

%files doc
%doc %{gem_docdir}
%doc %{gem_instdir}/VERSION
%doc %{gem_instdir}/LICENSE
%doc %{gem_instdir}/README.rdoc
%doc %{gem_instdir}/README.signals
%{gem_instdir}/fcgi.gemspec
%{gem_instdir}/test/helper.rb
%{gem_instdir}/test/test_fcgi.rb

%changelog
* Sat Jul 19 2014 Benjamin Tidor <btidor@mit.edu> - 0.9.2.1-1
- Updated to 0.9.2.1, reconfigured for Sscripts

* Mon Aug 12 2013 Steven Valdez <dvorak42@XVM-THREE-199.MIT.EDU> - 0.9.1-1
- Initial package
