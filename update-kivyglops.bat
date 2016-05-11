set SOURCE_DIR=\\FCAFILES\Resources\Classes\ComputerProgramming\Examples\KivyGlops
REM copy /y "%SOURCE_DIR%\pyglops.py" .
REM copy /y "%SOURCE_DIR%\pyrealtime.py" .
REM copy /y "%SOURCE_DIR%\kivyglops.py" .
REM copy /y "%SOURCE_DIR%\kivyglopsexample.py" .
copy "%SOURCE_DIR%\*.*" .
md sounds
copy "%SOURCE_DIR%\sounds\*.*" .\sounds
md sounds
copy "%SOURCE_DIR%\music\*.*" .\music

md "more credits"
copy "%SOURCE_DIR%\more credits\*.*" ".\more credits"
