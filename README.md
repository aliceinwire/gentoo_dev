# Gentoo Kernel sources development environment

Requirements:
- Gentoo developer SSH access
- pkgdev installed
- git configured
- write access to `/var/cache/distfiles`
- XDG config file at `~/.config/gkernel-dev/dev_settings.toml`

Example `dev_settings.toml`:
```
[gkernelci_try]
try_master = "..."
try_username = "..."
try_password = "..."
try_comment = "testing"
try_who = "arisut"
```

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
