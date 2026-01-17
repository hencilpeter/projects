@echo off
set PROJECT_ROOT=C:\Users\User\Documents\GitHub\PythonProjects\marania_invoice_venv
set BUILD_ROOT=C:\TempDeployment\build
set SCRIPT_ROOT=C:\Users\User\Documents\GitHub\PythonProjects\build_additional_scripts
set APP_ROOT=%PROJECT_ROOT%\marania_invoice_proj

echo Cleaning old build...
rmdir /S /Q %BUILD_ROOT% 2>nul

echo Creating build folders...
mkdir %BUILD_ROOT%\app
mkdir %BUILD_ROOT%\scripts

echo Copying Django project...
xcopy %APP_ROOT% %BUILD_ROOT%\app /E /I /H /Y

echo Removing unnecessary files...
REM rmdir /S /Q %BUILD_ROOT%\app\staticfiles 2>nul
for /d /r "%BUILD_ROOT%\app" %%d in (__pycache__) do rmdir /s /q "%%d" 2>nul

echo Creating requirements.txt...
%PROJECT_ROOT%\Scripts\pip.exe freeze > %BUILD_ROOT%\app\requirements.txt

echo Copying the scripts...
copy %SCRIPT_ROOT%\mac_app_deploy.sh  %BUILD_ROOT%\
copy %SCRIPT_ROOT%\mac_start_marania.sh		 %BUILD_ROOT%\
copy %SCRIPT_ROOT%\windows_app_deploy.bat		 %BUILD_ROOT%\
copy %SCRIPT_ROOT%\windows_start_marania.bat		 %BUILD_ROOT%\

echo Build completed at:
echo %BUILD_ROOT%
pause