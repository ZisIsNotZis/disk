# disk

**Status: archive — scratch tooling, kept for reference.**

A personal scratch directory of Python scripts and Jupyter notebooks from an
abandoned bench-investigation era (2025-09 … 2026-02). It mixes two unrelated
threads:

1. **Thermal-control / machine-vision experiments** — steering a physical 2-D
   heated plate (47 Modbus set-points, 34 IR sensor channels) toward a target
   field with `scipy.optimize` and PyTorch / scikit-learn surrogates
   (`disk*.py`, `nn.py`, `closed_form.ipynb`, `Untitled*.ipynb`). `closed_form.ipynb`
   derives the analytic Green's-function solution for the same diffusion-decay
   PDE as a ground-truth check.
2. **Industrial-camera SDK wrappers and object-storage plumbing** — vendored
   HIKROBOT MVS Python bindings generated from the vendor headers with
   `xml2py` (`MvCameraControl_class.py`, `CameraParams_header.py`,
   `CameraParams_const.py`, `MvErrorDefine_const.py`, `PixelType_header.py`),
   plus a `minio` / object-storage upload helper in `__main__.py`.

There is no README, LICENSE, packaging or test suite in the original tree; this
file was added during migration.

## Status

Archive — scratch tooling, kept for reference. Never became a project: no tests,
no packaging, single-letter naming, `Untitled*.ipynb` filenames, and nothing in
it can be re-executed without the original bench. It is *unreproducible* rather
than *outdated* — PyTorch + SciPy + scikit-learn are still the current stack.

## What is (and is not) the owner's work

- **Owner-authored:** `disk.py`, `disk0.py`, `disk1.py`, `disk2.py`, `nn.py`,
  `tmpmodbus.py`, `tmpmv.py`, `__main__.py`, `closed_form.ipynb`,
  `Untitled*.ipynb`. No licence is attached; they default to all-rights-reserved.
- **Third-party, vendored:** `MvCameraControl_class.py`, `CameraParams_const.py`,
  `CameraParams_header.py`, `MvErrorDefine_const.py`, `PixelType_header.py`.
  These are generated HIKROBOT MVS SDK bindings (bilingual generated doc comments,
  `MV_*` ctypes structs, `WinDLL("MvCameraControl.dll")` loader). They are kept
  here only because they ship in the same scratch tree; consume the SDK as an
  external dependency instead of copying them.

## How to run

No runnable entrypoint. Every module targets lab hardware on a private network
(GigE cameras, Modbus TCP PLCs, a barcode/IR sensor socket) plus capture files
(`ixy`, `ixy2`, `in.ixy`) and a config (`mock.json`) that are **not** present in
this directory. `__main__.py` additionally needs a MVTec HALCON licence, a MinIO
server, an MQTT broker and ffmpeg with Intel QSV.

The only self-contained artifact is the numerical core of `closed_form.ipynb`
(numpy / scipy / torch / matplotlib):

```bash
jupyter nbconvert --to notebook --execute closed_form.ipynb
```

`disk.py` can be imported standalone (`python -c "import disk"`); its Modbus and
socket imports are unused at import time.

## Dependencies (reconstructed from imports)

| Dependency | Used by |
|---|---|
| Python 3 + Jupyter/IPython | all notebooks |
| PyTorch | `disk0.py`, `disk1.py`, `tmpmodbus.py` |
| NumPy, SciPy | `disk.py`, `disk2.py`, notebooks |
| scikit-learn | `disk.py`, `Untitled4/5.ipynb` |
| matplotlib | notebooks |
| `pymodbus` | `disk*.py`, `tmpmodbus.py`, `__main__.py` |
| `paho-mqtt` | `__main__.py` |
| `minio` | `__main__.py` |
| MVTec HALCON Python bindings | `__main__.py` (commercial, licensed) |
| HIKROBOT MVS SDK | `tmpmv.py`, `__main__.py` |
| ffmpeg (with `h264_qsv`) | `__main__.py` |

No `requirements.txt` / `pyproject.toml` / lockfile exists.

## Sanitisation notes

This tree was migrated for publication with the following removals — the code is
unchanged apart from redaction, and no credential value survives here:

- A literal **MinIO access-key/secret-key pair** in `__main__.py` was removed and
  replaced by `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` environment lookups. That
  credential was exposed in plaintext and **must be rotated**.
- **Internal hostnames / private IPs** (Modbus PLCs, IR/barcode sensor socket, an
  RTSP target) were replaced with `<REDACTED:...>` placeholders in `disk.py`,
  `disk0.py`, `disk1.py`, `disk2.py`, `tmpmodbus.py` and `Untitled-Copy1.ipynb`.
- Loopback references use `localhost`; no real internal address remains.

No data files (`.xlsx`/`.csv`/images/`.mp4`) are present in this tree.
