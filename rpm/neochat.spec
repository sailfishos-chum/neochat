%global  kde_version 25.08.2
%global  kf6_version 6.18.0

%bcond_with upush

Name:       neochat
Version:    25.08.3
Release:    1%{?dist}
License:    Apache-2.0 and BSD-3-Clause and CC0-1.0 and LGPL-2.0-or-later and CC-BY-SA-4.0
Summary:    A client for matrix, the decentralized communication protocol
Url:        https://invent.kde.org/network/neochat
#Source0:    https://invent.kde.org/pim/%%{name}/-/archive/v%%{version}/%%{name}-v%%{version}.tar.bz2
Source0:    %{name}-%{version}.tar.bz2

Patch0:  0000-add-Sailfish-OS-Option-and-define.patch
Patch1:  0001-no-tts.patch
Patch2:  0002-no-x11.patch
Patch3:  0003-no-ksyntaxhighlight.patch
Patch4:  0004-no-kimageeditor.patch
Patch5:  0005-no-systemtray.patch
Patch6:  0006-have-dbus.patch

Patch10: 0000-conserve-memory.patch

Requires:      qt6-qtlocation
Requires:      kf6-kquickcharts
Requires:      kf6-kitemmodels
Requires:      kf6-prison
#Requires:      kf6-kio-widgets
#Requires:      qml(org.kde.prison)
#Requires:      qml(QtLocation)
#Requires:      qml(org.kde.quickcharts)
#Requires:      qml(org.kde.kquickimageeditor)

BuildRequires: desktop-file-utils
BuildRequires: sailfish-svg2png
BuildRequires: kf6-extra-cmake-modules >= %kf6_version
BuildRequires: gcc-c++
BuildRequires: kf6-rpm-macros
#BuildRequires: kf6-qqc2-desktop-style
#BuildRequires: kf6-qqc2-breeze-style

BuildRequires: pkgconfig(openssl)

BuildRequires: pkgconfig(Qt6Core)

#Core Quick Gui QuickControls2 Multimedia Svg TextToSpeech WebView
BuildRequires: cmake(Qt6Quick)
BuildRequires: cmake(Qt6QuickControls2)
BuildRequires: cmake(Qt6Multimedia)
BuildRequires: cmake(Qt6Svg)
#BuildRequires: cmake(Qt6TextToSpeech)
#BuildRequires: cmake(Qt6WebView)

BuildRequires: cmake(QCoro6)
BuildRequires: cmake(QuotientQt6)
BuildRequires: cmake(cmark)

# Kirigami I18n Notifications Config CoreAddons Sonnet ItemModels IconThemes ColorScheme
BuildRequires: kf6-kirigami-devel
BuildRequires: kf6-kirigami-addons-devel
BuildRequires: kf6-ki18n-devel
BuildRequires: kf6-knotifications-devel
BuildRequires: kf6-kconfig-devel
BuildRequires: kf6-kcoreaddons-devel
BuildRequires: kf6-sonnet-devel
BuildRequires: kf6-kitemmodels-devel
BuildRequires: kf6-kiconthemes-devel
BuildRequires: kf6-kcolorscheme-devel

BuildRequires: kf6-kdbusaddons-devel

#BuildRequires: cmake(KQuickImageEditor)
BuildRequires:  cmake(qt6declarative_location)
#BuildRequires:  cmake(kf6kio) kf6-kio-widgets-libs
BuildRequires:  cmake(kf6purpose)
BuildRequires:  pkgconfig(icu-uc)

%if %{with upush}
BuildRequires: cmake(KUnifiedPush)
Requires:      kde-kunifiedpush
%endif

%description
%{summary}.

NeoChat aims to be a fully featured application for the Matrix specification.
As such most parts of the current specification are supported, with the notable
exceptions of VoIP, threads, and some aspects of End-to-End Encryption. There
are a few other smaller omissions due to the fact that the Matrix spec is
constantly evolving, but the aim remains to provide eventual support for the
entire spec.

%if 0%{?_chum}
Title: Neochat
Type: desktop-application
DeveloperName: The KDE Community
PackagedBy: nephros
Categories:
  - Network
  - InstantMessaging
Custom:
  Repo: https://invent.kde.org/network/neochat
PackageIcon: https://invent.kde.org/network/neochat/-/raw/master/128-logo.png
Screenshots:
  - https://cdn.kde.org/screenshots/neochat/application.png
Links:
  Homepage: https://apps.kde.org/neochat/
  Help: https://discuss.kde.org/c/help/6
  Bugtracker: https://bugs.kde.org/enter_bug.cgi?product=NeoChat
%endif


%prep
%autosetup -p1 -n %{name}-%{version}/upstream

%build
export SBOX_MAPPING_LOGLEVEL=error
export SBOX_QUIET=1

# Disable LTO
%global _lto_cflags %{nil}
# prevent virtual memory exhaustion
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /' )
export CXXFLAGS="%{build_cxxflags} -Wl,--no-keep-memory -Wl,--reduce-memory-overheads" # --param ggc-min-expand=10"
 #FIXME: this is what causes memory exhaustion, null it for now
echo '{}' > src/libneochat/emojitones_data.h

%cmake_kf6 \
  -Wno-dev \
  -DCMAKE_BUILD_TYPE=Release \
  -DSAILFISHOS=ON \
%if %{with upush}
  -DWITH_UNIFIEDPUSH=ON \
%else
  -DWITH_UNIFIEDPUSH=OFF \
%endif
  %{nil}

#%%cmake_build -j1 --target LibNeoChat ||:
%cmake_build

%install
%cmake_install

%find_lang %{name}

desktop-file-edit \
  --remove-key=Version \
  --remove-key=SingleMainWindow \
   %{buildroot}%{_datadir}/applications/org.kde.neochat.desktop
sed -i -e 's@^Exec=neochat@Exec=qt-runner /usr/bin/neochat@g' \
   %{buildroot}%{_datadir}/applications/org.kde.neochat.desktop
printf 'X-Nemo-Single-Instance=no\nX-Nemo-Application-Type=no-invoker\n'
   >> %{buildroot}%{_datadir}/applications/org.kde.neochat.desktop
printf '\n[X-Sailjail]\nSandboxing=Disabled\n' \
   >> %{buildroot}%{_datadir}/applications/org.kde.neochat.desktop

desktop-file-install --delete-original       \
  --dir %{buildroot}%{_datadir}/applications             \
   %{buildroot}%{_datadir}/applications/*.desktop

## generate some icons
for size in 86 108 128 172 256 512; do
install -d %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/
sailfish_svg2png -z 1.0 -s 1 1 1 1 1 1 ${size} %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/ %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/
done

#%%post -p /sbin/ldconfig
#%%postun -p /sbin/ldconfig

%files -f %{name}.lang
%{_kf6_bindir}/neochat
%{_kf6_plugindir}/purpose/neochatshareplugin.so
%{_kf6_datadir}/applications/*.desktop
#%%{_kf6_datadir}/dbus-1/services/org.kde.neochat.service
%{_kf6_datadir}/icons/hicolor/scalable/apps/*.svg
%{_kf6_datadir}/icons/hicolor/*/apps/*.png
%{_kf6_datadir}/knotifications6/neochat.notifyrc
%{_kf6_datadir}/krunner/dbusplugins/plasma-runner-neochat.desktop
%{_kf6_datadir}/qlogging-categories6/neochat.categories
%exclude %{_kf6_datadir}/metainfo/org.kde.neochat.appdata.xml

