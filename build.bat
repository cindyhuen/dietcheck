:: This batch file converts the DietCheck Python script into a Windows executable.
@echo off
setlocal

:: Determine if we have 'python' or 'python3' in the path. On Windows, the
:: Python executable is typically called 'python', so check that first.
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
	call %VENV%\Scripts\activate.bat

	:: Ensure dietcheck subfolder exists
	if not exist "%DIETCHECK_DIR%" mkdir "%DIETCHECK_DIR%"

	pyinstaller --onefile --name dietcheck-plugin --distpath "%DIETCHECK_DIR%" plugin.py
	if exist manifest.json (
		copy /y manifest.json "%DIETCHECK_DIR%\manifest.json"
		echo manifest.json copied successfully.
	) else (
		echo {} > manifest.json
		echo Created a blank manifest.json file.	
		copy /y manifest.json "%DIETCHECK_DIR%\manifest.json"
		echo manifest.json copied successfully.
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
	exit /b 0
) else (
	echo Please run setup.bat before attempting to build
	exit /b 1
)

:nopython
echo Python needs to be installed and in your path
exit /b 1
