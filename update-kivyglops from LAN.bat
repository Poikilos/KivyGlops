set SOURCE_DIR=\\FCAFILES\Resources\Classes\ComputerProgramming\Examples\KivyGlops
set DEST_DIR=%~dp0
REM copy /y "%SOURCE_DIR%\pyglops.py" .
REM copy /y "%SOURCE_DIR%\pyrealtime.py" .
REM copy /y "%SOURCE_DIR%\kivyglops.py" .
REM copy /y "%SOURCE_DIR%\kivyglopsexample.py" .

del "%DEST_DIR%\update-kivyglops (py files only).bat"
del "%DEST_DIR%\update-kivyglops.bat"
del "%DEST_DIR%\update-kivyglops (scripts only).bat"

copy /y "%SOURCE_DIR%\*.*" "%DEST_DIR%\"
copy /y "%SOURCE_DIR%\update-kivyglops from LAN (scripts only).bat" "%DEST_DIR%\"

md "%DEST_DIR%\sounds\"
copy "%SOURCE_DIR%\sounds\*.*" "%DEST_DIR%\sounds\"

REM del "%DEST_DIR%\music"
md "%DEST_DIR%\music\"
copy "%SOURCE_DIR%\music\*.*" "%DEST_DIR%\music\"

md "%DEST_DIR%\meshes\"
copy "%SOURCE_DIR%\meshes\*.*" "%DEST_DIR%\meshes\"

md "%DEST_DIR%\meshes\medseaport"
copy "%SOURCE_DIR%\meshes\medseaport\*.*" "%DEST_DIR%\meshes\medseaport\"

md "%DEST_DIR%\more credits"
copy "%SOURCE_DIR%\more credits\*.*" "%DEST_DIR%\more credits"

md "%DEST_DIR%\maps\"
copy "%SOURCE_DIR%\maps\*.*" "%DEST_DIR%\maps\"

md "%DEST_DIR%\maps\2D"
copy "%SOURCE_DIR%\maps\2D\*.*" "%DEST_DIR%\maps\2D\"

md "%DEST_DIR%\maps\gi"
copy "%SOURCE_DIR%\maps\gi\*.*" "%DEST_DIR%\maps\gi\"

md "%DEST_DIR%\maps\organic"
copy "%SOURCE_DIR%\maps\organic\*.*" "%DEST_DIR%\maps\organic\"

md "%DEST_DIR%\maps\patterns"
copy "%SOURCE_DIR%\maps\patterns\*.*" "%DEST_DIR%\maps\patterns\"

md "%DEST_DIR%\maps\planets"
copy "%SOURCE_DIR%\maps\planets\*.*" "%DEST_DIR%\maps\planets\"

md "%DEST_DIR%\maps\rock"
copy "%SOURCE_DIR%\maps\rock\*.*" "%DEST_DIR%\maps\rock\"

md "%DEST_DIR%\shaders\"
copy "%SOURCE_DIR%\shaders\*.*" "%DEST_DIR%\shaders\"

md "%DEST_DIR%\sprites\"
copy "%SOURCE_DIR%\sprites\*.*" "%DEST_DIR%\sprites\"

IF NOT EXIST "%DEST_DIR%\medseaport1b-minimal.obj" GOTO NOMESH
IF EXIST "%DEST_DIR%\starfield_cylindrical_map.png.png" del "%DEST_DIR%\starfield_cylindrical_map.png.png"
IF EXIST "%DEST_DIR%\starfield_cylindrical_map.png" del "%DEST_DIR%\starfield_cylindrical_map.png"
IF EXIST "%DEST_DIR%\starfield_cylindrical_map.png CREDITS.txt" del "%DEST_DIR%\starfield_cylindrical_map.png CREDITS.txt"

set MESH_SRC_DIR=R:\Meshes\Environments,Outdoor-Manmade\Medieval Kind of Seaport by tokabilitor (CC0)
copy /y "%MESH_SRC_DIR%\medseaport1b-minimal.obj" "%DEST_DIR%\"
copy /y "%MESH_SRC_DIR%\medseaport1b-minimal.mtl" "%DEST_DIR%\"
copy /y "%MESH_SRC_DIR%\medseaport1b-techdemo.obj" "%DEST_DIR%\"
copy /y "%MESH_SRC_DIR%\medseaport1b-techdemo.mtl" "%DEST_DIR%\"
IF EXIST "%DEST_DIR%\Mauerwerk.jpg" copy "%MESH_SRC_DIR%\medseaport-bricks,sandstone-smooth.jpg" "%DEST_DIR%\"
IF EXIST "%DEST_DIR%\Mauerwerk.jpg" copy "%MESH_SRC_DIR%\medseaport-natural_sandstone_wall.jpg" "%DEST_DIR%\"
IF EXIST "%DEST_DIR%\Mauerwerk.jpg" copy "%MESH_SRC_DIR%\medseaport-paving_stones.jpg" "%DEST_DIR%\"
IF EXIST "%DEST_DIR%\Mauerwerk.jpg" copy "%MESH_SRC_DIR%\medseaport-wood-expertmm.jpg" "%DEST_DIR%\"
IF EXIST "%DEST_DIR%\Mauerwerk.jpg" copy "%MESH_SRC_DIR%\medseaport-wood-oak.jpg" "%DEST_DIR%\"
IF EXIST "%DEST_DIR%\Mauerwerk.jpg" copy "%MESH_SRC_DIR%\medseaport-cement.jpg" "%DEST_DIR%\"
IF EXIST "%DEST_DIR%\Mauerwerk.jpg" copy "%MESH_SRC_DIR%\medseaport-roof.jpg" "%DEST_DIR%\"
IF EXIST "%DEST_DIR%\Mauerwerk.jpg" del "%DEST_DIR%\Mauerwerk.jpg"
IF EXIST "%DEST_DIR%\mmauer3.jpg" del "%DEST_DIR%\mmauer3.jpg"
IF EXIST "%DEST_DIR%\Pflastersteine.jpg" del "%DEST_DIR%\Pflastersteine.jpg"
IF EXIST "%DEST_DIR%\Universalholz3.jpg" del "%DEST_DIR%\Universalholz3.jpg"
IF EXIST "%DEST_DIR%\Universalholz4.jpg" del "%DEST_DIR%\Universalholz4.jpg"
IF EXIST "%DEST_DIR%\wand2.jpg" del "%DEST_DIR%\wand2.jpg"
IF EXIST "%DEST_DIR%\ziegeln4.jpg" del "%DEST_DIR%\ziegeln4.jpg"

:NOMESH
