@echo off
REM Civ 6 AI Coach launcher.
REM
REM Prerequisites:
REM   1. Civ 6 is running with EnableTuner=1 in AppOptions.txt
REM      (Documents\My Games\Sid Meier's Civilization VI\AppOptions.txt).
REM   2. A save is loaded (not the main menu).
REM
REM Once this window says "hotkey ready", press Ctrl+Shift+C anywhere on
REM your desktop to grab a snapshot.  The Markdown copy of the snapshot is
REM placed on your clipboard automatically; paste into ChatGPT / Claude /
REM Gemini.  The JSON + Markdown files are also written to
REM   C:\Users\jakeb\civ6-mcp\output\
REM
REM Read-only.  Never sends commands that mutate game state.  Base game only.

setlocal
cd /d "%~dp0"
title Civ6 AI Coach
echo Starting Civ6 AI Coach...
echo (Leave this window open. Press Ctrl+C to stop.)
echo.
uv run python -m civ_mcp.coach --verbose
echo.
echo Coach exited.
pause
