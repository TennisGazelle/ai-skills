# lib/

Upstream skill sources tracked as **git submodules**. Canonical copies for agents live in [`../skills/`](../skills/) — we vendor (copy) meaningful skill content there rather than symlinking into `lib/`.

| Submodule | Upstream | Vendored into |
|-----------|----------|---------------|
| [`ponytail/`](ponytail/) | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | `skills/ponytail*`, plus `skills/ponytail/references/platform-native.md` |

## Update

From the repo root, run submodule branch parity and re-vendor:

```bash
./scripts/submod-parity.sh
```

Or invoke the `submod-parity` skill. That checks out each submodule’s branch matching the parent branch (with `master`↔`main` alias), re-copies mapped skill trees into `skills/`, and refreshes `CATALOG.md`.

## Clone

```bash
git clone --recurse-submodules <url>
# or after a plain clone:
git submodule update --init --recursive
```
