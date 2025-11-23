**Page Built By:** AI Assistant (Claude)  
**Date:** 2025-10-30

# direnv Auto-Activation Setup

Auto-magically activates your shared Python venv when you `cd` into any project directory.

---

## ✅ Setup Complete!

### What was done:
1. ✅ Installed `direnv` (2.37.1)
2. ✅ Added `eval "$(direnv hook zsh)"` to `~/.zshrc`
3. ✅ Created `.envrc` files in:
   - `/Pete_Sandbox_personal/` (root)
   - `/Street_View_Hyperlapse/`
   - `/last.fm/`
   - `/Music_migration_Tidal_Spotify/`
4. ✅ Allowed direnv for all projects with `direnv allow`

---

## How It Works

### Before direnv:
```bash
cd ~/projects/project1
# No venv active ❌

cd ~/projects/project2
# No venv active ❌
```

### After direnv:
```bash
cd ~/projects/project1
# 🚀 Venv auto-activates! Python 3.14.0 ready
direnv: loading ~/projects/project1/.envrc

cd ~/projects/project2
# 🚀 Venv auto-activates! Python 3.14.0 ready
direnv: loading ~/projects/project2/.envrc
```

---

## Testing It

**In your terminal, try:**
```bash
cd /path/to/Pete_Sandbox_personal
# You should see: direnv: loading .envrc

python --version
# Should show: Python 3.14.0

pip list
# Should show packages from pdms-shared venv
```

---

## Common Commands

### View direnv status
```bash
direnv status
```

### Allow a new .envrc
```bash
direnv allow
```

### Deny/revoke .envrc
```bash
direnv deny
```

### Clear all direnv state
```bash
direnv prune
```

### Add a new project
1. Create `.envrc` in the project:
```bash
echo 'source ~/.python-venvs/pdms-shared/bin/activate' > .envrc
```
2. Allow it:
```bash
direnv allow
```

---

## ⚠️ Important Notes

### Python Alias Override
Your `~/.zshrc` has:
```bash
alias python="/opt/homebrew/bin/python3.12"
```

This overrides the venv Python. To use the venv's Python (3.14.0), use:
```bash
/usr/bin/python      # Or full path
~/.python-venvs/pdms-shared/bin/python  # Direct path
```

**Alternative:** Remove the alias or comment it out for venv to work properly.

### Check Actual Python Version
```bash
# See which python is active
which python

# See actual venv python
~/.python-venvs/pdms-shared/bin/python --version  # Shows 3.14.0

# See aliased python
python --version  # May show 3.12 due to alias
```

---

## Troubleshooting

### direnv not loading .envrc?
```bash
# Reload shell
exec zsh

# Try again
cd /path/to/project
```

### "direnv: command not found"?
```bash
# Check if direnv is installed
which direnv
# Should show: /opt/homebrew/bin/direnv

# If not found, restart terminal and try:
exec zsh
```

### Want to disable direnv temporarily?
```bash
# Deny the .envrc
direnv deny

# Or disable globally in this shell
unset DIRENV_DIR
```

### Need to use a different venv?
1. Edit `.envrc`:
```bash
source ~/.python-venvs/your-other-venv/bin/activate
```
2. Reload:
```bash
direnv reload
```

---

## Next Steps (Optional)

### 1. Remove old project venvs to save space
```bash
# Street_View_Hyperlapse used to have .venv_python313
# Now using shared venv instead, so can delete:
rm -rf /path/to/Street_View_Hyperlapse/.venv_python313
```

### 2. Update your project activation scripts
Your `activate_env.sh` scripts can now be simplified or removed since direnv handles it.

### 3. Add to .gitignore (if using git)
```bash
# Direnv local files (optional)
.direnv/
.envrc.local
```

---

**Agent Model Used:** claude-4.5-haiku-thinking

