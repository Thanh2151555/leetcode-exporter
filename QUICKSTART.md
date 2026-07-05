# Quick Start Guide for LeetCode Exporter

## 5-Minute Setup

### Step 1: Install Python 3.12+

```bash
python --version  # Should be 3.12 or higher
```

### Step 2: Clone and Setup

```bash
# Navigate to the project directory
cd leetcode-exporter

# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Credentials

Edit `config.yaml` with your LeetCode username and password:

```yaml
leetcode:
  username: your_leetcode_username
  password: your_leetcode_password
```

### Step 4: Run the Exporter

```bash
python main.py
```

You'll see:
- Login progress
- Problem discovery (e.g., "Found 150 solved problems")
- Export progress bar with real-time updates
- Final summary

## Output Structure

After running, you'll have:

```
exported_solutions/
├── 0001-Two-Sum/
│   └── Solution.py
├── 0049-Group-Anagrams/
│   └── Solution.java
├── ...
└── README.md
```

## What Gets Committed to Git

- All solution files
- README.md (auto-generated index)
- No credentials or sensitive files

## Resume If Interrupted

If the process stops (e.g., network issue), just run again:

```bash
python main.py
```

It will skip already exported problems and continue from where it left off.

## Pushing to GitHub

The exporter will auto-commit but you may need to push:

```bash
git push origin main
```

Or configure the remote in `config.yaml` first.

## Troubleshooting

### Import errors?

```bash
# Verify virtual environment is activated
which python  # On Linux/Mac - should show venv path
pip list      # Should show selenium, gitpython, etc.
```

### Login fails?

1. Verify username/password in config.yaml
2. Try `headless: false` to watch the login process
3. Some accounts may need 2FA disabled for automation

### Can't find certain problems?

They may require premium access or be on different problemset pages. The crawler finds only public, accessible tasks.

## Advanced Configuration

See `config.yaml` for:
- `headless: false` - See the browser window (for debugging)
- `log_level: DEBUG` - More verbose logging
- `repo_path` - Where to store solutions
- `output_path` - Export directory

## Next Steps

1. Set up GitHub repository for solutions
2. Configure git remote: `git remote add origin <your-repo>`
3. Set up auto-run with cron (Linux/Mac) or Task Scheduler (Windows)

---

**Need help?** Check `README_PROJECT.md` for full documentation.
