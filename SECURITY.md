# Security Policy

TREMORMESH is safety-adjacent: people may make decisions based on its alerts.
We take two classes of issue seriously.

## 1. Software / firmware vulnerabilities

Standard stuff: memory safety in the firmware, injection in the server,
dependency CVEs, etc.

## 2. Integrity of the warning system (please read)

Because the network turns sensor reports into public alerts, the most
interesting attacks are not crashes, they are **false-alarm injection** and
**alert suppression**:

- Spoofed nodes publishing fake triggers to force an alert (panic, denial).
- A flood of triggers to exhaust the gateway or trip the cooldown.
- Tampering with node time so consensus windows can be gamed.

If you find a way to make the mesh cry wolf or stay silent when it should not,
that is a security issue, not just a bug.

## Reporting

- **Preferred:** open a private report via the repository's
  **Security advisories** tab ("Report a vulnerability").
- If that is unavailable, open a regular issue **without exploit details** and
  ask a maintainer to open a private channel.

Please give us a reasonable window to respond before public disclosure. This is
a volunteer project, so timelines are best-effort, but integrity issues get
priority triage.

## Supported versions

TREMORMESH is alpha (`0.x`). Only the latest `main` is supported; there are no
backported security fixes yet.
