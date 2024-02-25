%global srcname vercajk

Name:           %{srcname}-cli
Version:        1.0.0
Release:        1%{?dist}
Summary:        Cli tool for my personal vercajk

License:        GPLv3
URL:            https://github.com/nikromen/%{srcname}
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-click


%description
%{summary}


%prep
%autosetup -n  %{srcname}-%{version}


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
