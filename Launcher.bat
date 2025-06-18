@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM Mudrikam Launcher v.1.0.0
REM Universal Python Application Launcher (Command-Line Interface)
REM
REM This launcher provides a robust, user-friendly CLI experience
REM for running Python applications on Windows. It detects or installs Python,
REM manages dependencies, and launches your main Python program.
REM
REM USAGE:
REM - Double-click or run this batch file from the command prompt.
REM - The launcher will guide you through Python detection, installation, dependency management, and running your app.
REM
REM MAIN FEATURES:
REM 1. Detects local or system Python installations (prefers portable/local first).
REM 2. Offers to download and set up portable Python or official installer if needed.
REM 3. Manages dependencies via requirements.txt (auto-creates if missing).
REM 4. Verifies installation and launches your main.py.
REM 5. All steps are logged for troubleshooting.
REM
REM ============================================================================
REM MIT License
REM 
REM Copyright (c) 2024 Mudrikam Launcher
REM 
REM Permission is hereby granted, free of charge, to any person obtaining a copy
REM of this software and associated documentation files (the "Software"), to deal
REM in the Software without restriction, including without limitation the rights
REM to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
REM copies of the Software, and to permit persons to whom the Software is
REM furnished to do so, subject to the following conditions:
REM 
REM The above copyright notice and this permission notice shall be included in all
REM copies or substantial portions of the Software.
REM 
REM THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
REM IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
REM FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
REM AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
REM LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
REM OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
REM SOFTWARE.
REM ============================================================================

@echo off
setlocal enabledelayedexpansion

REM -----------------------------------------------------------------------------
REM Define ESC character for ANSI color codes
REM -----------------------------------------------------------------------------
for /f %%A in ('echo prompt $E ^| cmd') do set "ESC=%%A"

REM -----------------------------------------------------------------------------
REM EnableColors: Enables ANSI color codes for supported Windows versions.
REM -----------------------------------------------------------------------------
call :EnableColors

REM -----------------------------------------------------------------------------
REM Set the title of the CLI window for clarity.
REM -----------------------------------------------------------------------------
title Mudrikam Launcher v.1.0.0 - Universal Python Application Launcher

REM -----------------------------------------------------------------------------
REM Change to the script's directory to ensure relative paths work.
REM -----------------------------------------------------------------------------
cd /d "%~dp0"

REM -----------------------------------------------------------------------------
REM Create logs directory and start logging session.
REM -----------------------------------------------------------------------------
if not exist "logs" mkdir "logs" >nul 2>&1
REM Use only date for log filename, so one log per day
set "LOGFILE=logs\mudrikam_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log"
set "LOGFILE=%LOGFILE: =0%"
if not exist "%LOGFILE%" (
    echo Starting Mudrikam Launcher at %date% %time% > "%LOGFILE%"
) else (
    echo. >> "%LOGFILE%"
    echo --- New session at %date% %time% --- >> "%LOGFILE%"
)

REM -----------------------------------------------------------------------------
REM Print CLI header for clarity.
REM -----------------------------------------------------------------------------
call :PrintHeader
echo.

REM -----------------------------------------------------------------------------
REM Check Windows version compatibility (for logging and info).
REM -----------------------------------------------------------------------------
call :CheckSystemCompatibility

REM ===== STEP 1: Python Detection =====
REM Detects Python in local directory, then system, then offers install options.
call :PrintStep "1/4" "Detecting Python Environment"

REM -----------------------------------------------------------------------------
REM Define variables for Python paths and versions
REM -----------------------------------------------------------------------------
set "LOCAL_PYTHON=python\windows\python.exe"
set "PYTHON_CMD="
set "PYTHON_VERSION="
set "MIN_PYTHON_VERSION=3.8"

REM -----------------------------------------------------------------------------
REM Check if local Python exists and is functional
REM -----------------------------------------------------------------------------
if exist "%LOCAL_PYTHON%" (
    call :TestPython "%LOCAL_PYTHON%"
    if !ERRORLEVEL! EQU 0 (
        call :PrintSuccess "Python found in local directory"
        set "PYTHON_CMD=%LOCAL_PYTHON%"
        goto :PYTHON_FOUND
    ) else (
        call :PrintWarning "Local Python found but not functional, checking alternatives..."
        echo Local Python test failed >> "%LOGFILE%"
    )
)

REM -----------------------------------------------------------------------------
REM Check for system Python installations
REM -----------------------------------------------------------------------------
call :CheckSystemPython

if defined PYTHON_CMD goto :PYTHON_FOUND

REM -----------------------------------------------------------------------------
REM Python not found, offer installation options
REM -----------------------------------------------------------------------------
call :PrintError "Python is not installed or not functional on your device"
echo.
call :PrintInfo "Python is required to run this application. Please select an option:"
echo.
echo [1] %GREEN%Download portable Python %RESET%(Recommended - no system changes)
echo [2] %CYAN%Download official Python installer %RESET%(System-wide installation)
echo [3] %YELLOW%Manual installation guide%RESET%
echo [4] %RED%Exit%RESET%
echo.

:PYTHON_CHOICE
set /p choice="%BLUE%Enter your choice (1-4): %RESET%"

if "%choice%"=="1" (
    goto :DOWNLOAD_PORTABLE
) else if "%choice%"=="2" (
    goto :DOWNLOAD_INSTALLER
) else if "%choice%"=="3" (
    goto :MANUAL_GUIDE
) else if "%choice%"=="4" (
    goto :END
) else (
    call :PrintError "Invalid choice. Please enter 1, 2, 3, or 4"
    goto :PYTHON_CHOICE
)

:DOWNLOAD_PORTABLE
echo.
call :PrintStep "Installing" "Downloading Portable Python"

REM -----------------------------------------------------------------------------
REM Create python directory structure
REM -----------------------------------------------------------------------------
if not exist "python\windows" mkdir "python\windows" >nul 2>&1

REM -----------------------------------------------------------------------------
REM Try multiple download methods for better compatibility
REM -----------------------------------------------------------------------------
call :DownloadFile "https://www.python.org/ftp/python/3.12.0/python-3.12.0-embed-amd64.zip" "python_portable.zip"
if !ERRORLEVEL! NEQ 0 goto :DOWNLOAD_FAILED

call :PrintStep "Installing" "Setting up Portable Python"
call :ExtractPortablePython
if !ERRORLEVEL! NEQ 0 goto :SETUP_FAILED

set "PYTHON_CMD=%CD%\python\windows\python.exe"
goto :PYTHON_FOUND

:DOWNLOAD_INSTALLER
echo.
call :PrintStep "Installing" "Downloading Python Installer"

call :DownloadFile "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe" "python_installer.exe"
if !ERRORLEVEL! NEQ 0 goto :DOWNLOAD_FAILED

call :PrintStep "Installing" "Running Python Installer"
call :RunPythonInstaller
if !ERRORLEVEL! NEQ 0 goto :INSTALL_FAILED

REM -----------------------------------------------------------------------------
REM Refresh PATH and check again
REM -----------------------------------------------------------------------------
call :RefreshEnvironment
call :CheckSystemPython
goto :PYTHON_FOUND

:MANUAL_GUIDE
call :ShowManualGuide
goto :PYTHON_CHOICE

:PYTHON_FOUND
call :PrintSuccess "Python successfully detected: !PYTHON_CMD!"
call :GetPythonVersion "!PYTHON_CMD!"
call :PrintInfo "Python version: !PYTHON_VERSION!"
echo.

REM -----------------------------------------------------------------------------
REM Verify Python version meets minimum requirements
REM -----------------------------------------------------------------------------
call :VerifyPythonVersion "!PYTHON_VERSION!" "%MIN_PYTHON_VERSION%"
if !ERRORLEVEL! NEQ 0 (
    call :PrintWarning "Python version !PYTHON_VERSION! detected. Minimum required: %MIN_PYTHON_VERSION%"
    call :PrintInfo "The application may not work correctly with this version."
    echo.
)

REM ===== STEP 2: Install Dependencies =====
REM Ensures all required Python packages are installed.
call :PrintStep "2/4" "Managing Dependencies"

call :SetupRequirements
call :InstallDependencies "!PYTHON_CMD!"
if !ERRORLEVEL! NEQ 0 goto :DEPENDENCY_FAILED

call :PrintSuccess "Dependencies installed successfully"
echo.

REM ===== STEP 3: Verify Installation =====
REM Verifies that all dependencies are correctly installed.
call :PrintStep "3/4" "Verifying Installation"

call :VerifyInstallation "!PYTHON_CMD!"
if !ERRORLEVEL! NEQ 0 goto :VERIFICATION_FAILED

call :PrintSuccess "Installation verification completed"
echo.

REM ===== STEP 4: Run Main Program =====
REM Launches your main Python application.
call :PrintStep "4/4" "Starting Application"

REM -----------------------------------------------------------------------------
REM Check if main application exists
REM -----------------------------------------------------------------------------
if not exist "main.py" (
    call :PrintError "main.py not found in the current directory"
    call :PrintInfo "Please ensure all application files are present"
    goto :END
)

echo.
call :PrintInfo "Launching application..."
echo.

REM -----------------------------------------------------------------------------
REM Run the main program with error handling
REM -----------------------------------------------------------------------------
"!PYTHON_CMD!" main.py

set "EXIT_CODE=!ERRORLEVEL!"
if !EXIT_CODE! NEQ 0 (
    echo.
    call :PrintWarning "Program exited with code: !EXIT_CODE!"
    echo Program exit code: !EXIT_CODE! >> "%LOGFILE%"
) else (
    echo.
    call :PrintSuccess "Program completed successfully"
)

goto :END

REM ===== ERROR HANDLERS =====
REM Handles download, setup, install, and verification failures gracefully.
:DOWNLOAD_FAILED
call :PrintError "Failed to download Python. Please check your internet connection"
call :PrintInfo "You can also download Python manually from: https://www.python.org/downloads/"
goto :END

:SETUP_FAILED
call :PrintError "Failed to set up portable Python"
call :PrintInfo "Please try the official installer option instead"
goto :PYTHON_CHOICE

:INSTALL_FAILED
call :PrintError "Python installation failed or was cancelled"
call :PrintInfo "Please try the portable option or install manually"
goto :PYTHON_CHOICE

:DEPENDENCY_FAILED
call :PrintError "Failed to install required dependencies"
call :PrintInfo "Please check your internet connection and try again"
goto :END

:VERIFICATION_FAILED
call :PrintWarning "Installation verification failed"
call :PrintInfo "The application may not work correctly"
set /p continue="Do you want to continue anyway? (y/n): "
if /i "!continue!"=="y" goto :PYTHON_FOUND
goto :END

REM ===== UTILITY FUNCTIONS =====
REM All functions below are CLI utilities for color, info, and operations.

REM -----------------------------------------------------------------------------
REM EnableColors: Enables ANSI color codes for CLI color output.
REM -----------------------------------------------------------------------------
:EnableColors
:: Enable ANSI color codes for Windows 10+
for /f "tokens=2 delims=[]" %%x in ('ver') do set "winver=%%x"
echo !winver! | findstr /r "10\.[0-9] 11\.[0-9]" >nul
if !ERRORLEVEL! EQU 0 (
    reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1
    set "RED=%ESC%[31m"
    set "GREEN=%ESC%[32m"
    set "YELLOW=%ESC%[33m"
    set "BLUE=%ESC%[34m"
    set "CYAN=%ESC%[36m"
    set "RESET=%ESC%[0m"
) else (
    set "RED="
    set "GREEN="
    set "YELLOW="
    set "BLUE="
    set "CYAN="
    set "RESET="
)
exit /b 0

REM -----------------------------------------------------------------------------
REM PrintHeader: Prints CLI banner for clarity.
REM -----------------------------------------------------------------------------
:PrintHeader
call :EchoColor "%CYAN%=================================================================%RESET%"
call :EchoColor "%CYAN%              Mudrikam Launcher v.1.0.0%RESET%"
call :EchoColor "%CYAN%           Universal Python Application Launcher%RESET%"
call :EchoColor "%CYAN%=================================================================%RESET%"
call :EchoColor "%GREEN%    Compatible with Windows 8/10/11 and multiple Python versions%RESET%"
call :EchoColor "%YELLOW%                        MIT Licensed%RESET%"
exit /b 0

REM -----------------------------------------------------------------------------
REM PrintStep, PrintSuccess, PrintWarning, PrintError, PrintInfo:
REM CLI output helpers for clear, color-coded messages.
REM -----------------------------------------------------------------------------
:PrintStep
call :EchoColor "%BLUE%[%~1] %~2...%RESET%"
echo [%~1] %~2... >> "%LOGFILE%"
exit /b 0

:PrintSuccess
call :EchoColor "%GREEN%✓ %~1%RESET%"
echo SUCCESS: %~1 >> "%LOGFILE%"
exit /b 0

:PrintWarning
call :EchoColor "%YELLOW%⚠ %~1%RESET%"
echo WARNING: %~1 >> "%LOGFILE%"
exit /b 0

:PrintError
call :EchoColor "%RED%✗ %~1%RESET%"
echo ERROR: %~1 >> "%LOGFILE%"
exit /b 0

:PrintInfo
call :EchoColor "%CYAN%ℹ %~1%RESET%"
exit /b 0

REM -----------------------------------------------------------------------------
REM EchoColor: Helper to print colored text using ANSI escape codes
REM -----------------------------------------------------------------------------
:EchoColor
setlocal EnableDelayedExpansion
set "str=%~1"
REM Remove surrounding quotes if any
if "!str:~0,1!"=="^"" set "str=!str:~1,-1!"
REM Print without newline
<nul set /p="!str!"
echo.
endlocal
exit /b 0

REM -----------------------------------------------------------------------------
REM CheckSystemCompatibility: Logs and displays Windows version.
REM -----------------------------------------------------------------------------
:CheckSystemCompatibility
for /f "tokens=2 delims=[]" %%x in ('ver') do set "winver=%%x"
echo Windows version: !winver! >> "%LOGFILE%"
call :PrintInfo "Running on Windows: !winver!"
exit /b 0

REM -----------------------------------------------------------------------------
REM TestPython: Checks if a Python executable is functional.
REM -----------------------------------------------------------------------------
:TestPython
set "test_python=%~1"
"%test_python%" --version >nul 2>&1
if !ERRORLEVEL! NEQ 0 exit /b 1

:: Test basic Python functionality
"%test_python%" -c "import sys; print('Python test OK')" >nul 2>&1
exit /b !ERRORLEVEL!

REM -----------------------------------------------------------------------------
REM CheckSystemPython: Searches for Python in PATH and common locations.
REM -----------------------------------------------------------------------------
:CheckSystemPython
:: Check multiple Python commands in order of preference
set "python_candidates=python python3 py"

for %%p in (!python_candidates!) do (
    call :TestPython "%%p"
    if !ERRORLEVEL! EQU 0 (
        call :PrintSuccess "Python found in system PATH: %%p"
        set "PYTHON_CMD=%%p"
        exit /b 0
    )
)

:: Check common installation paths
set "common_paths=C:\Python3*\python.exe C:\Program Files\Python3*\python.exe C:\Program Files (x86)\Python3*\python.exe"

for %%p in (!common_paths!) do (
    if exist "%%p" (
        call :TestPython "%%p"
        if !ERRORLEVEL! EQU 0 (
            call :PrintSuccess "Python found at: %%p"
            set "PYTHON_CMD=%%p"
            exit /b 0
        )
    )
)

exit /b 1

REM -----------------------------------------------------------------------------
REM DownloadFile: Downloads a file using multiple CLI methods.
REM -----------------------------------------------------------------------------
:DownloadFile
set "download_url=%~1"
set "output_file=%~2"
set "download_success=0"

call :PrintInfo "Attempting download from official repository..."

REM -----------------------------------------------------------------------------
REM Method 1: PowerShell (Windows 7+)
REM -----------------------------------------------------------------------------
powershell -Command "try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('%~1', '%~2'); exit 0 } catch { exit 1 }" >nul 2>&1
if !ERRORLEVEL! EQU 0 set "download_success=1"

REM -----------------------------------------------------------------------------
REM Method 2: bitsadmin (fallback)
REM -----------------------------------------------------------------------------
if !download_success! EQU 0 (
    call :PrintInfo "Trying alternative download method..."
    bitsadmin /transfer "MudrikamDownload" /priority foreground "%~1" "%CD%\%~2" >nul 2>&1
    if !ERRORLEVEL! EQU 0 set "download_success=1"
)

REM -----------------------------------------------------------------------------
REM Method 3: curl (Windows 10+)
REM -----------------------------------------------------------------------------
if !download_success! EQU 0 (
    call :PrintInfo "Trying curl download method..."
    curl -L -o "%~2" "%~1" >nul 2>&1
    if !ERRORLEVEL! EQU 0 set "download_success=1"
)

if !download_success! EQU 0 (
    exit /b 1
) else (
    call :PrintSuccess "Download completed successfully"
    exit /b 0
)

REM -----------------------------------------------------------------------------
REM ExtractPortablePython: Extracts portable Python and sets up pip.
REM -----------------------------------------------------------------------------
:ExtractPortablePython
call :PrintInfo "Extracting portable Python..."

REM -----------------------------------------------------------------------------
REM Try PowerShell first
REM -----------------------------------------------------------------------------
powershell -Command "try { Expand-Archive -Path python_portable.zip -DestinationPath python\windows -Force; exit 0 } catch { exit 1 }" >nul 2>&1

if !ERRORLEVEL! NEQ 0 (
    call :PrintInfo "Using alternative extraction method..."
    call :ExtractZip "%CD%\python_portable.zip" "%CD%\python\windows"
    if !ERRORLEVEL! NEQ 0 exit /b 1
)

REM -----------------------------------------------------------------------------
REM Clean up download file
REM -----------------------------------------------------------------------------
del python_portable.zip >nul 2>&1

REM -----------------------------------------------------------------------------
REM Setup pip for portable Python
REM -----------------------------------------------------------------------------
call :PrintInfo "Setting up package manager..."
call :SetupPortablePip
exit /b !ERRORLEVEL!

REM -----------------------------------------------------------------------------
REM SetupPortablePip: Installs pip for portable Python.
REM -----------------------------------------------------------------------------
:SetupPortablePip
:: Download get-pip.py using multiple methods
call :DownloadFile "https://bootstrap.pypa.io/get-pip.py" "python\windows\get-pip.py"
if !ERRORLEVEL! NEQ 0 exit /b 1

:: Install pip
"%CD%\python\windows\python.exe" python\windows\get-pip.py --no-warn-script-location >nul 2>&1
exit /b !ERRORLEVEL!

REM -----------------------------------------------------------------------------
REM RunPythonInstaller: Runs the official Python installer.
REM -----------------------------------------------------------------------------
:RunPythonInstaller
call :PrintInfo "Please complete the installation. Ensure 'Add Python to PATH' is checked."
echo.
call :PrintWarning "The installer will open shortly. This launcher will wait for completion."

REM -----------------------------------------------------------------------------
REM Run installer with user-friendly options
REM -----------------------------------------------------------------------------
start /wait python_installer.exe /passive InstallAllUsers=0 PrependPath=1 Include_test=0 SimpleInstall=1

REM -----------------------------------------------------------------------------
REM Clean up
REM -----------------------------------------------------------------------------
del python_installer.exe >nul 2>&1

REM -----------------------------------------------------------------------------
REM Wait a moment for PATH to update
REM -----------------------------------------------------------------------------
timeout /t 3 >nul 2>&1

exit /b 0

REM -----------------------------------------------------------------------------
REM RefreshEnvironment: Refreshes environment variables after install.
REM -----------------------------------------------------------------------------
:RefreshEnvironment
:: Refresh environment variables
call :PrintInfo "Refreshing environment variables..."
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "SYS_PATH=%%b"
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USER_PATH=%%b"
set "PATH=%SYS_PATH%;%USER_PATH%"
exit /b 0

REM -----------------------------------------------------------------------------
REM ShowManualGuide: Displays manual Python installation instructions.
REM -----------------------------------------------------------------------------
:ShowManualGuide
echo.
call :PrintInfo "Manual Installation Guide:"
echo.
echo %YELLOW%1. Visit: https://www.python.org/downloads/%RESET%
echo %YELLOW%2. Download Python 3.8 or newer%RESET%
echo %YELLOW%3. Run the installer and check 'Add Python to PATH'%RESET%
echo %YELLOW%4. Restart this launcher after installation%RESET%
echo.
pause
exit /b 0

REM -----------------------------------------------------------------------------
REM GetPythonVersion: Retrieves Python version string.
REM -----------------------------------------------------------------------------
:GetPythonVersion
set "python_cmd=%~1"
for /f "tokens=2" %%v in ('"%python_cmd%" --version 2^>^&1') do set "PYTHON_VERSION=%%v"
exit /b 0

REM -----------------------------------------------------------------------------
REM VerifyPythonVersion: Checks if Python version meets minimum requirement.
REM -----------------------------------------------------------------------------
:VerifyPythonVersion
:: Simple version comparison (assumes standard version format)
set "current=%~1"
set "minimum=%~2"

:: Extract major and minor versions
for /f "tokens=1,2 delims=." %%a in ("%current%") do (
    set "curr_major=%%a"
    set "curr_minor=%%b"
)
for /f "tokens=1,2 delims=." %%a in ("%minimum%") do (
    set "min_major=%%a"
    set "min_minor=%%b"
)

if !curr_major! GTR !min_major! exit /b 0
if !curr_major! EQU !min_major! if !curr_minor! GEQ !min_minor! exit /b 0
exit /b 1

REM -----------------------------------------------------------------------------
REM SetupRequirements: Creates requirements.txt if missing.
REM -----------------------------------------------------------------------------
:SetupRequirements
call :PrintInfo "Preparing dependency list..."

if not exist "requirements.txt" (
    call :PrintInfo "Creating requirements.txt..."
    (
        echo # Mudrikam Launcher Dependencies
        echo pyside6^>=6.0.0
        echo pillow^>=9.0.0
        echo qtawesome^>=1.0.0
        echo requests^>=2.25.0
    ) > requirements.txt
)
exit /b 0

REM -----------------------------------------------------------------------------
REM InstallDependencies: Installs Python dependencies with retries.
REM -----------------------------------------------------------------------------
:InstallDependencies
set "python_cmd="%~1""
set "max_retries=3"
set "retry_count=0"

:RETRY_INSTALL
set /a retry_count+=1
call :PrintInfo "Installing dependencies (attempt !retry_count!/!max_retries!)..."

REM -----------------------------------------------------------------------------
REM Upgrade pip first
REM -----------------------------------------------------------------------------
"%python_cmd%" -m pip install --upgrade pip >nul 2>&1

REM -----------------------------------------------------------------------------
REM Install requirements with timeout and retry logic
REM -----------------------------------------------------------------------------
"%python_cmd%" -m pip install -r requirements.txt --upgrade --timeout 60 >nul 2>&1

if !ERRORLEVEL! EQU 0 (
    exit /b 0
) else (
    if !retry_count! LSS !max_retries! (
        call :PrintWarning "Installation failed, retrying in 5 seconds..."
        timeout /t 5 >nul 2>&1
        goto :RETRY_INSTALL
    ) else (
        call :PrintError "Failed to install dependencies after !max_retries! attempts"
        echo.
        call :PrintInfo "Attempting to diagnose the issue..."
        "%python_cmd%" -m pip install -r requirements.txt --upgrade
        exit /b 1
    )
)

REM -----------------------------------------------------------------------------
REM VerifyInstallation: Verifies that all required packages are installed.
REM -----------------------------------------------------------------------------
:VerifyInstallation
set "python_cmd="%~1""
call :PrintInfo "Testing installed packages..."

REM -----------------------------------------------------------------------------
REM Test each critical package
REM -----------------------------------------------------------------------------
set "packages=PySide6 PIL qtawesome"
for %%p in (!packages!) do (
    "%python_cmd%" -c "import %%p; print('%%p OK')" >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        call :PrintWarning "Package %%p verification failed"
        exit /b 1
    )
)

call :PrintSuccess "All packages verified successfully"
exit /b 0

REM -----------------------------------------------------------------------------
REM ExtractZip: Helper to extract ZIP files using VBScript if needed.
REM -----------------------------------------------------------------------------
:ExtractZip
setlocal
set "zipfile=%~1"
set "destination=%~2"

REM -----------------------------------------------------------------------------
REM Using VBScript to extract ZIP file
REM -----------------------------------------------------------------------------
set "vbscript=%temp%\mudrikam_extract_%random%.vbs"
(
    echo Set fso = CreateObject^("Scripting.FileSystemObject"^)
    echo If NOT fso.FolderExists^("%destination%"^) Then
    echo    fso.CreateFolder^("%destination%"^)
    echo End If
    echo Set objShell = CreateObject^("Shell.Application"^)
    echo Set FilesInZip = objShell.NameSpace^("%zipfile%"^).items
    echo objShell.NameSpace^("%destination%"^).CopyHere^(FilesInZip^), 16
    echo WScript.Sleep 2000
) > "%vbscript%"

cscript //nologo "%vbscript%" >nul 2>&1
set "extract_result=!ERRORLEVEL!"
del "%vbscript%" >nul 2>&1
endlocal & exit /b %extract_result%

REM -----------------------------------------------------------------------------
REM END: Final CLI output and exit.
REM -----------------------------------------------------------------------------
:END
echo.
echo %CYAN%=================================================================%RESET%
echo %GREEN%                 Mudrikam Launcher Complete%RESET%
echo %CYAN%=================================================================%RESET%

if exist "%LOGFILE%" (
    echo.
    call :PrintInfo "Log file created: %LOGFILE%"
)

echo.
call :PrintInfo "Thank you for using Mudrikam Launcher v.1.0.0"
echo.
pause
exit /b
echo.
pause
exit /b
