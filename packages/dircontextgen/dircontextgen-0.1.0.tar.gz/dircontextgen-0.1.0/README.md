# Directory Context Generator 🌳📂

**Your AI pair programmer's favorite tool!**
Now on PyPI 🎉 (`pip install dircontextgen --pre`)

When sharing code with Claude/GPT/Deepseek, avoid:

- 🚫 Accidental `node_modules` dumps
- 🚫 Secret leakage (we respect `.gitignore`)
- 🚫 Gigabyte-sized log files

## Quick Start 🚀

```bash
# Install the pre-release
pip install dircontextgen --pre

# Basic usage
dircontextgen ./your-project > context.txt

# Just show me the structure!
dircontextgen --tree-only ./src

# Precision mode
dircontextgen \
  --include-pattern "*.py" \
  --exclude-pattern "tests/" \
  --max-file-size 500KB \
  ./project
```

## File Inclusion Logic 🧠

1. **Must Have** - Matches `.dirtarget` patterns
2. **Must NOT Have** - Blocked by `.gitignore`/`.dirignore`
3. **Size Matters** - Default 1MB cutoff (configurable)

Example `.dirignore`:

```text
# No time for these!
*.log
secrets/
**/test_data/
```

## Pro Tips 💡

```bash
# Find why files are excluded
dircontextgen --verbose ./project

# Windows path? No problem!
dircontextgen 'C:\Users\me\project'  # Quotes save lives!

# Mix multiple ignore files
dircontextgen -i .dirignore -i custom.ignore ./src
```

## Test Drive 🧪

```bash
# Generate test environment
python -m pytest tests/ --setup-test-data

# See what AI would see
dircontextgen --tree-only tests/test_data
```

## Cross-Platform Notes 🌐

- Paths work with both `/` and `\`
- Case-insensitive pattern matching on Windows
- Tested on Python 3.8+ (Windows)
  - NOTE: UNTESTED ON UNIX SYSTEMS

```powershell
# PowerShell magic
dircontextgen (Join-Path $pwd "project") -o ai_context.md
```

## Why We're Better 😎

| Feature      | dircontextgen | Raw `tree` |
| ------------ | ------------- | ------------ |
| AI-safe      | ✅            | ❌           |
| Size limits  | ✅            | ❌           |
| .gitignore   | ✅            | ❌           |
| Windows love | ✅            | ❌           |

---

**License**: Apache 2.0 - Use freely, contribute kindly!
**Need Help?** [Open an issue](https://github.com/yourusername/dircontextgen/issues) - We respond faster than GPT-4!
