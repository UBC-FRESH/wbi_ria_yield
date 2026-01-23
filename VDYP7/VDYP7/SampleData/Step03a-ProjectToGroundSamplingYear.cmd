@echo off
REM ==========================================================
REM
REM Projects all all polygons not marked as 'IGNORE' to the
REM Year of Ground Sampling.
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
REM     -destdb [MDB File to be projected to Year of Ground Sampling]
REM     -rpt    [Report file showing parameters used]
REM     -err    [Error file for error and warning messages]
REM     -year   [The Year of Ground Sampling]
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

set V7DestDB="%~dp0Combined.mdb"
set V7Report="%~dp0ProjectToGroundSamplingYear.out"
set V7Error="%~dp0ProjectToGroundSamplingYear.err"
set V7Year=2003
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
REM Project to Ground Sampling Year
REM
REM

echo Process Start Time- %DATE% %TIME%

if exist %V7Report% del %V7Report%
if exist %V7Error% del %V7Error%

%V7TestMode%%V7Binary% -i %V7DestDB% -o %V7Report% -e %V7Error% -action ProjectGSYr -gsy %V7Year% %V7RunMode% %AddParams%

echo Process End Time- %DATE% %TIME%


REM
REM Clean up our environment variables.
REM
REM

:Done
ENDLOCAL
