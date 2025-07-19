:: This batch file setups a users environment to build an executable from a
:: Python script.
@echo off
setlocal

:: Determine if we have Python available. Try 'py' launcher first (most reliable on Windows),
:: then 'python' and 'python3'.
py --version >nul 2>&1
if ERRORLEVEL 1 goto try_python
set PYTHON=py
goto setup

:try_python
python --version >nul 2>&1
if ERRORLEVEL 1 goto python3
set PYTHON=python
goto setup

:python3
python3 --version >nul 2>&1
if ERRORLEVEL 1 goto nopython
set PYTHON=python3

:: Setup the virtual environment if it does not already exist.
:setup
echo Setting up virtual environment...
set VENV=.venv
if not exist %VENV% (
	echo Creating virtual environment with %PYTHON%...
	%PYTHON% -m venv %VENV%
	if ERRORLEVEL 1 goto python_error
)

:: Install the required packages
echo Installing required packages...
call %VENV%\Scripts\activate.bat
if ERRORLEVEL 1 goto venv_error
%PYTHON% -m pip install -r requirements.txt
if ERRORLEVEL 1 goto pip_error
call %VENV%\Scripts\deactivate.bat

echo Setup complete
endlocal
exit /b 0

:nopython
echo.
echo ERROR: Python is not installed or not accessible from command line
echo.
echo Please install Python 3.6 or higher from:
echo https://www.python.org/downloads/
echo.
echo Make sure to check "Add Python to PATH" during installation
echo.
exit /b 1

:python_error
echo.
echo ERROR: Failed to create virtual environment
echo Make sure Python is properly installed and accessible
echo.
exit /b 1

:venv_error
echo.
echo ERROR: Failed to activate virtual environment
echo.
exit /b 1

:pip_error
echo.
echo ERROR: Failed to install required packages
echo Check your internet connection and try again
echo.
exit /b 1

:nopython
echo Python needs to be installed and in your path
exit /b 1
