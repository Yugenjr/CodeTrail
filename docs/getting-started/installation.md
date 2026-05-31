# Installation

Install CodeTrail from PyPI for standard use, or install an editable copy for development.

Quick install (user):

```bash
pip install codetrail
```

Development install (from source):

```bash
git clone https://github.com/your-org/codetrail.git
cd codetrail
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\Activate.ps1 # Windows PowerShell
pip install -e .
pip install -r requirements.txt
```

Notes:

- CodeTrail targets Python 3.11+. Use a virtual environment for development and testing.
- The package may require network access to query GitHub APIs.
