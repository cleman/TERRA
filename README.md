# TERRA

> ⚠️ This README is a work in progress.

---

## Installation

### Prerequisites

- **Python 3.10+**
- **tkinter** — usually bundled with Python, but may require a separate install on Linux:
  ```bash
  # Debian / Ubuntu
  sudo apt install python3-tk

  # Fedora
  sudo dnf install python3-tkinter
  ```
- **HiGHS** — the MILP solver used under the hood. Install via `highspy`, which is pulled automatically with Pyomo's optional dependencies (see below). No standalone binary needed.

---

### 1. Clone the repository

```bash
git clone https://github.com/cleman/TERRA.git
cd TERRA
```

---

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
```

| Platform | Command |
|----------|---------|
| Linux / macOS | `source .venv/bin/activate` |
| Windows (cmd) | `.venv\Scripts\activate.bat` |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |

You should see `(.venv)` appear in your prompt.

---

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install numpy matplotlib shapely Pillow pyomo highspy
```

> **What each package does:**
> | Package | Role |
> |---------|------|
> | `numpy` | Numerical arrays and geometry computations |
> | `matplotlib` | Map and solution rendering |
> | `shapely` | Obstacle polygon geometry and line-of-sight checks |
> | `Pillow` | Image handling in the GUI |
> | `pyomo` | MILP formulation |
> | `highspy` | HiGHS solver backend |

---

### 4. Run TERRA

**GUI mode:**
```bash
cd src/TERRA
python src/TERRA/__main_ui__.py
```

**CLI mode:**
```bash
cd src/TERRA
python src/TERRA/__main__.py
```

> **Note:** TERRA currently relies on implicit relative imports, so it must be run from inside `TERRA/`. This will be fixed in a future packaging update.

---

### Deactivating the virtual environment

When you're done, simply run:
```bash
deactivate
```