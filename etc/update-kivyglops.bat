set SOURCE_DIR=\\FCAFILES\Resources\Classes\ComputerProgramming\Examples\KivyGlops
set DEST_DIR=%~dp0
REM copy /y "%SOURCE_DIR%\pyglops.py" .
REM copy /y "%SOURCE_DIR%\pyrealtime.py" .
REM copy /y "%SOURCE_DIR%\kivyglops.py" .
REM copy /y "%SOURCE_DIR%\kivyglopsexample.py" .
copy "%SOURCE_DIR%\*.*" "%DEST_DIR%\"

md "%DEST_DIR%\sounds\"
copy "%SOURCE_DIR%\sounds\*.*" "%DEST_DIR%\sounds\"

md "%DEST_DIR%\music\"
copy "%SOURCE_DIR%\music\*.*" "%DEST_DIR%\music\"

md "%DEST_DIR%\meshes\"
copy "%SOURCE_DIR%\meshes\*.*" "%DEST_DIR%\meshes\"

md "%DEST_DIR%\more credits"
copy "%SOURCE_DIR%\more credits\*.*" "%DEST_DIR%\more credits"
