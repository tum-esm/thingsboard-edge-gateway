## Installation

**Set up virtual environment and install dependencies:**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Add local user to the `docker` group to run docker commands without sudo:

```bash
sudo usermod -a -G docker $USER
newgrp docker
```

**Perform type checks:**

```bash
bash scripts/run_mypy.sh
```

## TODOS

- in start_edge(): always reset git to correct commit even if image already exists
