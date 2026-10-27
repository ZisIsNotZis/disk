# Contributing

`disk` is an archive, not a maintained product. There is no feature roadmap, no test suite and no CI.

## What is useful

- Factual corrections, broken links and documentation drift.
- Clarifications that make the existing code or the migration record easier to understand.
- Reports of an incomplete redaction, especially a live credential or private hostname.

## What is not

- Hardware-specific patches you cannot test.
- New dependencies, packaging or build systems for an archive.
- Reintroducing redacted hostnames, internal MQTT topics or credentials.
- CI workflows. This repository deliberately has none.

## Security

Do not open a public issue for a live credential or private hostname. Use GitHub's private vulnerability reporting if it is enabled for this repository; otherwise contact the owner directly. Rotate or remove the value before discussing details in public.

## Process

Open an issue or pull request with the smallest change that fixes the problem. Keep the English and Chinese READMEs, `docs/project-status.md` and code comments in sync. Review is by inspection; there is no automated check to wait for.
