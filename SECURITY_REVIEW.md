# Security Review and Audit Report

## Executive Summary

A comprehensive security audit and review was conducted for the repository. The audit covered secret & content scanning, GitHub Actions workflow permissions and execution safety, dependency vulnerability analysis, and custom build plugin checks.

---

## 1. Secret & Content Scanning

- **Status**: PASSED
- **Findings**:
  - Full automated scan performed using `detect-secrets` and pattern checks across the codebase.
  - No active passwords, private keys, or API tokens were found in source files or configuration files.
  - High entropy strings identified in `_config.yml` and `_includes/` correspond to public SRI hashes, CDN URLs, or template defaults.
- **Controls Implemented**:
  - Configured local pre-commit hooks in `.pre-commit-config.yaml` (`detect-private-key`, `gitleaks`).
  - Added `.github/workflows/secret-scan.yml` running Gitleaks Action on every push, pull request, and weekly schedule.

---

## 2. GitHub Actions Security Audit

- **Findings & Risks**:
  - **Unbounded Permissions**: Several workflow files (`deploy.yml`, `broken-links.yml`, `prettier.yml`, etc.) rely on default `GITHUB_TOKEN` permissions rather than declaring explicit least-privilege `permissions:` blocks.
  - **Remote Script Execution Risk (`update-tocs.yml`)**: `update-tocs.yml` fetched and executed an unpinned raw shell script from a third-party GitHub repository (`curl https://raw.githubusercontent.com/george-gca/github-markdown-toc/main/gh-md-toc -o gh-md-toc`).
  - **Action Versioning**: Third-party community actions are referenced using floating tags (e.g., `@v2`, `@v5`) rather than commit SHAs.
- **Recommendations**:
  - Define explicit `permissions:` blocks (e.g. `permissions: contents: read`) at job or workflow top-level.
  - Pin external third-party script downloads to immutable commit SHAs or vendor the tool directly.
  - Consider adding Dependabot for automated action update management (`.github/dependabot.yml`).

---

## 3. Dependency Vulnerability Audit

- **Ruby Gems (`Gemfile.lock`)**:
  - `bundler-audit` check identified vulnerability advisories in `nokogiri` (version 1.19.0), including regular expression backtracking (CVE-2026-79770) and memory leaks (CVE-2026-79771).
  - _Mitigation_: Update `nokogiri` to version `>= 1.19.4` by executing `bundle update nokogiri`.
- **Python Packages (`requirements.txt`)**:
  - `pip-audit -r requirements.txt` passed with 0 known vulnerabilities.
- **Node.js Packages (`package.json`)**:
  - `npm audit` passed with 0 known vulnerabilities.

---

## 4. Custom Plugins and Build Scripts Audit

- **`_plugins/download-3rd-party.rb`**:
  - Uses `open-uri` to fetch third-party fonts and assets. Contains checks (`!url.start_with?('|')`) to prevent `open-uri` command execution vectors.
- **`bin/sync_orcid_publications.py` & `bin/update_scholar_citations.py`**:
  - Standard Python network calls using `urllib.request`. No arbitrary command execution or untrusted input injection risks found.
- **`bin/entry_point.sh`**:
  - Container entrypoint script uses `set -euo pipefail` for safe bash error handling.

---

## 5. Security Policy and Governance

- **Added `SECURITY.md`**:
  - Establishes private vulnerability disclosure procedures, instructing security researchers to use GitHub Private Vulnerability Reporting or direct maintainer contact rather than public issues.
