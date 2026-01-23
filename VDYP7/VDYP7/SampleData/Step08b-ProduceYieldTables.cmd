@echo off
REM ==========================================================
REM
REM Produces a yield table over the age range specified
REM based on the adjustments made in the PIT for all polygons
REM not marked as 'IGNORE'.
REM
REM	Use -help to get command line usage.
REM
REM Command line arguments used by this script and can be
REM supplied in any order:
REM
REM	-help
REM     -test   [Show the internal command lines without running]
REM     -params [Param file name]
REM	-binary [VDYP7Batch executable]
REM     -srcdb  [Source MDB File to be projected into yield tables]
REM     -rpt    [Report file containing the yield tables]
REM     -start  [Start Age for yeild tables]
REM     -end    [End Age for yield tables]
REM     -inc    [Age increment for yield tables]
REM     -err    [Error file to report warning and error messages to]
REM     -run  -norun
REM
REM All command line arguments will default to a value that
REM may or may not be applicable to your environment.  Use
REM the -test command line argument to test the default
REM arguments against what you expect.     
REM
REM

SETLOCAL

REM
REM Set Default Values...
REM
REM

if "%COMPUTERNAME%" == "VDYP7DEV" ( set V7Binary="..\Source\VDYP7Batch.exe") else ( set V7Binary="..\ReferenceBinaries\VDYP7Batch.exe")
IF NOT EXIST %V7Binary% SET V7Binary="%~dp0..\VDYP7Batch.exe"
if NOT EXIST %V7Binary% SET V7Binary="VDYP7Batch.exe"

if EXIST "%~dp0CmdLineArgExtractor.cmd"    set V7ArgExtractor="%~dp0CmdLineArgExtractor.cmd"
if EXIST "%~dp0..\CmdLineArgExtractor.cmd" set V7ArgExtractor="%~dp0..\CmdLineArgExtractor.cmd"
if %V7ArgExtractor%. EQU .                 set V7ArgExtractor="CmdLineArgExtractor.cmd"

set V7SrcDB="%~dp0Combined.mdb"
set V7Report="%~dp0ProduceYieldTables.out"
set V7Error="%~dp0ProduceYieldTables.err"
set V7Start=50
set V7End=300
set V7Increment=25
set V7RunMode=-run
set AddParams=


REM
REM Process the command line arguments:
REM
REM

CALL %V7ArgExtractor% %~n0 %*
IF %V7Help%. NEQ . GOTO Done
SET V7


REM
REM Produce the Yield Tables
REM
REM

echo Process Start Time- %DATE% %TIME%

if exist %V7Report% del %V7Report%
if exist %V7Error%  del %V7Error%

%V7TestMode%%V7Binary% -i %V7SrcDB% -o %V7Report% -e %V7Error% -action ProduceAdjustedYieldTable -start %V7Start% -end %V7End% -inc %V7Increment% %V7RunMode% %AddParams%

echo Process End Time- %DATE% %TIME%


REM
REM Clean up our environment variables.
REM
REM

:Done
ENDLOCAL
