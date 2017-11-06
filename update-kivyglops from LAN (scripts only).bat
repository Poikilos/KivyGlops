set SOURCE_DIR=\\FCAFILES\Resources\Classes\ComputerProgramming\Examples\KivyGlops
set DEST_DIR=%~dp0
REM copy /y "%SOURCE_DIR%\pyglops.py" .
REM copy /y "%SOURCE_DIR%\pyrealtime.py" .
REM copy /y "%SOURCE_DIR%\kivyglops.py" .
REM copy /y "%SOURCE_DIR%\kivyglopsexample.py" .

del "%DEST_DIR%\update-kivyglops (py files only).bat"
del "%DEST_DIR%\update-kivyglops.bat"
del "%DEST_DIR%\update-kivyglops (scripts only).bat"

copy /y "%SOURCE_DIR%\*.py" "%DEST_DIR%\"
copy /y "%SOURCE_DIR%\update-kivyglops from LAN.bat" "%DEST_DIR%\"

REM md "%DEST_DIR%\sounds\"
REM copy "%SOURCE_DIR%\sounds\*.*" "%DEST_DIR%\sounds\"

REM del "%DEST_DIR%\music"
REM md "%DEST_DIR%\music\"
REM copy "%SOURCE_DIR%\music\*.*" "%DEST_DIR%\music\"

REM md "%DEST_DIR%\meshes\"
REM copy "%SOURCE_DIR%\meshes\*.*" "%DEST_DIR%\meshes\"

REM md "%DEST_DIR%\more credits"
REM copy "%SOURCE_DIR%\more credits\*.*" "%DEST_DIR%\more credits"

REM md "%DEST_DIR%\maps\"
REM copy "%SOURCE_DIR%\maps\*.*" "%DEST_DIR%\maps\"
