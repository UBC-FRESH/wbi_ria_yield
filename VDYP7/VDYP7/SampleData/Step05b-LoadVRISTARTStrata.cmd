@echo off
REM ========================================================
REM
REM Load VRISTART Strata Adjustments from external 
REM data stores for all polygons not marked as IGNORE.
REM
REM	Use -help to get command line usage.
REM
REM Command line arguments used by this script and can be
REM supplied in any order:
REM
REM	-help
REM     -test   [Show the internal command lines without running]
REM     -params [Param file name]
REM     -load   [LOAD Specification File]
REM             Identifies the LOAD specification file for this process.
REM
REM             If not supplied, defaults to the value: .\LoadVRISTARTStrata.load
REM
REM     -srcdb  [MDB Strata Definitions File]
REM             Identifies the Database file holding the VRISTART Strata.
REM             The organization of the spreadsheet file is fixed.
REM
REM             If not supplied, defaults to the value: .\Strata.mdb
REM
REM     -strata [Table containing Strata Names]
REM             Identifies the table within the database containing
REM             the stata identifiers.
REM
REM             If not supplied, defaults to the table: StrataDefinitions
REM
REM     -adjust [Table with Strata Adjustments]
REM             Identifies the table within the database containing
REM             the adjustment coefficients for each strata parameter.
REM
REM             If not supplied, defaults to the table: StrataVRISTARTAdjustments
REM
REM     -poly   [Table with Polygon/Strata Associations]
REM             Identifies the table within the database containing
REM             the adjustment coefficients for each strata parameter.
REM
REM             If not supplied, defaults to the table: PolygonStrataAssignments
REM
REM     -offset [Table with Polygon specific Parameter Offsets]
REM             Identifies the table within the database containing
REM             the polygon specific offsets for each adjustable PIT parameter.
REM
REM             If not supplied, defaults to the table: VRISTARTParameterOffsets
REM
REM     -destdb [MDB Database File]
REM             Identifies the MDB Database file to reset
REM             the settings and computed values for.
REM
REM             If not supplied, defaults to the value: ..\Combined.mdb
REM
REM     -rpt [Output Report File]
REM             Lists the results of processing along with any
REM             error/warning messages that may have been generated.
REM
REM             If not supplied, defaults to the value: .\ResetVRISTARTStrata.log
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
pushd %~dp0

REM
REM Set default values for relevant command line options.
REM
REM

if "%COMPUTERNAME%" == "VDYP7DEV" ( set V7Binary="..\..\..\DTSRun\Source\DTSRun.exe") else ( set V7Binary="..\ReferenceBinaries\DTSRun\DTSRun.exe")
IF NOT EXIST %V7Binary% SET V7Binary="%~dp0..\..\DTSRun.exe"
IF NOT EXIST %V7Binary% SET V7Binary="%~dp0..\DTSRun.exe"
if NOT EXIST %V7Binary% SET V7Binary="DTSRun.exe"

if EXIST "%~dp0CmdLineArgExtractor.cmd"    set V7ArgExtractor="%~dp0CmdLineArgExtractor.cmd"
if EXIST "%~dp0..\CmdLineArgExtractor.cmd" set V7ArgExtractor="%~dp0..\CmdLineArgExtractor.cmd"
if %V7ArgExtractor%. EQU .                 set V7ArgExtractor="CmdLineArgExtractor.cmd"

set V7LoadFile="%~dp0LoadVRISTARTStrata.load"
set V7StrataNames=StrataDefinitions
set V7Adjustments=StrataVRISTARTAdjustments
set V7PolyAssignment=PolygonStrataAssignments
set V7PolyOffsets=VRISTARTParameterOffsets
set V7SrcDB="%~dp0Strata.mdb"
set V7DestDB="%~dp0Combined.mdb"
IF NOT EXIST %V7DestDB% set V7DestDB="%~dp0..\Combined.mdb"
set V7Report="%~dp0..\LoadVRISTARTStrata.log"
set V7RunMode=-run
set V7TestMode=


REM
REM Process the command line arguments:
REM
REM

CALL %V7ArgExtractor% %~n0 %*
IF %V7Help%. NEQ . GOTO Usage


REM
REM Process for special case command line arguments.
REM
REM

:CommandLoop
if "%1" == "" goto ExitCommandLoop

if /I "%1" == "-strata" (set V7StrataNames=%2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/strata" (set V7StrataNames=%2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-adjst"  (set V7Adjustments=%2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/adjst"  (set V7Adjustments=%2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-poly"   (set V7PolyAssignment=%2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/poly"   (set V7PolyAssignment=%2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-offset" (set V7PolyOffsets=%2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/offset" (set V7PolyOffsets=%2&& shift /1 && goto NextCommandParam)


:NextCommandParam
shift /1
goto CommandLoop

:ExitCommandLoop

set V7


REM
REM Reset VRISTART Strata
REM
REM

echo .
echo Redefining All Strata Definitions...

echo Process Start Time- %DATE% %TIME%

if exist %V7Report% del %V7Report%
%V7TestMode%%V7Binary% -i %V7LoadFile% -srcdbase %V7SrcDB% -e StrataNames=%V7StrataNames% -e StrataAdjustments=%V7Adjustments% -e StrataAssignments=%V7PolyAssignment% -e StrataOffsets=%V7PolyOffsets% -dstdbase %V7DestDB% -rpt %V7Report% %V7RunMode% %V7DebugOpt%

echo Process End Time- %DATE% %TIME%

goto Done


REM
REM Dump Usage Messages
REM
REM

:Usage

echo     -strata [Strata Worksheet]
echo        The worksheet within the spreadheet with Strata Names
echo     -adjst [Adjustment Worksheet]
echo        The worksheet with Strata Adjustments
echo     -poly [Poly/Strata Assignment Worksheet]
echo        The worksheet association polygons with strata
echo     -offset [Poly/Strata Param Offset Worksheet]
echo        The worksheet with polygon specific param offsets

goto Done


REM
REM Clean up our environment variables.
REM
REM

:Done

popd
endlocal
