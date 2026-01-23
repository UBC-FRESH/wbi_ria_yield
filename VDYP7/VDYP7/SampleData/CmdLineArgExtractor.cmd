@echo off
REM ==============================================================
REM
REM This script provides generic and common command line argument
REM extraction.
REM
REM By providing these common services, all scripts would contain
REM similar command line processing and therefore also be consistent
REM in their use of command line arguments.
REM
REM This script must be called from a parent script with the command
REM line arguments passed to it via the %* command line arg specifier
REM all prefixed with the name of the script being launched.
REM For example:
REM     call CmdLineArgExtractor Step02-InitalizePIT %*
REM
REM
REM The command line arguments and their corresponding environment
REM variables that they populate.  All command line args are 
REM case insensitive
REM
REM
REM    Cmd Line Arg            Environment Var
REM    ---------------         -------------------------
REM    load                    V7LoadFile
REM    srcdb                   V7SrcDB
REM    destdb                  V7DestDB
REM    origdb                  V7OrigDB
REM    rpt                     V7Report
REM    err                     V7Error
REM    start                   V7Start
REM    end                     V7End
REM    inc                     V7Increment
REM    year                    V7Year
REM    run  norun  singlestep  V7RunMode
REM    binary                  V7Binary
REM    debugfile               V7DebugFile
REM    template                V7Template
REM    test                    V7TestMode
REM    help    ?               V7Help
REM
REM

REM
REM Get the script name calling the command line processor.
REM
REM

SET V7Script=%1
SHIFT /1


REM
REM Loop through command line options
REM
REM

:CommandLoop
REM ECHO Current Argument: %1

if /I %1. == .            goto ExitCommandLoop

if /I "%1" == "-?"          goto Usage
if /I "%1" == "/?"          goto Usage
if /I "%1" == "-help"       goto Usage
if /I "%1" == "/help"       goto Usage

if /I "%1" == "-params"     (call :ProcessParamFile %2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/params"     (call :ProcessParamFile %2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-load"       (set V7LoadFile=%2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/load"       (set V7LoadFile=%2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-srcdb"      (set V7SrcDB=%2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/srcdb"      (set V7SrcDB=%2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-destdb"     (set V7DestDB=%2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/destdb"     (set V7DestDB=%2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-origdb"     (set V7OrigDB=%2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/origdb"     (set V7OrgiDB=%2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-template"   (set V7Template=%2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/template"   (set V7Template=%2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-rpt"        (set V7Report=%2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/rpt"        (set V7Report=%2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-err"        (set V7Error=%2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/err"        (set V7Error=%2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-start"      (set V7Start=%2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/start"      (set V7Start=%2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-end"        (set V7End=%2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/end"        (set V7End=%2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-inc"        (set V7Increment=%2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/inc"        (set V7Increment=%2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-year"       (set V7Year=%2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/year"       (set V7Year=%2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-binary"     (set V7Binary=%2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/binary"     (set V7Binary=%2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-debugfile"  (set V7DebugFile=%2&& set V7DebugOpt=-debugfile %2&& shift /1 && goto NextCommandParam)
if /I "%1" == "/debugfile"  (set V7DebugFile=%2&& set V7DebugOpt=-debugfile %2&& shift /1 && goto NextCommandParam)

if /I "%1" == "-run"        (set V7RunMode=%1&& goto NextCommandParam)
if /I "%1" == "-norun"      (set V7RunMode=%1&& goto NextCommandParam)
if /I "%1" == "-singlestep" (set V7RunMode=%1&& goto NextCommandParam)
if /I "%1" == "/run"        (set V7RunMode=%1&& goto NextCommandParam)
if /I "%1" == "/norun"      (set V7RunMode=%1&& goto NextCommandParam)
if /I "%1" == "/singlestep" (set V7RunMode=%1&& goto NextCommandParam)

if /I "%1" == "-test"       (set V7TestMode=echo && goto NextCommandParam)
if /I "%1" == "/test"       (set V7TestMode=echo && goto NextCommandParam)

:NextCommandParam
shift /1
goto CommandLoop

:ExitCommandLoop
GOTO Done



REM
REM Process command line arguments from a file.
REM Each line of the file may contain one or more command line arguments
REM but individual command line arguments may not be split across lines.
REM
REM The name of the command line argument file is specified
REM as the first argument in the CALL statement.
REM
REM

:ProcessParamFile

REM ECHO Processing Command Line Argument File: %1...
IF     EXIST %1 FOR /F "usebackq eol=; tokens=1*" %%i IN (`type %1`) DO CALL :CommandLoop %%i %%j
IF NOT EXIST %1 (ECHO Parameter File %1 Not Found...&& GOTO Usage)
GOTO Done


REM
REM Display Command Line Usage:
REM
REM

:Usage

SET V7Help=True
echo Usage: %V7Script% [option] [option]...
echo   Where each  case insensitive option can be one of the following:
echo   (Some command line options are not used for all scripts)
echo     -? -h -help
echo        Displays this usage screen.
echo     -params   [parameter file]
echo        Identifies a file containing command line parameters.
echo     -load     [load file]
echo        Identifies the LOAD file associated with this step.
echo     -srcdb    [source db file or file spec]
echo        Identifies the source database(s) to be used.
echo     -destdb   [dest db file]
echo        Identifies the target database.
echo     -origdb   [original db file]
echo        Identifies the original database.
echo     -template [template MDB file]
echo        The name of the template MDB file to be used.
echo     -rpt [report file]
echo        Identifies the output report file.
echo     -err [error dump file]
echo        Identifies the error output file.
echo     -start   -end    -inc
echo        Defines the age range for yield tables.
echo     -run -norun -singlestep
echo        Specifies the processing mode of DTSRun
echo     -binary [DTSRun exe file name]
echo        File name of the DTSRun executable.
echo     -debugfile [Debug File Name]
echo        Name of file for debug information.
echo     -test
echo        Turns on Test Mode echoing the internal command line
echo        but does not execute it.

goto Done




REM
REM All Done processing the command line.
REM
REM

:Done
REM ECHO --------
REM ECHO --------
REM SET V7
REM ECHO --------
REM ECHO --------

GOTO :EOF
