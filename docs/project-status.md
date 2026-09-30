# disk project status

## Classification

Archive: a personal scratch directory, not a project. It bundles
(1) unreproducible bench experiments that invert a 2-D thermal-diffusion plant
with `scipy.optimize` and PyTorch/scikit-learn surrogates and (2) industrial-camera
SDK bindings plus minio/object-storage helper code. Kept for reference only.

## Status

Archive — scratch tooling, kept for reference. Never became a project: no tests,
no packaging, no README/LICENSE upstream, single-letter naming and
`Untitled*.ipynb` filenames. It is unreproducible rather than outdated — the
stack (PyTorch / SciPy / scikit-learn) is still current, but re-execution needs
the original bench, capture files (`ixy`, `ixy2`, `in.ixy`), a `mock.json` config,
a MVTec HALCON licence, a MinIO server, an MQTT broker and QSV-capable ffmpeg.

## Evidence

- `closed_form.ipynb` — analytic Green's-function solution for the same
  diffusion-decay PDE, usable as a self-contained ground-truth check; the only
  artifact that can be executed without lab hardware.
- `disk.py`, `disk0.py`, `disk1.py`, `disk2.py`, `nn.py` — a coherent personal
  investigation (steer 47 set-points / read 34 IR channels toward a target), in
  one consistent author idiom.
- `__main__.py` — HALCON + HIKROBOT + MQTT + MinIO inspection-pipeline prototype;
  documents how the camera/SDK plumbing was wired.
- `MvCameraControl_class.py`, `CameraParams_header.py`, `CameraParams_const.py`,
  `MvErrorDefine_const.py`, `PixelType_header.py` — **third-party** generated
  HIKROBOT MVS SDK bindings (bilingual generated comments, `MV_*` ctypes structs,
  `WinDLL`/`CDLL` loader). Vendored, not owner's work.

## Boundaries

- **Credential:** `__main__.py` contained a literal object-storage
  access-key/secret-key pair. It was removed during migration and replaced by
  `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` environment lookups. **The credential
  must be rotated by the owner** — it sat in a plaintext scratch file.
- **Network:** internal/private hosts in `disk*.py`, `tmpmodbus.py` and
  `Untitled-Copy1.ipynb` were replaced with `<REDACTED:...>` placeholders.
- **Licensing:** owner-authored files carry no licence (all-rights-reserved by
  default); the five vendored SDK binding files are third-party and should be
  dropped in favour of an external SDK dependency.
- **Provenance:** the HALCON inspection workflow and its MQTT topic schema encode
  an employer production process; general business is fine, internals are not.
  Not yet genericised — review before any wider publication.
- **Reproducibility:** no runnable entrypoint and no dependency lockfile; the
  dependency list in `README.md` is reconstructed from imports.
- **Scope:** migrating this directory does not imply support; it is an archive
  entry.

## Publication removals

- The five vendored HIKROBOT MVS SDK bindings (`MvCameraControl_class.py`,
  `CameraParams_header.py`, `CameraParams_const.py`, `MvErrorDefine_const.py`,
  `PixelType_header.py`) were removed before publication: they are third-party
  SDK code, not the owner's work. Install the SDK externally instead.
- Employer-internal MQTT topic names in `__main__.py` were genericised
  (`alg/ipc/job` -> `demo/vision/job`, `be/`/`ipc/` job-result paths, `be/cfg`).
