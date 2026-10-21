# Security Review and Audit Report

## Executive Summary

A comprehensive security audit and review was conducted for the repository. The audit covered secret & content scanning, GitHub Actions workflow permissions and execution safety, dependency vulnerability analysis, custom build plugin checks, and governance policy. Remediations have been applied across workflow permissions, third-party script pinning, automated dependency management, and security patches.

---

## 1. Secret & Content Scanning

- **Status**: PASSED
- **Findings**:
  - Full automated scan performed using `detect-secrets` and pattern checks across the codebase.
  - No active passwords, private keys, or API tokens were found in source files or configuration files.
  - High entropy strings identified in `_config.yml` and `_includes/` correspond to public SRI hashes, CDN URLs, or template defaults.
- **Controls Implemented**:
  - Configured local pre-commit hooks in `.pre-commit-config.yaml` (`detect-private-key`, `gitleaks`).
  - Added `.github/workflows/secret-scan.yml` running Gitleaks CLI on every push, pull request, and weekly schedule.

---

## 2. GitHub Actions Security Audit

- **Status**: REMEDIATED
- **Findings & Actions Taken**:
  - **Least Privilege Permissions**: Added explicit minimal `permissions:` blocks (e.g. `permissions: contents: read`) to all workflow files in `.github/workflows/` so `GITHUB_TOKEN` access is strictly scoped.
  - **Pinned Remote Script (`update-tocs.yml`)**: Pinned the remote `gh-md-toc` script download in `update-tocs.yml` to a specific, immutable commit SHA (`e9e9197682f98d98d22ea6f1ae39afd95a054481`) instead of unpinned `main`.
  - **Automated Security Updates**: Added `.github/dependabot.yml` configured for weekly security updates across GitHub Actions, Bundler (gems), pip (Python packages), and npm (Node packages).

---

## 3. Dependency Vulnerability Audit

- **Ruby Gems (`Gemfile.lock`)**:
  - **Status**: REMEDIATED
  - `bundler-audit` identified vulnerability advisories in `nokogiri` (1.19.0), including regular expression backtracking (CVE-2026-79770) and memory leaks (CVE-2026-79771).
  - _Remediation_: Updated `nokogiri` to version `1.19.4` in `Gemfile.lock`.
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
