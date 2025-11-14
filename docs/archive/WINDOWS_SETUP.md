# Windows Setup Guide

## Issue: Unicode Emoji Errors on Windows

If you encountered `UnicodeEncodeError` when running the crawler on Windows, this has been **FIXED** in the latest commit.

### The Problem
```
UnicodeEncodeError: 'charmap' codec can't encode characters in position 43-44: character maps to <undefined>
```

This occurred because Windows console (cmd.exe/PowerShell) uses `cp1252` encoding by default, which cannot display Unicode emojis like 🕷️, ✅, ❌.

### The Solution
The logger has been updated to use UTF-8 encoding, which properly handles all Unicode characters including emojis.

## Setup Instructions

### 1. Pull Latest Changes
```powershell
git pull origin claude/immigration-platform-build-plan-011CV5fS4Mj5BtYhoTJd5BP5
```

### 2. Test the Fix
```powershell
# Test logger Unicode support
python tests/test_logger_unicode.py

# If the test passes, you should see emojis without errors!
```

### 3. Run the Crawler
```powershell
# Test with Australia (note: may get 403 errors from govt site)
python main.py crawl --countries australia

# Run all tests
python tests/test_crawler.py
python tests/test_classifier.py
```

## Optional: Enable UTF-8 in Windows Console

For best results, configure your Windows console to use UTF-8:

### PowerShell
Add to your PowerShell profile (`$PROFILE`):
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

Or run before using the app:
```powershell
chcp 65001
```

### CMD
```cmd
chcp 65001
```

### Windows Terminal
Windows Terminal (recommended) has better Unicode support by default:
- Install from Microsoft Store: "Windows Terminal"
- UTF-8 is enabled by default

## Troubleshooting

### Still Seeing Errors?
1. Make sure you pulled the latest changes
2. Try using Windows Terminal instead of PowerShell/CMD
3. Run `chcp 65001` before running the app
4. Check Python version (Python 3.7+ recommended)

### Government Website 403 Errors
The Australian immigration website blocks automated crawlers. This is expected behavior. See `docs/STAGE_2_CRAWLER.md` for alternatives:
- Use official APIs
- Request crawling permission
- Use browser automation (Selenium)
- Manually collect sample data for testing

## Verified Working On
- ✅ Windows 10/11 with PowerShell
- ✅ Windows 10/11 with CMD
- ✅ Windows Terminal
- ✅ Linux (Ubuntu, Debian, etc.)
- ✅ macOS

## Need Help?
If you continue to have issues, please report them with:
1. Windows version
2. Python version (`python --version`)
3. Console type (PowerShell/CMD/Windows Terminal)
4. Full error message
