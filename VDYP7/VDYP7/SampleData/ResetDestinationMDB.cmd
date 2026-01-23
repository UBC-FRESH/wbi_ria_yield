@echo off
REM ========================================================
REM
REM Overwrite Destination with Template Database.
REM
REM     -template	The template MDB File Spec
REM     -destdb         The destination MDB File Spec
REM     -rpt            Progress Report File Name
REM
REM

SETLOCAL

REM
REM Set up the command line options.
REM
REM

if EXIST "%~dp0CmdLineArgExtractor.cmd"    set V7ArgExtractor="%~dp0CmdLineArgExtractor.cmd"
if EXIST "%~dp0..\CmdLineArgExtractor.cmd" set V7ArgExtractor="%~dp0CmdLineArgExtractor.cmd"

CALL %V7ArgExtractor% %~n0 %*

IF %V7Template%. == . SET V7Template="%~dp0\Template\Template.MDB"
IF %V7DestDB%.   == . SET V7DestDB="%~dp0\Combined.MDB"
IF %V7Report%.   == . SET V7Report="%~dp0\Progress.Log"


REM
REM Perform the Copy...
REM
REM

IF EXIST %V7DestDB% DEL %V7DestDB%
COPY /V /B %V7Template% %V7DestDB%
IF EXIST %V7Report% DEL %V7Report%


REM
REM All Done.
REM
REM

ENDLOCAL
REM ECHO Done ResetDestinationMDB