# Gentoo Kernel sources development environment

Need to have write access to `/var/cache/distfiles`

## Standalone CLI (Poetry + Click)

This repository now exposes a standalone command line tool named `gkernel-dev`.

### Install

```bash
poetry install
```

### Usage

```bash
gkernel-dev --help
gkernel-dev run check-updates
gkernel-dev update-packages
```

Available workflows:

- `check-updates`
- `update-packages`
- `update-linux-patches`
- `push-changes`
- `check-rt-changes`
- `check-linux-patch-patches`
