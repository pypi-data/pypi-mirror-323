@echo off
setlocal enabledelayedexpansion

:: Scan for .kicad_pro files
set count=0
for %%f in (.\*.kicad_pro) do (
    set /a count+=1
    set "file!count!=%%f"
)

:: If no files found
if %count%==0 (
    echo No .kicad_pro files found in the current directory.
    pause
    exit /b
)

:: If only one file found, open it directly
if %count%==1 (
    echo Opening the only .kicad_pro file found: %file1%
    start "" "%file1%"
    goto RUN_COMMAND
)

:: If multiple files found, ask which one to open
echo Multiple .kicad_pro files found:
for /l %%i in (1,1,%count%) do (
    echo %%i. !file%%i!
)
set /p choice="Enter the number of the file you want to open: "

:: Validate the user's choice
if not defined file%choice% (
    echo Invalid choice.
    pause
    exit /b
)

:: Open the selected file
echo Opening: !file%choice%!
start "" "!file%choice%!"

:RUN_COMMAND
:: Add a 5-second delay before running the Python command
echo Waiting for 5 seconds before launching Kicad Auto Lib..
timeout /t 5 /nobreak >nul

:: Run the Python command in the background
start /b python -m kicad_auto_lib

:: Pause to see the output
pause