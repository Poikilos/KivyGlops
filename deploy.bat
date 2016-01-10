SET DESTDIR_FULLNAME=R:\Classes\ComputerProgramming\Examples\KivyMesher
copy /y *.* "%DESTDIR_FULLNAME%\"
del "%DESTDIR_FULLNAME%\deploy.bat"
del "%DESTDIR_FULLNAME%\.gitattributes"
del "%DESTDIR_FULLNAME%\.gitignore"
del "%DESTDIR_FULLNAME%\screenshot01.png"
rd /s /q "%DESTDIR_FULLNAME%\__pycache__"
del "%DESTDIR_FULLNAME%\opengl6.py"
