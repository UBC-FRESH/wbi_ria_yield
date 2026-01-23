@echo off
REM ========================================================
REM
REM Convert a PGDB MDB File into the Template MDB Structure
REM
REM	Use the -help to get command line usage.
REM
REM Command line arguments used by this script and can be
REM supplied in any order:
REM
REM	-help
REM     -test   [Show the internal command lines without running]
REM     -params [Param file name]
REM	-binary [DTSRun executable]
REM     -load   [DTSRun LOAD specification file]
REM     -srcdb  [Source PGDB MDB File to be converted]
REM     -destdb [Destination MDB file to be converted into]
REM     -rpt    [Report file containing the results of combining]
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
if EXIST "%~dp0..\CmdLineArgExtractor.cmd" set V7ArgExtractor="%~dp0..\CmdLineArgExtractor.cmd
"if %V7ArgExtractor%. EQU .                set V7ArgExtractor="CmdLineArgExtractor.cmd"

set V7LoadFile="%~dp0PGDB2Template.load"
set V7SrcDB="%~dp0OriginalData\PGDB\PGDBSample.mdb"
set V7Template="%~dp0Template\Template.MDB"
set V7DestDB="%~dp0Combined.MDB"
set V7Report="%~dp0PGDB2Template.log"
set V7RunMode=-run
set CopyTemplateFile="%~dp0ResetDestinationMDB.cmd"


REM
REM Process the command line arguments:
REM
REM

CALL %V7ArgExtractor% %~n0 %*
IF %V7Help%. NEQ . GOTO Done
SET V7


REM
REM Check that the template file exists and copy it to the
REM output file.
REM
REM

ECHO Checking Template Existance...
if exist %V7Template% goto CopyTemplate
echo .
echo . Could not locate template file: %V7Template%
echo .
echo .
goto Done

:CopyTemplate
ECHO Copying Template...
%V7TestMode%call %CopyTemplateFile% -template %V7Template% -destdb %V7DestDB% -rpt %V7Report%




REM
REM Combine Each Input File
REM
REM

echo .
echo Combining Specified Map Sheets in the Parameter file...

echo Process Start Time- %DATE% %TIME%

%V7TestMode%%V7Binary% -i %V7LoadFile% -srcdbase %V7SrcDB% -dstdbase %V7DestDB% -rpt %V7Report% %V7RunMode%

echo Process End Time- %DATE% %TIME%

goto Done


REM
REM Clean up our environment variables.
REM
REM

:Done
ENDLOCAL
