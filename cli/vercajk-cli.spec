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
BuildRequires:  python3-pytest
BuildRequires:  python3-pytest-click
BuildRequires:  python3-libvirt

Requires:  python3-click
Requires:  python3-jinja2
Requires:  python3-pyyaml
Requires:  python3-pydantic
Requires:  python3-requests
Requires:  ansible-core
Requires:  stow
Requires:  git
Requires:  python3-libvirt
Requires:  lorax
Requires:  virt-install


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


%check
%pytest


%files -n %{name} -f %{pyproject_files}
%{_bindir}/%{srcname}


%changelog
%autochangelog
