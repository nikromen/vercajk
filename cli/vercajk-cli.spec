%global srcname vercajk

Name:           %{srcname}-cli
Version:        1.0.0
Release:        %autorelease
Summary:        CLI tool for personal system provisioning and dotfiles management

License:        MIT
URL:            https://github.com/nikromen/%{srcname}
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

Requires:  python3-click
Requires:  python3-jinja2
Requires:  python3-pyyaml
Requires:  python3-pydantic
Requires:  python3-requests
Requires:  ansible-core
Requires:  stow
Requires:  git

Recommends:  python3-libvirt
Recommends:  lorax
Recommends:  virt-install


%description
%{summary}


%prep
%autosetup -n %{srcname}-%{version}


%generate_buildrequires
%pyproject_buildrequires -r


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files %{srcname}


%files -n %{name} -f %{pyproject_files}
%{_bindir}/%{srcname}


%changelog
%autochangelog
