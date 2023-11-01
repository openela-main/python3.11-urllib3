%global __python3 /usr/bin/python3.11
%global python3_pkgversion 3.11

%global srcname urllib3

# RHEL: Tests disabled during build due to missing dependencies
%bcond_with tests

Name:           python%{python3_pkgversion}-%{srcname}
Version:        1.26.12
Release:        1%{?dist}
Summary:        Python HTTP library with thread-safe connection pooling and file post

License:        MIT
URL:            https://github.com/urllib3/urllib3
Source0:        %{url}/archive/%{version}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch


BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-rpm-macros
BuildRequires:  python%{python3_pkgversion}-setuptools
%if %{with tests}
BuildRequires:  python%{python3_pkgversion}-dateutil
BuildRequires:  python%{python3_pkgversion}-six
BuildRequires:  python%{python3_pkgversion}-pysocks
BuildRequires:  python%{python3_pkgversion}-pytest
BuildRequires:  python%{python3_pkgversion}-pytest-freezegun
BuildRequires:  python%{python3_pkgversion}-pytest-timeout
BuildRequires:  python%{python3_pkgversion}-tornado
BuildRequires:  python%{python3_pkgversion}-trustme
BuildRequires:  python%{python3_pkgversion}-idna
%endif

Requires:       ca-certificates
Requires:       python%{python3_pkgversion}-idna
Requires:       python%{python3_pkgversion}-six >= 1.16.0
Requires:       python%{python3_pkgversion}-pysocks

%description
Python HTTP module with connection pooling and file POST abilities.

%prep
%autosetup -p1 -n %{srcname}-%{version}
# Make sure that the RECENT_DATE value doesn't get too far behind what the current date is.
# RECENT_DATE must not be older that 2 years from the build time, or else test_recent_date
# (from test/test_connection.py) would fail. However, it shouldn't be to close to the build time either,
# since a user's system time could be set to a little in the past from what build time is (because of timezones,
# corner cases, etc). As stated in the comment in src/urllib3/connection.py:
#   When updating RECENT_DATE, move it to within two years of the current date,
#   and not less than 6 months ago.
#   Example: if Today is 2018-01-01, then RECENT_DATE should be any date on or
#   after 2016-01-01 (today - 2 years) AND before 2017-07-01 (today - 6 months)
# There is also a test_ssl_wrong_system_time test (from test/with_dummyserver/test_https.py) that tests if
# user's system time isn't set as too far in the past, because it could lead to SSL verification errors.
# That is why we need RECENT_DATE to be set at most 2 years ago (or else test_ssl_wrong_system_time would
# result in false positive), but before at least 6 month ago (so this test could tolerate user's system time being
# set to some time in the past, but not to far away from the present).
# Next few lines update RECENT_DATE dynamically.
recent_date=$(date --date "7 month ago" +"%Y, %_m, %_d")
sed -i "s/^RECENT_DATE = datetime.date(.*)/RECENT_DATE = datetime.date($recent_date)/" src/urllib3/connection.py

# Drop the dummyserver tests in koji.  They fail there in real builds, but not
# in scratch builds (weird).
rm -rf test/with_dummyserver/
# Don't run the Google App Engine tests
rm -rf test/appengine/
# Lots of these tests started failing, even for old versions, so it has something
# to do with Fedora in particular. They don't fail in upstream build infrastructure
rm -rf test/contrib/

# Tests for Python built without SSL, but Fedora builds with SSL. These tests
# fail when combined with the unbundling of backports-ssl_match_hostname
rm -f test/test_no_ssl.py

# Use the standard library instead of a backport
sed -i -e 's/^import mock/from unittest import mock/' \
       -e 's/^from mock import /from unittest.mock import /' \
    test/*.py docs/conf.py

%build
%py3_build


%install
%py3_install

# Unbundle the Python 3 build
rm -rf %{buildroot}/%{python3_sitelib}/urllib3/packages/six.py
rm -rf %{buildroot}/%{python3_sitelib}/urllib3/packages/__pycache__/six.*

mkdir -p %{buildroot}/%{python3_sitelib}/urllib3/packages/
ln -s %{python3_sitelib}/six.py %{buildroot}/%{python3_sitelib}/urllib3/packages/six.py
ln -s %{python3_sitelib}/__pycache__/six.cpython-%{python3_version_nodots}.opt-1.pyc \
      %{buildroot}/%{python3_sitelib}/urllib3/packages/__pycache__/
ln -s %{python3_sitelib}/__pycache__/six.cpython-%{python3_version_nodots}.pyc \
      %{buildroot}/%{python3_sitelib}/urllib3/packages/__pycache__/


%if %{with tests}
%check
%pytest -v
%endif


%files -n python%{python3_pkgversion}-%{srcname}
%license LICENSE.txt
%doc CHANGES.rst README.rst
%{python3_sitelib}/urllib3/
%{python3_sitelib}/urllib3-*.egg-info/


%changelog
* Tue Nov 29 2022 Charalampos Stratakis <cstratak@redhat.com> - 1.26.12-1
- Initial package
- Fedora contributions by:
      Adam Williamson <awilliam@redhat.com>
      Anna Khaitovich <akhaitov@redhat.com>
      Arun S A G <sagarun@gmail.com>
      Carl George <carl@george.computer>
      Charalampos Stratakis <cstratak@redhat.com>
      Dennis Gilmore <dennis@ausil.us>
      Haikel Guemar <hguemar@fedoraproject.org>
      Iryna Shcherbina <shcherbina.iryna@gmail.com>
      Jeremy Cline <jeremy@jcline.org>
      Karolina Surma <ksurma@redhat.com>
      Kevin Fenzi <kevin@scrye.com>
      Lukas Slebodnik <lslebodn@redhat.com>
      Lumir Balhar <lbalhar@redhat.com>
      Miro Hrončok <miro@hroncok.cz>
      Ralph Bean <rbean@redhat.com>
      Robert Kuska <rkuska@redhat.com>
      Slavek Kabrda <bkabrda@redhat.com>
      Tomas Hoger <thoger@redhat.com>
      Tom Callaway <spot@fedoraproject.org>
      Toshio Kuratomi <toshio@fedoraproject.org>
      yatinkarel <ykarel@redhat.com>
