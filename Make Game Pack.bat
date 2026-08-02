@echo off
REM ==========================================================================
REM  Make Game Pack — compiles one archived game into a single GAME-PACK.md
REM  you can upload to an AI chat.  The game does NOT need to be running.
REM ==========================================================================
setlocal
cd /d "%~dp0"

echo.
echo   CIV 6 GAME PACK BUILDER
echo   ----------------------------------------------------------------

where uv >nul 2>nul
if %ERRORLEVEL%==0 (
    uv run python scripts\make_game_pack.py --lean %*
) else (
    python scripts\make_game_pack.py --lean %*
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo   Something went wrong ^(exit code %ERRORLEVEL%^).
)

echo.
pause
endlocal
