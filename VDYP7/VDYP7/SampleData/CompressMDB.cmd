@echo off
REM ========================================================
REM
REM Reset VRISTART and VRIADJST Strata Adjustments and 
REM results coming from these phases for all polygons not
REM marked as IGNORE.
REM
REM	Use -help to get command line usage.
REM
REM Command line arguments used by this script and can be
REM supplied in any order:
REM
REM	-help
REM     -test   [Show the internal command lines without running]
REM	-srcdb  [MDB Database File]
REM             Identifies the MDB Database file to be compressed.
REM
REM		If not suppled, defaults to the value: .\Combined.mdb
REM
REM	-destdb [MDB Database File]
REM             Identifies the destination of the compressed MDB 
REM		Database file.
REM
REM		If not suppled, the source database is compressed in place.
REM
REM     -binary [JETCOMP.exe file name]
REM             The fully qualified path name of the JETCOMP application.
REM
REM             If not supplied, defaults to the value: ..\ReferenceBinaries\JETCOMP\JETCOMP.exe
REM
REM

SETLOCAL

REM
REM Set default values for relevant command line options.
REM
REM

if "%COMPUTERNAME%" == "VDYP7DEV" ( set V7Binary="..\Source\ReferenceBinaries\JETCOMP\JETCOMP.exe") else ( set V7Binary="..\ReferenceBinaries\JETCOMP\JETCOMP.exe")
if NOT EXIST %V7Binary% SET V7Binary="%~dp0..\JETCOMP.exe"
if NOT EXIST %V7Binary% SET V7Binary="JETCOMP.exe"

if EXIST "%~dp0CmdLineArgExtractor.cmd"    set V7ArgExtractor="%~dp0CmdLineArgExtractor.cmd"
if EXIST "%~dp0..\CmdLineArgExtractor.cmd" set V7ArgExtractor="%~dp0..\CmdLineArgExtractor.cmd"
if %V7ArgExtractor%. EQU .                 set V7ArgExtractor="CmdLineArgExtractor.cmd"

set V7SrcDB="%~dp0Combined.mdb"


REM
REM Process the command line arguments:
REM
REM

CALL %V7ArgExtractor% %~n0 %*
IF %V7Help%.   NEQ . GOTO Done
IF %TestMode%. NEQ . SET V7SkipInPlace=Yes
SET V7


REM
REM Ensure the source MDB file is around.
REM
REM

IF NOT EXIST %V7SrcDB% ECHO Error: MDB file %V7SrcDB% not found.
IF NOT EXIST %V7SrcDB% GOTO Done

IF %V7DestDB%. NEQ . SET V7SkipInPlace=Yes
IF %V7DestDB%. EQU . FOR %%L IN (%V7SrcDB%) DO SET V7DestDB="%%~dpL~TEMP~%%~nxL"


REM
REM Compress the MDB File
REM
REM

echo .
echo Compressing the MDB File: %V7SrcDB%...

echo Process Start Time- %DATE% %TIME%

%V7TestMode%%V7Binary% -src:%V7SrcDB% -dest:%V7DestDB%
IF /I %V7SkipInPlace%. EQU Yes. GOTO SkipRemaining


IF ERRORLEVEL 1 ( ECHO %V7Binary% reported an error level of %ERRORLEVEL%. Aborting...&& GOTO Done)
IF ERRORLEVEL 0 GOTO Continue
ECHO %V7Binary% reported an error level of %ERRORLEVEL%. Aborting...
GOTO Done

:Continue

REM
REM Succeeded in compressing the file.  Now replace the original.
REM
REM

ECHO Replacing source MDB with Compressed version...
IF EXIST %V7SrcDB%  DEL  %V7SrcDB%
IF EXIST %V7DestDB% COPY /V %V7DestDB% %V7SrcDB%
IF EXIST %V7DestDB% DEL  %V7DestDB%


:SkipRemaining
echo Process End Time- %DATE% %TIME%

goto Done


REM
REM Clean up our environment variables.
REM
REM

:Done
endlocal
