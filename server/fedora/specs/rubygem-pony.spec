# Generated from pony-1.8.gem by gem2rpm -*- rpm-spec -*-
%global gem_name pony
%global rubyabi 1.9.1

Name: rubygem-%{gem_name}
Version: 1.8
Release: 1%{?dist}.scripts.%{scriptsversion}
Summary: Send email in one command: Pony.mail(:to => 'someone@example.com', :body => 'hello')
Group: Development/Languages
License: MIT
URL: http://github.com/benprew/pony
Source0: http://rubygems.org/gems/%{gem_name}-%{version}.gem
Requires: ruby(abi) = %{rubyabi}
Requires: ruby(rubygems) 
Requires: rubygem(mail) >= 2.0
BuildRequires: ruby(abi) = %{rubyabi}
BuildRequires: rubygems-devel 
BuildRequires: ruby 
BuildArch: noarch
Provides: rubygem(%{gem_name}) = %{version}

%description
Send email in one command: Pony.mail(:to => 'someone@example.com', :body =>
'hello')


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
mkdir -p .%{gem_dir}

# Create the gem as gem install only works on a gem file
gem build %{gem_name}.gemspec


# gem install installs into a directory.  We set that to be a local
# directory so that we can move it into the buildroot in %%install
gem install --local --install-dir ./%{gem_dir} \
            --force --rdoc %{gem_name}-%{version}.gem

%install
mkdir -p %{buildroot}%{gem_dir}
cp -pa .%{gem_dir}/* \
        %{buildroot}%{gem_dir}/
rm -f %{buildroot}%{gem_instdir}/{Rakefile,pony.gemspec}
rm -rf %{buildroot}%{gem_instdir}/spec


%files
%dir %{gem_instdir}
%{gem_libdir}
%exclude %{gem_cache}
%{gem_spec}

%files doc
%doc %{gem_docdir}
%doc %{gem_instdir}/README.rdoc

%changelog
* Sun Mar 09 2014 Benjamin Tidor <btidor@mit.edu> - 1.8-1
- Initial package
