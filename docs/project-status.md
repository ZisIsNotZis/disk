# disk — archive record

Source: **INFERRED** from the published tree and the migration log. `README.md` and `README.zh-CN.md` are the public face; this file is the detailed record of what was migrated, what was removed, and what still cannot be reproduced.

## Classification

Archive: a personal scratch directory, not a product. It bundles two unrelated threads:

1. **Thermal-control / machine-vision experiments** — steering a physical 2-D heated plate (47 Modbus set-points, 34 IR sensor channels) toward a target field with online least squares, `scipy.optimize`, and PyTorch / scikit-learn surrogates (`disk*.py`, `nn.py`, `closed_form.ipynb`, `Untitled*.ipynb`).
2. **Industrial-camera SDK wrappers and object-storage plumbing** — HIKROBOT MVS camera capture, a HALCON inspection loop, MQTT job messages and MinIO uploads (`tmpmv.py`, `__main__.py`).

Kept for reference only. It never became a project: no tests, no packaging, no data files, single-letter naming and `Untitled*.ipynb` filenames.

## Inventory

- **Owner-authored:** `disk.py`, `disk0.py`, `disk1.py`, `disk2.py`, `nn.py`, `tmpmodbus.py`, `tmpmv.py`, `__main__.py`, `closed_form.ipynb`, `Untitled*.ipynb`, `README.md`, `README.zh-CN.md`, `CONTRIBUTING.md`, `assets/logo.svg`, `docs/project-status.md`.
- **Third-party, not included:** the generated HIKROBOT MVS Python bindings (`MvCameraControl_class.py`, `CameraParams_header.py`, `CameraParams_const.py`, `MvErrorDefine_const.py`, `PixelType_header.py`) were removed before publication. `tmpmv.py` and `__main__.py` still depend on them; install the SDK externally.
- **Not included:** capture files (`ixy`, `ixy2`, `in.ixy`), `mock.json`, images and `.mp4` files. The `.gitignore` excludes them.
- **License:** [`LICENSE`](../LICENSE) is AGPL-3.0-only for owner-authored code. It does not grant rights to redistribute the HIKROBOT MVS SDK or to use MVTec HALCON without a licence.

## What can be executed

- `nn.py` — importable; it only defines `Scale`.
- `closed_form.ipynb` — the analytical transient, steady-state and differentiable solvers are self-contained in principle (NumPy / SciPy / PyTorch), with no lab hardware required. The notebook has no stored outputs and was not re-executed during migration. Some cells are expensive by construction. It does not run top-to-bottom as shipped: the plotting cell `plt.imshow(o[-1])` references a variable `o` left over from the original scratch session, so run the function cells individually.
- `Untitled*.ipynb` — the simulator cells can run standalone; the cells that read `ixy` / `ixy2` cannot.
- **Correction:** `disk.py` is not import-safe. Its module-level code opens `in.ixy` and connects to the Modbus PLC and sensor socket on import. The same applies to `disk0.py`, `disk1.py`, `disk2.py`, `tmpmodbus.py` and `__main__.py`, which all execute hardware or file setup at import time.
- No end-to-end entrypoint exists. The scripts need the private bench network, capture files, a MVTec HALCON licence, the HIKROBOT MVS SDK, a MinIO server, an MQTT broker and an ffmpeg build with Intel QSV.

## Boundaries

- **Credential:** `__main__.py` contained a literal object-storage access-key/secret-key pair. It was removed and replaced by `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` environment lookups. **The credential must be rotated by the owner** — it sat in a plaintext scratch file.
- **Network:** internal/private hosts in `disk.py`, `disk0.py`, `disk1.py`, `disk2.py`, `tmpmodbus.py` and `Untitled-Copy1.ipynb` were replaced with `<REDACTED:...>` placeholders. Loopback references use `localhost`.
- **Licensing:** owner-authored files are AGPL-3.0-only. The five vendored SDK binding files are third-party and were removed; consume the vendor SDK as an external dependency.
- **Provenance:** the HALCON inspection workflow and its MQTT topic schema encode an employer production process. The topics were genericised (`alg/ipc/job` → `demo/vision/job`, `be/` and `ipc/` job-result paths, `be/cfg`), but the workflow itself is still employer-derived. Review before any wider publication.
- **Reproducibility:** no runnable entrypoint, no dependency lockfile, no recorded versions. The dependency list in `README.md` is reconstructed from imports.
- **Scope:** migrating this directory does not imply support. It is an archive entry. No CI workflows are included by design.

## Publication removals

- Five generated HIKROBOT MVS SDK bindings were removed: `MvCameraControl_class.py`, `CameraParams_header.py`, `CameraParams_const.py`, `MvErrorDefine_const.py`, `PixelType_header.py`.
- The MinIO literal credential was removed from `__main__.py` and replaced with environment lookups.
- Internal hosts and private IPs were replaced with `<REDACTED:...>` placeholders.
- Employer-internal MQTT topic names were genericised.
- Capture files, images, videos and local config (`mock.json`) were excluded from the repository.

## Corrections to earlier migration notes

- `LICENSE` now exists and is AGPL-3.0-only; an earlier note said owner-authored files were unlicensed and all-rights-reserved.
- `README.md` and `README.zh-CN.md` now exist; an earlier note said the original tree had no README.
- The SDK bindings are absent; an earlier evidence list named them as if they were present.
- `disk.py` is not import-safe; an earlier README claimed its Modbus and socket imports were unused at import time.
