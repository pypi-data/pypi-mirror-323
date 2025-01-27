Name: cloney
Version: 0.1.0
Release: 1%{?dist}
Summary: Cloney - Cloud Storage Migration Tool
License: MIT
Source0: %{name}-%{version}.tar.gz
BuildArch: noarch
Requires: python3, python3-boto3, python3-google-cloud-storage, python3-oss2, python3-azure-storage-blob

%description
A command-line tool to migrate files between S3, GCS, OSS, and Azure.

%prep
%setup -q

%install
mkdir -p %{buildroot}/usr/local/bin
cp src/cloney/main.py %{buildroot}/usr/local/bin/cloney
chmod +x %{buildroot}/usr/local/bin/cloney

%files
/usr/local/bin/cloney
