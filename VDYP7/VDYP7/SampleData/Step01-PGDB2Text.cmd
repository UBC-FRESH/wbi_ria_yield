@echo off
REM ========================================================
REM
REM Convert a PGDB Access MDB into Text Format
REM
REM Command line parameters are (in no particular order):
REM
REM     -load [LOAD Specification File]
REM             Identifies the LOAD specification file for this process.
REM
REM             If not supplied, defaults to the value: .\PGDB2Text.load
REM
REM     -srcdb [Source MDB File]
REM             Identifies the PGDB source database.
REM
REM             If not supplied, defaults to the value: .\PGDB.mdb
REM
REM     -destdb [Destination Text Folder]
REM             Identifies the folder to place the text version of
REM             the PGDB database.
REM
REM             If not supplied, defaults to the value: .\PGDBText
REM
REM     -rpt [Output Report File]
REM             Lists the results of processing along with any
REM             error/warning messages that may have been generated.
REM
REM             If not supplied, defaults to the value: .\PGDB2Text.log
REM
REM     -schema [Schema INI File]
REM             The Text Database Schema file.
REM
REM             If not supplied, defaults to the value: .\PGDB2Text.ini
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

REM
REM Set default values for relevant command line options.
REM
REM

setlocal

if "%COMPUTERNAME%" == "VDYP7DEV" ( set V7Binary="..\..\DTSRun\Source\DTSRun.exe") else ( set V7Binary="..\ReferenceBinaries\DTSRun\DTSRun.exe")
IF NOT EXIST %V7Binary% SET V7Binary="%~dp0..\DTSRun.exe"
if NOT EXIST %V7Binary% SET V7Binary="DTSRun.exe"

if EXIST "%~dp0CmdLineArgExtractor.cmd"    set V7ArgExtractor="%~dp0CmdLineArgExtractor.cmd"
if EXIST "%~dp0..\CmdLineArgExtractor.cmd" set V7ArgExtractor="%~dp0..\CmdLineArgExtractor.cmd"
if %V7ArgExtractor%. EQU .                 set V7ArgExtractor="CmdLineArgExtractor.cmd"

set V7LoadFile="%~dp0PGDB2Text.load"
set V7Schema="%~dp0schema.ini"
set V7SrcDB="%~dp0PGDBAdjusted.mdb"
set V7DestDB="%~dp0PGDBText"
set V7Report="%~dp0PGDB2Text.log"
set V7RunMode=-run


REM
REM Process the command line arguments:
REM
REM

CALL %V7ArgExtractor% %~n0 %*
IF %V7Help%. NEQ . GOTO Done
SET V7




REM
REM Check the destination.
REM
REM

IF NOT EXIST %V7SrcDB%         ( ECHO Source PGDB Database does not exist. && GOTO Usage)
IF NOT EXIST %V7Schema%        ( ECHO The PGDB Text Schema file does not exist. && GOTO Usage)
IF NOT EXIST %V7DestDB%\*      ( ECHO Destination Folder does not exist. && GOTO Usage)
IF NOT EXIST %V7LoadFile%      ( ECHO Translation Configuration File does not exist. && GOTO Usage)
IF NOT EXIST %V7Binary%        ( ECHO Translation Program could not be found. && GOTO Usage)


REM
REM Convert the MDB File
REM
REM

echo .
echo Translating PGDB Database...

copy %V7Schema% %V7DestDB%\schema.ini
if exist %V7Report% del %V7Report%

%V7TestMode%%V7Binary% -i %V7LoadFile% -srcdbase %V7SrcDB% -dstdbase %V7DestDB% -rpt %V7Report% %V7RunMode% %V7DebugOpt%

rem if exist %V7DestDB%\schema.ini del %V7DestDB%\schema.ini
goto Done


REM
REM Dump Usage Messages
REM
REM

:Usage

echo Usage: %0 [option] [option]...
echo   Where each option can be one of the following:
echo     -? -h -help
echo        Displays this usage screen.
echo     -load [load file]
echo        Identifies the LOAD file associated with this
echo        DTSRun execution
echo     -srcdb [PGB MDB file]
echo        The source PGDB MDB file to converted.
echo     -schema [Text Schema file]
echo        File describing the format of the text files.
echo     -destdb [dest text folder]
echo        Identifies the target folder to place the PGDB text files.
echo     -rpt [report file]
echo        Identifies the output report file.
echo     -run -norun -singlestep
echo        Specifies the processing mode of DTSRun
echo     -binary [DTSRun exe file name]
echo        File name of the DTSRun executable.
echo     -debugfile [Debug File Name]
echo        Name of file for debug information.

goto Done


REM
REM Clean up our environment variables.
REM
REM

:Done

endlocal
