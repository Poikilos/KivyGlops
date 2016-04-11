@echo off
SET DESTDIR_FULLNAME=R:\Classes\ComputerProgramming\Examples\KivyGlops
copy /y *.* "%DESTDIR_FULLNAME%\"
IF NOT ["%errorlevel%"]==["0"] GOTO EXIT_ERROR
md "%DESTDIR_FULLNAME%\maps"
copy /y maps\*.* "%DESTDIR_FULLNAME%\maps\"
IF NOT ["%errorlevel%"]==["0"] GOTO EXIT_ERROR
REM IF EXIST "%DESTDIR_FULLNAME%\deploy.bat" del "%DESTDIR_FULLNAME%\deploy.bat"
del "%DESTDIR_FULLNAME%\deploy*.bat"
IF EXIST "%DESTDIR_FULLNAME%\.gitattributes" del "%DESTDIR_FULLNAME%\.gitattributes"
IF EXIST "%DESTDIR_FULLNAME%\.gitignore" del "%DESTDIR_FULLNAME%\.gitignore"
IF EXIST "%DESTDIR_FULLNAME%\screenshot01.png" del "%DESTDIR_FULLNAME%\screenshot01.png"
IF EXIST "%DESTDIR_FULLNAME%\__pycache__" rd /s /q "%DESTDIR_FULLNAME%\__pycache__"
IF EXIST "%DESTDIR_FULLNAME%\opengl6.py" del "%DESTDIR_FULLNAME%\opengl6.py"
del "%DESTDIR_FULLNAME%\*.pyc"
IF EXIST "%DESTDIR_FULLNAME%\kivyglopstesting.py" del "%DESTDIR_FULLNAME%\kivyglopstesting.py"
IF EXIST "%DESTDIR_FULLNAME%\kivyglopsminimal.py" del "%DESTDIR_FULLNAME%\kivyglopsminimal.py"
GOTO EXIT_OK
:EXIT_ERROR
pause
:EXIT_OK
