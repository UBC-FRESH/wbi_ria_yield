@echo off
REM ========================================================
REM
REM Redefine all Initialize the PIT for the Adjusted 
REM Projection process.
REM
REM	Use -help to get commmand line usage.
REM
REM Command line arguments used by this script and can be
REM supplied in any order:
REM
REM	-help
REM     -test   [Show the internal command lines without running]
REM     -params [Param file name]
REM     -binary [DTSRun executable]
REM     -load   [DTSRun LOAD sepcification file]
REM     -destdb [Combined MDB file to be initialized]
REM     -rpt    [Report file containing the results of initialization]
REM     -run  -norun  -singlestep
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

if "%COMPUTERNAME%" == "VDYP7DEV" ( set V7Binary="..\..\DTSRun\Source\DTSRun.exe") else ( set V7Binary="..\ReferenceBinaries\DTSRun\DTSRun.exe")
IF NOT EXIST %V7Binary% SET V7Binary="%~dp0..\DTSRun.exe"
if NOT EXIST %V7Binary% SET V7Binary="DTSRun.exe"

if EXIST "%~dp0CmdLineArgExtractor.cmd"    set V7ArgExtractor="%~dp0CmdLineArgExtractor.cmd"
if EXIST "%~dp0..\CmdLineArgExtractor.cmd" set V7ArgExtractor="%~dp0..\CmdLineArgExtractor.cmd"
if %V7ArgExtractor%. EQU .                 set V7ArgExtractor="CmdLineArgExtractor.cmd"

set V7LoadFile="%~dp0InitializePIT.load"
set V7DestDB="%~dp0Combined.MDB"
set V7Report="%~dp0InitializePIT.log"
set V7RunMode=-run


REM
REM Process the command line arguments:
REM
REM

CALL %V7ArgExtractor% %~n0 %*
IF %V7Help%. NEQ . GOTO Done
SET V7


REM
REM Process the Combined Format MDB file.
REM
REM

echo .
echo Loading Initial PIT Values...

echo Process Start Time- %DATE% %TIME%

%V7TestMode%if exist %V7Report% del %V7Report%
%V7TestMode%%V7Binary% -i %V7LoadFile% -dstdbase %V7DestDB% -rpt %V7Report% %V7RunMode%

echo Process End Time- %DATE% %TIME%

goto Done


REM
REM Clean up our environment variables.
REM
REM

:Done
ENDLOCAL
