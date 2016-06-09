@echo off
SET DESTDIR_FULLNAME=R:\Classes\ComputerProgramming\Examples\KivyGlops
echo Copying py files...
copy /y "%~dp0\*.py" "%DESTDIR_FULLNAME%\"
IF NOT ["%errorlevel%"]==["0"] GOTO EXIT_ERROR

REM md "%DESTDIR_FULLNAME%\maps"
REM intentionally skip subfolders
REM copy /y "maps\*.*" "%DESTDIR_FULLNAME%\maps\"

REM md "%DESTDIR_FULLNAME%\sounds"
REM copy /y "sounds\*.*" "%DESTDIR_FULLNAME%\sounds\"

REM md "%DESTDIR_FULLNAME%\music"
REM copy /y "music\*.*" "%DESTDIR_FULLNAME%\music\"

REM md "%DESTDIR_FULLNAME%\meshes"
REM copy /y "meshes\*.*" "%DESTDIR_FULLNAME%\meshes\"

REM md "%DESTDIR_FULLNAME%\more credits"
REM copy /y "more credits\*.*" "%DESTDIR_FULLNAME%\more credits\"

REM see also:
echo Copying updater script...
copy /y "%~dp0\etc\update-kivyglops.bat" "%DESTDIR_FULLNAME%\"
echo Copying script updater script...
copy /y "%~dp0\etc\update-kivyglops (scripts only).bat" "%DESTDIR_FULLNAME%\"


IF NOT ["%errorlevel%"]==["0"] GOTO EXIT_ERROR
REM IF EXIST "%DESTDIR_FULLNAME%\deploy.bat" del "%DESTDIR_FULLNAME%\deploy.bat"
del "%DESTDIR_FULLNAME%\update-kivyglops (py files only).bat"
del "%DESTDIR_FULLNAME%\deploy*.bat"
del "%DESTDIR_FULLNAME%\*.bak"
del "%DESTDIR_FULLNAME%\opengl*.py*"
IF EXIST "%DESTDIR_FULLNAME%\.gitattributes" del "%DESTDIR_FULLNAME%\.gitattributes"
IF EXIST "%DESTDIR_FULLNAME%\.gitignore" del "%DESTDIR_FULLNAME%\.gitignore"
IF EXIST "%DESTDIR_FULLNAME%\screenshot01.png" del "%DESTDIR_FULLNAME%\screenshot01.png"
IF EXIST "%DESTDIR_FULLNAME%\__pycache__" rd /s /q "%DESTDIR_FULLNAME%\__pycache__"
IF EXIST "%DESTDIR_FULLNAME%\opengl6.py" del "%DESTDIR_FULLNAME%\opengl6.py"
IF EXIST "%DESTDIR_FULLNAME%\hud.png" del "%DESTDIR_FULLNAME%\hud.png"
del "%DESTDIR_FULLNAME%\*.pyc"
IF EXIST "%DESTDIR_FULLNAME%\kivyglopstesting.py" del "%DESTDIR_FULLNAME%\kivyglopstesting.py"
IF EXIST "%DESTDIR_FULLNAME%\kivyglopsminimal.py" del "%DESTDIR_FULLNAME%\kivyglopsminimal.py"
GOTO EXIT_OK
:EXIT_ERROR
pause
:EXIT_OK
REM explorer "%DESTDIR_FULLNAME%"
