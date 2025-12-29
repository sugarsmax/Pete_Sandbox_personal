**Page Built By:** AI Assistant (Claude)  
**Date:** 2025-10-30  

# Shared Python Virtual Environment Setup

Your shared venv is located at: `~/.python-venvs/pdms-shared`  
**Python Version:** 3.14.0

---

## Quick Start: Activate Shared venv in Any Project

### Option 1: Direct Source (Fastest)
```bash
source ~/.python-venvs/pdms-shared/bin/activate
```

### Option 2: Create Project-Specific Activation Script
In each project root, create or update `activate_env.sh`:

```bash
#!/bin/bash
echo "🚀 Activating shared Python environment..."
source ~/.python-venvs/pdms-shared/bin/activate
echo "✅ Environment activated! (Python $(python --version))"
```

Then run:
```bash
chmod +x activate_env.sh
./activate_env.sh
```

### Option 3: Use direnv (Recommended for Auto-Activation)
1. Install direnv: `brew install direnv`
2. Add to `~/.zshrc`: `eval "$(direnv hook zsh)"`
3. Create `.envrc` in each project:
```bash
source ~/.python-venvs/pdms-shared/bin/activate
```
4. Run `direnv allow` in the project directory

---

## View Installed Packages

```bash
source ~/.python-venvs/pdms-shared/bin/activate
pip list
```

## Add New Packages

```bash
source ~/.python-venvs/pdms-shared/bin/activate
pip install package_name
```

All projects using this venv will immediately have access to new packages.

---

## For Your Projects

### Street_View_Hyperlapse
Currently uses: `.venv_python313` (Python 3.13)  
**To migrate:**
1. Remove `cd $(dirname "$0")` from activate_env.sh
2. Update script to source the shared venv
3. Delete the `.venv_python313` directory to save space

### last.fm Projects
**To migrate:**
Create `activate_env.sh` in the project root pointing to shared venv

### Other Projects
Create activation scripts as needed

---

## Troubleshooting

**venv not found?**
```bash
ls -la ~/.python-venvs/pdms-shared/bin/activate
```

**Wrong Python version?**
```bash
python --version
```

**Need a different Python version?**
Create a new venv:
```bash
python3.13 -m venv ~/.python-venvs/py313-shared
```

---

**Agent Model Used:** claude-4.5-haiku-thinking

