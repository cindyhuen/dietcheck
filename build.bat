:: This batch file converts the DietCheck Python script into a Windows executable.
@echo off
setlocal

:: Determine if we have Python available. Try 'py' launcher first (most reliable on Windows),
:: then 'python' and 'python3'.
py --version >nul 2>&1
if ERRORLEVEL 1 goto try_python
set PYTHON=py
goto build

:try_python
where /q python
if ERRORLEVEL 1 goto python3
set PYTHON=python
goto build

:python3
where /q python3
if ERRORLEVEL 1 goto nopython
set PYTHON=python3

:: Verify the setup script has been run
:build
set VENV=.venv
set DIST_DIR=dist
set DIETCHECK_DIR=%DIST_DIR%\dietcheck
if exist %VENV% (
	echo Activating virtual environment...
	call %VENV%\Scripts\activate.bat

	:: Ensure dietcheck subfolder exists
	if not exist "%DIETCHECK_DIR%" mkdir "%DIETCHECK_DIR%"

	echo Building DietCheck plugin executable...
	pyinstaller --onefile --name dietcheck-plugin --distpath "%DIETCHECK_DIR%" plugin.py
	if exist manifest.json (
		echo Copying manifest.json...
		copy /y manifest.json "%DIETCHECK_DIR%\manifest.json"
	) else (
		echo Warning: manifest.json not found
	)

	call %VENV%\Scripts\deactivate.bat
	echo.
	echo Build complete! 
	echo Plugin files are ready in: %DIETCHECK_DIR%
	echo.
	echo Next steps:
	echo 1. Copy the entire 'dietcheck' folder from the dist directory
	echo 2. Paste it into: %%PROGRAMDATA%%\NVIDIA Corporation\nvtopps\rise\plugins
	echo.
) else (
	echo Error: Virtual environment not found. Please run setup.bat first.
	exit /b 1
)
goto end

:nopython
echo Error: Python is not installed or not in PATH
echo Please install Python 3.6 or higher and try again
exit /b 1

:end
