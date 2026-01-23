@echo off
REM ========================================================
REM
REM Expands VRISTART Strata Parameters into the PIT for all
REM polygons not marked as IGNORE.
REM
REM	Use -help to get command line usage.
REM
REM Command line arguments used by this script and can be
REM supplied in any order:
REM
REM	-help
REM     -test   [Show the internal command lines without running]
REM     -params [Param file name]
REM	-binary [DTSRun executable]
REM     -load [LOAD Specification File]
REM             Identifies the LOAD specification file for this process.
REM
REM             If not supplied, defaults to the value: .\ExpandVRISTARTStrataIntoPIT.load
REM
REM     -destdb [MDB Database File]
REM             Identifies the MDB Database file to reset
REM             the settings and computed values for.
REM
REM             If not supplied, defaults to the value: .\Combined.mdb
REM
REM     -rpt [Output Report File]
REM             Lists the results of processing along with any
REM             error/warning messages that may have been generated.
REM
REM             If not supplied, defaults to the value: .\ExpandVRISTARTStrataIntoPIT.log
REM
REM     -run or -norun or -singlestep
REM             Identifies the processing mode for the DTSRun application.
REM             Only one of these options should be specified.
REM
REM             -run        Batch mode processing with no user interaction.
REM             -norun      Interactive mode.  User must manually start run and 
REM                         exit application.
REM             -singlestep Each individual step is processed then confirmation
REM                         is required from the user.
REM
REM             If not supplied, defaults to the value: -run
REM
REM     -binary [DTSRun.exe file name]
REM             The fully qualified path name of the DTSRun application.
REM
REM             If not supplied, defaults to the value: ..\ReferenceBinaries\DTSRun\DTSRun.exe
REM
REM     -debugfile [Debug File Name]
REM             The name of the debug file to dump diagnostic and other information
REM             into.
REM
REM             if not supplied, defaults to no debug file being generated.
REM
REM

setlocal

REM
REM Set default values for relevant command line options.
REM
REM

if "%COMPUTERNAME%" == "VDYP7DEV" ( set V7Binary="..\..\DTSRun\Source\DTSRun.exe") else ( set V7Binary="..\ReferenceBinaries\DTSRun\DTSRun.exe")
IF NOT EXIST %V7Binary% SET V7Binary="%~dp0..\DTSRun.exe"
if NOT EXIST %V7Binary% SET V7Binary="DTSRun.exe"

if EXIST "%~dp0CmdLineArgExtractor.cmd"    set V7ArgExtractor="%~dp0CmdLineArgExtractor.cmd"
if EXIST "%~dp0..\CmdLineArgExtractor.cmd" set V7ArgExtractor="%~dp0..\CmdLineArgExtractor.cmd"
if %V7ArgExtractor%. EQU .                 set V7ArgExtractor="CmdLineArgExtractor.cmd"

set V7LoadFile="%~dp0ExpandVRISTARTStrataIntoPIT.load"
set V7DestDB="%~dp0Combined.mdb"
set V7Report="%~dp0ExpandVRISTARTStrataIntoPIT.log"
set V7RunMode=-run


REM
REM Process the command line arguments:
REM
REM

CALL %V7ArgExtractor% %~n0 %*
IF %V7Help%. NEQ . GOTO Done
SET V7


REM
REM Expand VRISTART Strata
REM
REM

echo .
echo Expanding All Strata Definitions...

echo Process Start Time- %DATE% %TIME%

if exist %V7Report% del %V7Report%
%V7TestMode%%V7Binary% -i %V7LoadFile% -dstdbase %V7DestDB% -rpt %V7Report% %V7RunMode% %V7DebugOpt%

echo Process End Time- %DATE% %TIME%

goto Done


REM
REM Clean up our environment variables.
REM
REM

:Done

endlocal
