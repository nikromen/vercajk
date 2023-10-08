Name:           vercajk
Version:        1.0.0
Release:        %autorelease
Summary:        My personal tools

License:        MIT
URL:            https://github.com/nikromen/%{name}
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-click

# also requires pip install --user konsave
Requires:       make
Requires:       conky
Requires:       git
Requires:       fish
Requires:       vim-enhanced
# requires rust but Fedora doesn't have rustup packaged


%description
%{summary}


%prep
%autosetup


%generate_buildrequires
%pyproject_buildrequires -r


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files %{name}
make update


%files -n %{name} -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/%{name}


%changelog
%autochangelog
