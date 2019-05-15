%global debug_package %{nil}
%global vector_version 2.0.0-beta.1

Name:           vector
Version:        2.0.0
Release:        0.1.beta.1%{?dist}
Summary:        On-host performance monitoring framework

License:        ASL 2.0
URL:            https://getvector.io
Source0:        https://github.com/Netflix/vector/archive/v%{vector_version}/vector-%{vector_version}.tar.gz
Source1:        vector_deps-%{vector_version}.tar.xz
Source2:        vector-httpd-conf
Source3:        vector-nginx-conf
Source4:        make_deps.sh

Patch0:         000-update-npm-packages.patch
Patch1:         001-router-basename.patch
Patch2:         002-update-default-config.patch
Patch3:         003-RPM-spec-and-make_deps.patch

ExclusiveArch: %{nodejs_arches} noarch

Requires:       httpd-filesystem
Requires:       nginx-filesystem
Suggests:       httpd
BuildRequires:  nodejs

# Declare all bundled nodejs modules - this is for security purposes so if
# nodejs-foo ever needs an update, affected packages can be easily identified.
# This is generated from package.json, with the actual version numbers from
# package-lock.json.
Provides: bundled(nodejs-babel-core) = 6.26.3
Provides: bundled(nodejs-babel-eslint) = 8.2.5
Provides: bundled(nodejs-babel-jest) = 23.2.0
Provides: bundled(nodejs-babel-loader) = 7.1.5
Provides: bundled(nodejs-babel-plugin-transform-async-to-generator) = 6.24.1
Provides: bundled(nodejs-babel-plugin-transform-class-properties) = 6.24.1
Provides: bundled(nodejs-babel-plugin-transform-object-rest-spread) = 6.26.0
Provides: bundled(nodejs-babel-plugin-transform-runtime) = 6.23.0
Provides: bundled(nodejs-babel-polyfill) = 6.26.0
Provides: bundled(nodejs-babel-preset-env) = 1.7.0
Provides: bundled(nodejs-babel-preset-es2015) = 6.24.1
Provides: bundled(nodejs-babel-preset-react) = 6.24.1
Provides: bundled(nodejs-chai) = 4.1.2
Provides: bundled(nodejs-color-hash) = 1.0.3
Provides: bundled(nodejs-copy-webpack-plugin) = 4.5.2
Provides: bundled(nodejs-css-loader) = 0.28.11
Provides: bundled(nodejs-d3-scale) = 2.1.0
Provides: bundled(nodejs-d3-selection) = 1.3.2
Provides: bundled(nodejs-d3-svg-legend) = 2.25.6
Provides: bundled(nodejs-enzyme) = 3.3.0
Provides: bundled(nodejs-enzyme-adapter-react-16) = 1.1.1
Provides: bundled(nodejs-eslint) = 5.1.0
Provides: bundled(nodejs-eslint-loader) = 2.0.0
Provides: bundled(nodejs-eslint-plugin-react) = 7.10.0
Provides: bundled(nodejs-estraverse) = 4.1.1
Provides: bundled(nodejs-file-loader) = 1.1.11
Provides: bundled(nodejs-font-awesome) = 4.6.1
Provides: bundled(nodejs-html-loader) = 0.5.5
Provides: bundled(nodejs-html-webpack-plugin) = 3.2.0
Provides: bundled(nodejs-http-server-spa) = 1.3.0
Provides: bundled(nodejs-jest) = 23.6.0
Provides: bundled(nodejs-less) = 3.5.3
Provides: bundled(nodejs-lodash-es) = 4.17.10
Provides: bundled(nodejs-lodash.clonedeep) = 4.5.0
Provides: bundled(nodejs-lodash.debounce) = 4.0.8
Provides: bundled(nodejs-lodash.isequal) = 4.5.0
Provides: bundled(nodejs-memoize-one) = 4.0.0
Provides: bundled(nodejs-moment) = 2.22.2
Provides: bundled(nodejs-prop-types) = 15.6.2
Provides: bundled(nodejs-react) = 16.4.1
Provides: bundled(nodejs-react-dom) = 16.4.1
Provides: bundled(nodejs-react-error-boundary) = 1.2.3
Provides: bundled(nodejs-react-grid-layout) = 0.16.6
Provides: bundled(nodejs-react-router-dom) = 4.3.1
Provides: bundled(nodejs-sass-loader) = 7.0.3
Provides: bundled(nodejs-semantic-ui-css) = 2.3.3
Provides: bundled(nodejs-semantic-ui-react) = 0.82.0
Provides: bundled(nodejs-semiotic) = 1.14.2
Provides: bundled(nodejs-style-loader) = 0.21.0
Provides: bundled(nodejs-superagent) = 3.8.3
Provides: bundled(nodejs-types-jest) = 23.1.4
Provides: bundled(nodejs-uglify-save-license) = 0.4.1
Provides: bundled(nodejs-url-loader) = 1.0.1
Provides: bundled(nodejs-webpack) = 4.15.1
Provides: bundled(nodejs-webpack-auto-inject-version) = 1.1.0
Provides: bundled(nodejs-webpack-cli) = 3.0.8
Provides: bundled(nodejs-webpack-merge) = 4.1.4
Provides: bundled(nodejs-why-did-you-update) = 0.1.1
Provides: bundled(nodejs-worker-loader) = 2.0.0
Provides: bundled(nodejs-wrench) = 1.5.9


%description
Vector is an open source on-host performance monitoring framework which exposes
hand picked high resolution system and application metrics to every engineer’s
browser. Having the right metrics available on-demand and at a high resolution
is key to understand how a system behaves and correctly troubleshoot
performance issues.


%prep
%setup -q -T -D -b 0 -n vector-%{vector_version}
%setup -q -T -D -b 1 -n vector-%{vector_version}

%patch0 -p1
%patch1 -p1
%patch3 -p1


%build
node_modules/webpack/bin/webpack.js --display-error-details --config webpack.prod.js

# apply patch 002-update-default-config.patch (updates default values in the
# configuration file) on the compiled webpack bundle instead of the sources,
# as otherwise tests which check for the upstream default port will fail
patch -p1 < %{PATCH2}


%install
install -d %{buildroot}%{_datadir}/%{name}
cp -aT dist %{buildroot}%{_datadir}/%{name}

# webserver configurations
install -D -p -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf
install -D -p -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/nginx/default.d/%{name}.conf


%check
node_modules/jest/bin/jest.js


%files
%dir %{_datadir}/%{name}
%{_datadir}/%{name}

%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%config(noreplace) %{_sysconfdir}/nginx/default.d/%{name}.conf

%license LICENSE
%doc CHANGELOG.md README.md


%changelog
* Wed May  8 2019 Andreas Gerstmayr <agerstmayr@redhat.com> 2.0.0-0.1.beta.1
- initial Vector package