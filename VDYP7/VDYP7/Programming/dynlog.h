/*=============================================================================
 *
 *	Module Name....	Dynamic Logging Library Definitions
 *	Filename.......	dynlog\dynlog.h
 *
 *	Copyright......	Source Code (c) 2004 - 2016
 *							Government of British Columbia
 *							All Rights Reserved
 *
 *
 *-----------------------------------------------------------------------------
 *
 *	Contents:
 *	---------
 *
 *	LogENTRY
 * LogEXIT
 * LogPRI
 *	LogFTL
 * LogERR
 * LogWRN
 * LogINF
 * LogTRC
 * LogDBG
 *	LogMsgPriority
 *	LogCntxt
 *	Logger
 *	NULL_LOG_CONTEXT
 *	NULL_LOGGER
 * DynLog_GET_LOGGER
 *	DynLog_SET_LOCAL_CONTEXT
 *
 *	DynLog_Version
 *	DynLog_CreateContext
 *	DynLog_ConfigComplete
 *	DynLog_DestroyContext
 *	DynLog_IsContextEnabled
 *	DynLog_EnableContext
 *	DynLog_GetLogger
 *	DynLog_LoggingPri
 * DynLog_Entry
 *	DynLog_Msg
 *	DynLog_Exit
 *	DynLog_IncrIndent
 *	DynLog_DecrIndent
 *
 *	dynlog_for_version
 * dynlog_for_createcontext_
 * dynlog_for_configcomplete_
 * dynlog_for_destroycontext_
 * dynlog_for_iscontextenabled_
 * dynlog_for_enablecontext_
 * dynlog_for_getlogger_
 * dynlog_for_getrootlogger_
 * dynlog_for_loggingpri_
 * dynlog_for_entry_
 * dynlog_for_exit_
 *	dynlog_for_cmnt_
 * dynlog_for_str_
 * dynlog_for_bool2_
 * dynlog_for_int2_
 * dynlog_for_int4_
 * dynlog_for_r4_
 * dynlog_for_r8_
 * dynlog_for_crnttime_
 * dynlog_for_incrindent_
 * dynlog_for_decrindent_
 *
 * DynLog_VB_Version
 * DynLog_VB_ConfigComplete
 * DynLog_VB_DestroyContext
 * DynLog_VB_IsContextEnabled
 * DynLog_VB_EnableContext
 *
 * DynLog_VB_GetRootLogger
 * DynLog_VB_GetLogger
 * DynLog_VB_LoggingPri
 * DynLog_VB_Entry
 * DynLog_VB_Exit
 * DynLog_VB_Cmnt
 * DynLog_VB_Str
 * DynLog_VB_Bool
 * DynLog_VB_Int
 * DynLog_VB_Long
 * DynLog_VB_Float
 * DynLog_VB_Double
 * DynLog_VB_CrntTime
 * DynLog_VB_IncrIndent
 * DynLog_VB_DecrIndent
 *
 *
 *-----------------------------------------------------------------------------
 *
 *	Notes:
 *	------
 *
 *	Written in ANSI C
 *
 * This library provides a generic and portable interface to logging
 * services written using the 'C' language.
 *
 *
 *=============================================================================
 *
 *	Modification History:
 *	---------------------
 *
 *
 *  Date       |  Details
 * ------------+---------------------------------------------------------------
 *	 yyyy/mm/dd |
 *             |
 *  2004/04/09 |  Initial Implementation
 *             |  (Shawn Brant)
 *             |
 *  2005/02/16 |  Moved the logging services into its own library.
 *             |  (Shawn Brant)
 *             |
 *  2011/12/24 |  Added the routines 'DynLog_Enter' and 'DynLog_Leave' to
 *             |  support the notion of nesting logging blocks.
 *             |  (Shawn Brant)
 *             |
 *  2012/01/05 |  Mantis: 0000044
 *             |  Additional control structures for optional logging of
 *             |  Timestamps and Routine Names.
 *             |  (Shawn Brant)
 *             |
 *  2013/07/25 |  Continuing expansion of log file capabilities by configuring
 *             |  whether Entry to and from Log Blocks are logged and whether
 *             |  or not to indent or leave flat log file input with entry and
 *             |  exit to those blocks.
 *             |  (Shawn Brant)
 *             |
 *  2013/07/26 |  Mantis: 0000052
 *             |  Started adding support for linking this library with FORTRAN
 *             |  routines.
 *             |  (Shawn Brant)
 *             |
 *  2015/06/19 |  Now using ENV_IMPORT macro for routines intended to be
 *             |  imported from a DLL.
 *             |  (Shawn Brant)
 *             |
 *  2016/01/14 |  00115
 *             |  Extensive reorganizations to support Loggers and Appenders
 *             |  within a Log Handle in a move towards a more standardized
 *             |  logging framework.
 *             |  (Shawn Brant)
 *             |
 *  2016/02/19 |  00125
 *             |  Convert message priorities/logging levels to be signed
 *             |  16-bit values rather than unsigned 16-bit values to
 *             |  support languages such as Visual Basic and FORTRAN which
 *             |  do not support the idea of 'unsigned'.
 *             |  (Shawn Brant)
 *             |
 *  2016/02/20 |  00126:
 *             |  Added support for integration with Visual Basic applications.
 *             |  (Shawn Brant)
 *             |
 *  2016/11/16 |  00133
 *             |  Integrated the ability to define and reference environment
 *             |  (substitution) variables when loading the configuration
 *             |  from a configuration file.
 *             |  (Shawn Brant)
 *             |
 *    
 *
 */


#ifndef __DYNLOG_H
#define __DYNLOG_H




/*=============================================================================
 *
 *	File Dependencies:
 *
 */


#ifndef  __ENVIRON_H
#include "environ.h"
#endif


#ifndef  __ENVVARS_H
#include "envvars.h"
#endif



/*=============================================================================
 *
 *	Data and Data Structures
 *
 */

/*-----------------------------------------------------------------------------
 *
 *	LogMsgPriority
 *	==============
 *
 *		Identify the priority for a particular log message.
 *
 *
 *	Members
 *	-------
 *
 *		MSG_PRI_NONE
 *    MSG_PRI_HIGHEST
 *			The highest priority possible message.  No message can be issued with
 *       a higher priority.  Further, if used as a maximum priority filter in
 *       a logger or an appender, all messages will be logged as all messages
 *       must be of equal priority or lower.
 *
 *    MSG_PRI_FATAL
 *    MSG_PRI_ERROR
 *    MSG_PRI_WARN
 *    MSG_PRI_INFO
 *    MSG_PRI_TRACE
 *    MSG_PRI_DEBUG
 *       Provides message priorities for some standard message types.
 *
 *    MSG_PRI_ALL
 *    MSG_PRI_LOWEST
 *       The lowest priority possible message.  No message can be issued with
 *       a lower priority.  Further, if used as a minimum priority filter in
 *       a logger or an appender, all messages will be logged as all messages
 *       must be of equal priority or higher.
 *
 *
 *	Remarks
 *	-------
 *
 *		Log messages are all given a priority when submitted for logging and
 *    fall into the range of logging priorities implied by the LogMsgPriority
 *    data type.
 *
 *    In addition, some typical log priorities are defined.  These message
 *    priorities do not limit you from defining other message priorities.
 *    A message priority is simply a number with some standard priorities
 *    defined.  Any other number in the range of a SWU16 can be used.
 *
 *    The allowed range of message priorities is deliberately chosen:
 *       - Message priorities are all defined to be 5 digit numbers
 *         meaning if they are printed, they have a consistency throughout.
 *       - Numbers always filling a field will sort alphabetically as well
 *         as numerically without having to worry about left or right
 *         justification as well.
 *       - The numbers are all positive so no concerns about the negative sign.
 *       - The range accommodates signed 16-bit integers.  Not all languages
 *         support unsigned integers, this range is consistent with a signed
 *         integer.
 *       - Even with the constrained range, there is still lots of room between
 *         the predefined priorities and the min and max priorities for new
 *         message priorities to be defined.
 *
 */


typedef  SWI16    LogMsgPriority;


#define  MSG_PRI_NONE         ((LogMsgPriority) 32767)
#define  MSG_PRI_HIGHEST      MSG_PRI_NONE

#define  MSG_PRI_FATAL        ((LogMsgPriority) 32500)
#define  MSG_PRI_ERROR        ((LogMsgPriority) 27500)
#define  MSG_PRI_WARN         ((LogMsgPriority) 22500)
#define  MSG_PRI_INFO         ((LogMsgPriority) 17500)
#define  MSG_PRI_TRACE        ((LogMsgPriority) 12500)
#define  MSG_PRI_DEBUG        ((LogMsgPriority) 11000)

#define  MSG_PRI_ALL          ((LogMsgPriority) 10000)
#define  MSG_PRI_LOWEST       MSG_PRI_ALL




/*-----------------------------------------------------------------------------
 *
 *	LogCntxt
 *	========
 *
 *		An overall, self contained logging context.
 *
 *
 *	Remarks
 *	-------
 *
 *		The logging context maintains all definitions, loggers, appenders,
 *    state and configuration data for a single context.
 *
 *    Multiple contexts may exist.
 *
 */


typedef  struct _LogCntxt *    LogCntxt;




/*-----------------------------------------------------------------------------
 *
 *	NULL_LOG_CONTEXT
 *	================
 *
 *		The appropriate value to use to indicate an invalid or uninitialized
 *    logging context handle.
 *
 *
 *	Remarks
 *	-------
 *
 *		All routines which can accept, check for or return a Log Context, will
 *    also check for or return this value to indicate that.
 *
 *    You should compare return values against this constant.
 *
 */


#define     NULL_LOG_CONTEXT   ((LogCntxt) NULL)




/*-----------------------------------------------------------------------------
 *
 *	Logger
 *	======
 *
 *		A logger specific to a named logging block.
 *
 *
 *	Remarks
 *	-------
 *
 *		A logger is defined with a call to 'Dbg_LogEnter' and exists for the
 *    lifetime of the Log Handle.
 *
 *    Subsequent calls to 'Dbg_LogEnter' will return the same logger object.
 *
 */

typedef  struct _Logger *     Logger;




/*-----------------------------------------------------------------------------
 *
 *	NULL_LOGGER
 *	===========
 *
 *		The appropriate value to use to indicate an invalid or uninitialized
 *    logger.
 *
 *
 *	Remarks
 *	-------
 *
 *		All routines which can accept, check for or return a Logger, will
 *    also check for or return this value to indicate that.
 *
 *    You should compare return values against this constant.
 *
 */


#define     NULL_LOGGER   ((Logger) NULL)




/*-----------------------------------------------------------------------------
 *
 *	DynLog_GET_LOGGER
 *	=================
 *
 *		Function macro to retrieve the specified logger if it has not already
 *    bee retrieved.
 *
 *
 *	Members
 *	-------
 *
 *		logrVar
 *			The 'Logger' variable being tested if it is already initialized.
 *
 *    cntxt
 *       The log context to retrieve (or define) the logger variable in.
 *
 *    fullyQualNm
 *       If known, the fully qualified name of the logger desired.
 *
 *    libEXENm
 *       The library or exectuable the logger is defined within.
 *
 *    modNm
 *       The module within the library or executable the logger is defined
 *       within.
 *
 *    funcNm
 *       The function within the module the logger is defined within.
 *
 *    qualNm
 *       Additional qualifying name to append to any supplied names above
 *       for more fine grained (or for a differently defined hierarchy)
 *       in which to define the Logger.
 *    
 *
 *	Remarks
 *	-------
 *
 *		In the typical use paradigm, the 'logrVar' will refer to a 'static Logger'
 *    variable which is initialized to 'NULL_LOGGER'.
 *
 *    On the first run of the routine, the logger referred to will be retrieved
 *    (and possibly created) in the log context and assigned to the logger
 *    variable.
 *
 *    On subsequent runs of the routine, the static variable will have been
 *    previously initialized and this macro will do nothing.
 *
 */


#define  DynLog_GET_LOGGER( logrVar, cntxt, fullyQualNm, libEXENm, modNm, funcNm, qualNm )   \
            ((logrVar != NULL_LOGGER)                                                        \
                  ? logrVar                                                                  \
                  : DynLog_GetLogger( cntxt, fullyQualNm, libEXENm, modNm, funcNm, qualNm ))


                             

/*-----------------------------------------------------------------------------
 *
 *	DynLog_SET_LOCAL_CONTEXT
 *	========================
 *
 *		Boiler plate code to set up the local logging context.
 *
 *
 *	Members
 *	-------
 *
 *    logContext
 *       The logging context in which the local logging context is being
 *       created.  It is against this logging context that the local static
 *       logger is being created.
 *
 *    fullyQualName
 *       If known, the fully qualified name of the logger being searched for.
 *       If supplied, the remaining parameters are ignored.
 *       May be NULL or ""
 *
 *		libEXEName
 *    moduleName
 *    functionName
 *    qualifyingName
 *			Specifies the unique combination of strings identifying the local
 *       logging context.
 *
 *       Each may be NULL or "" if not known.
 *
 *
 *	Remarks
 *	-------
 *
 *		There is no requirement that the identifying strings indicate a unique
 *    identifier.  If the strings equate to another set of strings, then
 *    the same logger will be used in both situations.
 *
 *    This macro creates the following initialized local, static variables:
 *
 *       static   SWChar const * funcName    Function Name for the routine.
 *       static   Logger         logr     The static local logger to log to.
 *       static   SWBool         isFTL    Indicates whether FATAL messages are processed.
 *       static   SWBool         isERR    Indicates whether ERROR messages are processed.
 *       static   SWBool         isWRN    Indicates whether WARN  messages are processed.
 *       static   SWBool         isINF    Indicates whether INFO  messages are processed.
 *       static   SWBool         isTRC    Indicates whether TRACE messages are processed.
 *       static   SWBool         isDBG    Indicates whether DEBUG messages are processed.
 *
 */

#define  DynLog_SET_LOCAL_CONTEXT( logContext,        \
                                   fullyQualName,     \
                                   libEXEName,        \
                                   moduleName,        \
                                   functionName,      \
                                   qualifyingName )   \
static SWChar const *   funcName = functionName;      \
static Logger           logr     = NULL_LOGGER;       \
static SWBool           isFTL    = FALSE;             \
static SWBool           isERR    = FALSE;             \
static SWBool           isWRN    = FALSE;             \
static SWBool           isINF    = FALSE;             \
static SWBool           isTRC    = FALSE;             \
static SWBool           isDBG    = FALSE;             \
if (logr == NULL_LOGGER)                              \
   {                                                  \
   logr  = DynLog_GetLogger( logContext, fullyQualName, libEXEName, moduleName, functionName, qualifyingName ); \
   isFTL = DynLog_LoggingPri( logr, MSG_PRI_FATAL );  \
   isERR = DynLog_LoggingPri( logr, MSG_PRI_ERROR );  \
   isWRN = DynLog_LoggingPri( logr, MSG_PRI_WARN  );  \
   isINF = DynLog_LoggingPri( logr, MSG_PRI_INFO  );  \
   isTRC = DynLog_LoggingPri( logr, MSG_PRI_TRACE );  \
   isDBG = DynLog_LoggingPri( logr, MSG_PRI_DEBUG );  \
   }




/*-----------------------------------------------------------------------------
 *
 *	LogENTRY
 * LogEXIT
 *	========
 *
 *		Simplifies and shortens the request to log entry and exit from a
 *    block of code.
 *
 *
 *	Members
 *	-------
 *
 *		logr
 *			The logger through which you are entering a block of code.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


#define  LogENTRY( logr )     DynLog_Entry( logr, __LINE__ )
#define  LogEXIT(  logr )     DynLog_Exit(  logr, __LINE__ )



/*-----------------------------------------------------------------------------
 *
 * LogPRI
 *	LogFTL
 * LogERR
 * LogWRN
 * LogINF
 * LogTRC
 * LogDBG
 *	======
 *
 *		These macros provide shorthand notation for logging at the various
 *    known message priorities.
 *
 *    These macros are an UGLY HACK!  Read on...
 *
 *
 *	Remarks
 *	-------
 *
 *		To log at custom message priorities, the function DynLog_Msg must
 *    be used.
 *
 *    Generate log requests through 'DynLog_Msg' at the following predefine
 *    message priorities:
 *
 *       MSG_PRI_FATAL
 *       MSG_PRI_ERROR
 *       MSG_PRI_WARN
 *       MSG_PRI_INFO
 *       MSG_PRI_TRACE
 *       MSG_PRI_DEBUG
 *
 *
 *    IMPORTANT:  (Make sure you understand this ugly hack)
 *    ----------
 *
 *    Because the VC 6++ Preprocessor does not support variadic macros, 
 *    a work around has been implemented which requires the creation of
 *    seemingly incorrect C statements.
 *
 *    These macros expand out to a partial statement.  Specifically,
 *    the result DynLog_Msg call looks like:
 *
 *       LogINF( logr, indent )     BECOMES
 *       DynLog_Msg( logr, MSG_PRI_INFO, __LINE__, indent
 *
 *    Suppose you wish to write the following DynLog_Msg call using
 *    these macros:
 *
 *       DynLog_Write( logr, MSG_PRI_INFO, __LINE__, indent, "A msg saying: %s", "something simple" );
 *
 *    You would write a complete and correct log request statement that
 *    looks like:
 *
 *       LogINF( logr, indent ), "A simple msg saying: %s", "something simple" );
 *
 *    If you were to write the statement as you expect you should (with 
 *    variadic macro support):
 *
 *       LogINF( logr, indent, "A simple msg saying: %s", "something simple" );
 *
 *    Visual C 6 will produce the following error messages:
 *       warning C4002: too many actual parameters for macro 'LogINF'
 *       error C2143: syntax error : missing ')' before ';'
 *       error C2198: 'DynLog_Msg' : too few actual parameters
 *
 */


#define  LogPRI( logr, pri, indent )   DynLog_Msg( logr, pri, __LINE__, indent

#define  LogFTL( logr, indent )        LogPRI( logr, MSG_PRI_FATAL, indent )
#define  LogERR( logr, indent )        LogPRI( logr, MSG_PRI_ERROR, indent )
#define  LogWRN( logr, indent )        LogPRI( logr, MSG_PRI_WARN,  indent )
#define  LogINF( logr, indent )        LogPRI( logr, MSG_PRI_INFO,  indent )
#define  LogTRC( logr, indent )        LogPRI( logr, MSG_PRI_TRACE, indent )
#define  LogDBG( logr, indent )        LogPRI( logr, MSG_PRI_DEBUG, indent )




/*-----------------------------------------------------------------------------
 *
 *	Object Name
 *	===========
 *
 *		Brief Description of what this object represents or contains
 *
 *
 *	Members (Optional Heading)
 *	-------
 *
 *		Member1
 *			member description
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


/*=============================================================================
 *
 *	Function Prototypes:
 *
 */


#ifdef __cplusplus
extern "C" {
#endif



/*-----------------------------------------------------------------------------
 *
 *	DynLog_Version
 * DynLog_VB_Version
 * dynlog_for_version
 *	==================
 *
 *		Returns the version number of this library.
 *
 *
 *	Parameters
 *	----------
 *
 *		versionNum
 *       On input, points to a buffer at least 16 bytes in length to
 *       receive the version string.
 *
 *			On output, this buffer will hold the DynLog Library version
 *			as a string.
 *
 *       Must not be NULL.
 *
 *    versionLen
 *       On input (VB only), contains the length of the 'versionNum'
 *       buffer in characters.
 *
 *       On output, contains the length of the string stored in the
 *       'versionNum' buffer.
 *
 *       Must not be NULL.
 *
 *		versionBufrLen
 *			(FORTRAN only) The length of the 'versionNum' buffer.  This 
 *       length should be at a minimum of 16 characters.
 *
 *
 *	Return Value
 *	------------
 *
 *		Returns a string of the format:
 *
 *       "x.yyz.wwww"
 *
 *    Where 'x' is the major version number.
 *          'y' is the minor version number.
 *          'z' is a minor update version letter.
 *          'w' is a strictly increasing build number.
 *
 *
 *	Remarks
 *	-------
 *
 *		Strings are null terminated and may be as long as 16 characters in
 *    length.
 *
 *    Each field above may be longer or shorter than shown above except
 *    for field 'z', which is always a single alphabetic character (a-z).
 *
 *    If the buffer pointed to by 'versionNum' is too short to receive the
 *    version string, a zero length string is stored in the 'versionNum'
 *    buffer and 'versionLen' will be set to 0.
 *
 */


SWChar const *    ENV_IMPORT_STDCALL      DynLog_Version( void );


void              ENV_IMPORT_STDCALL   DynLog_VB_Version( SWChar *    versionNum,
                                                          SWI32 *     versionLen );


void    ENV_IMPORT_STDCALL   dynlog_for_version_( SWChar * versionNum,
                                                  SWI32 *  versionLen,
                                                  SWU32    bufferLen );




/*-----------------------------------------------------------------------------
 *
 *	DynLog_CreateContext
 * DynLog_VB_CreateContext
 * dynlog_for_createcontext_
 *	=========================
 *
 *		Create a brand new, base configured Logging Context.
 *
 *
 *	Parameters
 *	----------
 *
 *    configurationFile
 *       The name of the file to use for Log Context configuration.
 *       If not supplied (NULL) or zero length, a minimal, default 
 *       configuration will be created.
 *
 *    envVariables
 *       Handle to the environment variables to be defined/used by the Dynamic
 *       Logging library while loading the configuration.
 *
 *       May be NULL_ENV_VARS.
 *
 *    configFileNameLen
 *       Identifies the length, in characters, of the string passed in through
 *       the FORTRAN language.
 *
 *
 *	Return Value
 *	------------
 *
 *		A handle to the new Log Context.
 *    NULL_LOG_CONTEXT if the logging context could not be created.
 *
 *
 *	Remarks
 *	-------
 *
 *    It is best to configure the Log Context through the external
 *    configuration rather than relying on the minimal, default configuration
 *    that is created in its absence.  The external configuration file allows
 *    a full state and configuration specification as well as gives hints to
 *    tuning internal data structures.
 *
 *    If using the minimal logging context, the initial state of the log 
 *    context is disabled.
 *
 *    The current state of this global logging switch can be tested with a
 *    call to 'DynLog_IsContextEnabled'.
 *
 *    The current state of this global logging switch can be changed with a
 *    call to 'DynLog_EnableContext'.
 *
 */


LogCntxt  ENV_IMPORT_STDCALL
DynLog_CreateContext( SWChar const *   configFileName,
                      EnvVars          envVariables );


SWI32     ENV_IMPORT_STDCALL
DynLog_VB_CreateContext( SWChar const *   configFileName,
                         SWI32            envVariables );


SWI32     ENV_IMPORT_STDCALL   
dynlog_for_createcontext_( SWChar const *    configFileName,
                           SWI32 *           envVariables,
                           SWU32             configFileNameLen );




/*-----------------------------------------------------------------------------
 *
 *	DynLog_ConfigComplete
 * DynLog_VB_ConfigComplete
 * dynlog_for_configcomplete_
 *	==========================
 *
 *		Mark the loaded logging context as configuration complete.
 *
 *
 *	Parameters
 *	----------
 *
 *    cntxt
 *       The logging context to mark as fully configured.
 *
 *
 *	Remarks
 *	-------
 *
 *    While the configuration file and the basic configuration provides
 *    fully configured logging contexts, they do not provide any ability
 *    for an application to provide custom logging services.
 *
 *    Between the time the logging context is created and the start of the
 *    main application and the logging it would like to do, custom
 *    custom configuration may need to be done at an API level.
 *
 *    Custom configuration is possible between 'DynLog_CreateContext' and
 *    'DynLog_ConfigComplete'.
 *
 *    This routine does any remaining startup steps, notably:
 *       -  Calling the 'Open Routine' for any appenders.
 *
 */


SWVoid   ENV_IMPORT_STDCALL
DynLog_ConfigComplete( LogCntxt   cntxt );


SWVoid   ENV_IMPORT_STDCALL
dynlog_for_configcomplete_( SWI32 *  cntxt );


SWVoid   ENV_IMPORT_STDCALL
DynLog_VB_ConfigComplete( SWI32 cntxt );





/*-----------------------------------------------------------------------------
 *
 *	DynLog_DestroyContext
 * DynLog_VB_DestroyContext
 * dynlog_for_destroycontext_
 *	==========================
 *
 *		Destroy a log context and release all resources held by it.
 *
 *
 *	Parameters
 *	----------
 *
 *		logContext
 *			The log context to be destroyed.
 *
 *
 *	Remarks
 *	-------
 *
 *		All loggers, appenders, configuration items and memory held by this
 *    log context are closed, released and deleted as appropriate.
 *
 */


SWVoid   ENV_IMPORT_STDCALL
DynLog_DestroyContext( LogCntxt  logContext );


SWVoid   ENV_IMPORT_STDCALL
DynLog_VB_DestroyContext( SWI32  logContext );


SWVoid   ENV_IMPORT_STDCALL
dynlog_for_destroycontext_( SWI32 *    logContext );




/*-----------------------------------------------------------------------------
 *
 *	DynLog_IsContextEnabled
 * DynLog_VB_IsContextEnabled
 * dynlog_for_iscontextenabled_
 *	============================
 *
 *		Determines if the supplied log context is currently globally enabled or 
 *    disabled.
 *
 *
 *	Parameters 
 *	----------
 *
 *		cntxt
 *			The Log Context to test if it is globally enabled or disabled.
 *       Must not be NULL_LOG_CONTEXT
 *
 *
 *	Return Value
 *	------------
 *
 *		TRUE     The log context is currently active and all subordinate objects
 *             will operate normally according to their own rules.
 *
 *    FALSE    The log context is inactive and no logging or other activies
 *             are to be performed.  This is the global main breaker.
 *
 *
 *	Remarks
 *	-------
 *
 *		The global logging state switch can be manipulated with a call to the
 *    routine: 'DynLog_EnableContext'.
 *
 */


SWBool   ENV_IMPORT_STDCALL
DynLog_IsContextEnabled( LogCntxt    cntxt );


SWI32    ENV_IMPORT_STDCALL
DynLog_VB_IsContextEnabled( SWI32   contxt );


SWI32    ENV_IMPORT_STDCALL
dynlog_for_iscontextenabled_( SWI32 *  cntxt );




/*-----------------------------------------------------------------------------
 *
 *	DynLog_EnableContext
 * DynLog_VB_EnableContext
 * dynlog_for_enablecontext_
 *	=========================
 *
 *		Enable/Disable the log context.
 *
 *
 *	Parameters
 *	----------
 *
 *		cntxt
 *			The logging context to be enabled or disabled.
 *       Must not be NULL_LOG_CONTEXT.
 *
 *    enable
 *       TRUE     The logging context is active and all logging occurs
 *                according to the rules governing individual logging objects
 *                in the context.
 *
 *       FALSE    All logging activities are stopped.
 *
 *
 *	Remarks
 *	-------
 *
 *		This routine makes a fast way to turn all logging on and off.
 *    The current state of this global logging switch can be determined
 *    with a call to: 'DynLog_IsContextEnabled'.
 *
 */


SWVoid   ENV_IMPORT_STDCALL
DynLog_EnableContext( LogCntxt   cntxt,   SWBool   enable );


SWVoid   ENV_IMPORT_STDCALL
DynLog_VB_EnableContext( SWI32   cntxt, SWI32  enable );


SWVoid   ENV_IMPORT_STDCALL
dynlog_for_enablecontext_( SWI32 *  cntxt,   SWI32 *  enable );




/*-----------------------------------------------------------------------------
 *
 * DynLog_VB_Cmnt
 * DynLog_VB_Str
 * DynLog_VB_Bool
 * DynLog_VB_Int
 * DynLog_VB_Long
 * DynLog_VB_Float
 * DynLog_VB_Double
 * DynLog_VB_CrntTime
 *
 *	dynlog_for_cmnt_
 * dynlog_for_str_
 * dynlog_for_bool2_
 * dynlog_for_int2_
 * dynlog_for_int4_
 * dynlog_for_r4_
 * dynlog_for_r8_
 * dynlog_for_crnttime_
 *	====================
 *
 *		Helper functions to DynLog_Msg for languages that do not easily write
 *    to variable length argument lists (like FORTRAN).
 *
 *
 *	Parameters
 *	----------
 *
 *    logger
 *       The logger to print the message to.
 *
 *    priority
 *       The message priority to associate with the message.
 *       Must be between MSG_PRI_LOWEST and MSG_PRI_HIGHEST.  If outside
 *       that range, the priority will be set to the appropriate limit.
 *
 *    lineNum
 *       The source file line number where the message originated.
 *       If the line number is not known or should be suppressed on a case
 *       by case basis, supply 0.
 *
 *    indent
 *       The number of spaces to indent the diagnostic message (in addition
 *       to the current indent level).
 *
 *    message
 *    messageLen
 *       The specific message/comment to be printed out and the number of
 *       characters in the string.
 *
 *    string
 *    stringLen
 *       The arbitrary string argument to be printed and the number of the
 *       characters in the string.
 *
 *    boolVal
 *       The boolean value to be printed as True/False
 *
 *    intVal
 *       The integer value to be printed.
 *
 *    floatVal
 *       The floating point value to be printed.
 *
 *    numDecimals
 *       The number of decimals to be printed with the value.
 *
 *
 *	Remarks
 *	-------
 *
 *		These routines will help languages (such as FORTRAN) that have troubles
 *    with a variable list of arguments to write to the DynLog library by
 *    translating known arguments into an appropriate DynLog_Msg call.
 *
 */


void  ENV_IMPORT_STDCALL
DynLog_VB_Cmnt( SWI32      logger,
                SWI16      priority,
                SWI32      lineNum,
                SWI32      indent,
                SWChar *   message );




void  ENV_IMPORT_STDCALL
dynlog_for_cmnt_( SWI32 *     logger,
                  SWI32 *     priority,
                  SWI32 *     lineNum,
                  SWI32 *     indent,
                  SWChar *    message,
                  SWU32       messageLen );



void  ENV_IMPORT_STDCALL
DynLog_VB_Str( SWI32      logger,
               SWI16      priority,
               SWI32      lineNum,
               SWI32      indent,
               SWChar *   message,
               SWChar *   string );


void  ENV_IMPORT_STDCALL
dynlog_for_str_( SWI32 *      logger,
                 SWI32 *      priority,
                 SWI32 *      lineNum,
                 SWI32 *      indent,
                 SWChar *     message,
                 SWChar *     string,
                 SWU32        messageLen,
                 SWU32        stringLen );



void  ENV_IMPORT_STDCALL
DynLog_VB_Bool( SWI32      logger,
                SWI16      priority,
                SWI32      lineNum,
                SWI32      indent,
                SWChar *   message,
                SWI32      boolVal );



void  ENV_IMPORT_STDCALL
dynlog_for_bool2_( SWI32 *      logger,
                   SWI32 *      priority,
                   SWI32 *      lineNum,
                   SWI32 *      indent,
                   SWChar *     message,
                   SWI32 *      boolVal,
                   SWU32        messageLen );



void  ENV_IMPORT_STDCALL
DynLog_VB_Int( SWI32      logger,
               SWI16      priority,
               SWI32      lineNum,
               SWI32      indent,
               SWChar *   message,
               SWI16      intVal );



void  ENV_IMPORT_STDCALL
dynlog_for_int2_( SWI32 *      logger,
                  SWI32 *      priority,
                  SWI32 *      lineNum,
                  SWI32 *      indent,
                  SWChar *     message,
                  SWI16 *      intVal,
                  SWU32        messageLen );



void  ENV_IMPORT_STDCALL
DynLog_VB_Long( SWI32      logger,
                SWI16      priority,
                SWI32      lineNum,
                SWI32      indent,
                SWChar *   message,
                SWI32      intVal );



void  ENV_IMPORT_STDCALL
dynlog_for_int4_( SWI32 *      logger,
                  SWI32 *      priority,
                  SWI32 *      lineNum,
                  SWI32 *      indent,
                  SWChar *     message,
                  SWI32 *      intVal,
                  SWU32        messageLen );



void  ENV_IMPORT_STDCALL
DynLog_VB_Float( SWI32      logger,
                 SWI16      priority,
                 SWI32      lineNum,
                 SWI32      indent,
                 SWChar *   message,
                 SWF32      floatVal,
                 SWI16      numDecimals );



void  ENV_IMPORT_STDCALL
dynlog_for_r4_( SWI32 *      logger,
                SWI32 *      priority,
                SWI32 *      lineNum,
                SWI32 *      indent,
                SWChar *     message,
                SWF32 *      floatVal,
                SWI32 *      numDecimals,
                SWU32        messageLen );




void  ENV_IMPORT_STDCALL
DynLog_VB_Double( SWI32      logger,
                  SWI16      priority,
                  SWI32      lineNum,
                  SWI32      indent,
                  SWChar *   message,
                  SWF64      floatVal,
                  SWI16      numDecimals );



void  ENV_IMPORT_STDCALL
dynlog_for_r8_( SWI32 *      logger,
                SWI32 *      priority,
                SWI32 *      lineNum,
                SWI32 *      indent,
                SWChar *     message,
                SWF64 *      floatVal,
                SWI32 *      numDecimals,
                SWU32        messageLen );



void  ENV_IMPORT_STDCALL
DynLog_VB_CrntTime( SWI32      logger,
                    SWI16      priority,
                    SWI32      lineNum,
                    SWI32      indent,
                    SWChar *   message );



void  ENV_IMPORT_STDCALL
dynlog_for_crnttime_( SWI32 *      logger,
                      SWI32 *      priority,
                      SWI32 *      lineNum,
                      SWI32 *      indent,
                      SWChar *     message,
                      SWU32        messageLen );





/*-----------------------------------------------------------------------------
 *
 *	DynLog_Entry
 * DynLog_VB_Entry
 * dynlog_for_entry_
 *	=================
 *
 *		Mark entry into a logger block.
 *
 *
 *	Parameters
 *	----------
 *
 *		logr
 *			The logger for which you are entering a block for.
 *
 *    lineNum
 *       The line number of the source file where the entry is occurring.
 *
 *
 *	Remarks
 *	-------
 *
 *    All 'DynLog_Entry' calls must be matched with a corresponding
 *    'DynLog_Exit' call whether or not entry is actually logged by
 *    the logger or is output through any appenders.
 *
 *		Entry messaging occurs at the MSG_PRI_TRACE priority level.
 *
 */


SWVoid   ENV_IMPORT_STDCALL   DynLog_Entry( Logger    logr,
                                            SWU32     lineNum );



SWVoid   ENV_IMPORT_STDCALL   dynlog_for_entry_( SWI32 *    logr,
                                                 SWI32 *    lineNum );


SWVoid   ENV_IMPORT_STDCALL   DynLog_VB_Entry( SWI32  logr,
                                               SWI32  lineNum );




/*-----------------------------------------------------------------------------
 *
 *	DynLog_Exit
 * DynLog_VB_Exit
 * dynlog_for_exit_
 *	================
 *
 *		Mark exit from a logger block.
 *
 *
 *	Parameters
 *	----------
 *
 *		logr
 *			The logger for which you are entering a block for.
 *
 *    lineNum
 *       The line number of the source file where the entry is occurring.
 *
 *
 *	Remarks
 *	-------
 *
 *    All 'DynLog_Entry' calls must be matched with a corresponding
 *    'DynLog_Exit' call whether or not entry is actually logged by
 *    the logger or is output through any appenders.
 *
 *		Exit messaging occurs at the MSG_PRI_TRACE priority level.
 *
 */


SWVoid   ENV_IMPORT_STDCALL   DynLog_Exit( Logger    logr,
                                           SWU32     lineNum );



SWVoid   ENV_IMPORT_STDCALL   dynlog_for_exit_( SWI32 *     logr,
                                                SWI32 *     lineNum );



SWVoid   ENV_IMPORT_STDCALL   DynLog_VB_Exit( SWI32  logr,
                                              SWI32  lineNum );




/*-----------------------------------------------------------------------------
 *
 *	DynLog_IncrIndent
 * DynLog_VB_IncrIndent
 * dynlog_for_incrindent_
 *	======================
 *
 *		Increment future log messages to the right by one level for each 
 *    appender affected by this logger.
 *
 *
 *	Parameters
 *	----------
 *
 *		logr
 *			The logger through which future messages will indented by one level.
 *
 *
 *	Remarks
 *	-------
 *
 *    All calls to 'DynLog_IncrIndent' must be paired with a corresponding
 *    call to 'DynLog_DecrIndent'.
 *
 *    This routine works through the logger hierarchy, touching each appender
 *    that is associated with each appender along the way in the same way
 *    a log message is propagated through the logger hierarchy.
 *
 *    For each appender encountered, the indent level of that appender is
 *    incremented.
 *
 *    All appenders not encountered on up the logger hierarchy to the root
 *    logger are not affected.
 *
 *    If the logger does not allow propagation of log messages, indenting of
 *    appender output ends at that logger in the same way messages stop at
 *    that logger.
 *
 */


SWVoid   ENV_IMPORT_STDCALL   DynLog_IncrIndent( Logger  logr );


SWVoid   ENV_IMPORT_STDCALL   DynLog_VB_IncrIndent( SWI32   logr );


SWVoid   ENV_IMPORT_STDCALL   dynlog_for_incrindent_( SWI32 *  logr );




/*-----------------------------------------------------------------------------
 *
 *	DynLog_DecrIndent
 * DynLog_VB_DecrIndent
 * dynlog_for_decrindent_
 *	======================
 *
 *		Decrement future log messages to the left by one level.
 *
 *
 *	Parameters
 *	----------
 *
 *		logr
 *			The logger through which future messages will outdented by one level.
 *
 *
 *	Remarks
 *	-------
 *
 *		Setting the indent level is global setting to the Log Context in which
 *    the supplied Logger is operating.  Once the indent level is changed, all
 *    other messages supplied by all other loggers will be affected.
 *
 */


SWVoid   ENV_IMPORT_STDCALL   DynLog_DecrIndent( Logger  logr );


SWVoid   ENV_IMPORT_STDCALL   DynLog_VB_DecrIndent( SWI32 logr );


SWVoid   ENV_IMPORT_STDCALL   dynlog_for_decrindent_( SWI32 *  logr );




/*-----------------------------------------------------------------------------
 *
 *	DynLog_GetLogger
 * DynLog_VB_GetLogger
 * dynlog_for_getlogger_
 *	=====================
 *
 *		Retrieve the requested logger from a logging context.
 *
 *
 * Parameters
 * ----------
 *
 *    context
 *       The log context from which to get the root logger.
 *
 *    fullyQualifiedName
 *       The already known fully qualified name of the logger to be
 *       looked up.  The name is case insensitive so special care need be
 *       taken to verify the name is all lower case or something.
 *
 *       If NULL or "", the logger's fully qualified name will be constructed
 *       from the remaining name components.
 *
 *    libEXEName
 *       The library or executable name to which this logger is created 
 *       within.
 *
 *       If the 'fullyQualifiedName' is supplied, this name component is
 *       recorded in the logger but is not used in the construction of the
 *       fully qualified name.
 *
 *       May be NULL or ""
 *
 *    moduleName
 *       The name of the module within the library or executable project
 *       to which this logger is created.
 *
 *       If the 'fullyQualifiedName' is supplied, this name component is
 *       recorded in the logger but is not used in the construction of the
 *       fully qualified name.
 *
 *       May be NULL or ""
 *
 *    funcName
 *       The name of the function/routine within the library/module
 *       to which this logger is created.
 *
 *       If the 'fullyQualifiedName' is supplied, this name component is
 *       recorded in the logger but is not used in the construction of the
 *       fully qualified name.
 *
 *       May be NULL or ""
 *
 *    qualifyingName
 *       A qualifying name to associate with the logger to be appended
 *       to the libEXEName/moduleName/functionName to make the logger
 *       fully qualified name unique (if required).  The qualifying name
 *       may be composed of additional name separator characters.
 *
 *       If the 'fullyQualifiedName' is supplied, this name component is
 *       recorded in the logger but is not used in the construction of the
 *       fully qualified name.
 *
 *       May be NULL or ""
 *
 *
 *	Return Value
 *	------------
 *
 *		The requested logger for the context.
 *    NULL_LOGGER if the logger could not be found and could
 *    not be created or the supplied context is invalid.
 *
 *
 *	Remarks
 *	-------
 *
 *		If necessary, the logger will be created along with any required
 *    parent loggers that go with it.
 *
 */


Logger   ENV_IMPORT_STDCALL
DynLog_GetLogger( LogCntxt          context,
                  SWChar const *    fullyQualifiedName,
                  SWChar const *    libEXEName,
                  SWChar const *    moduleName,
                  SWChar const *    funcName,
                  SWChar const *    qualifyingName );



SWI32    ENV_IMPORT_STDCALL
DynLog_VB_GetLogger( SWI32          context,
                     SWChar const * fullyQualifiedName,
                     SWChar const * libEXEName,
                     SWChar const * moduleName,
                     SWChar const * funcName,
                     SWChar const * qualifyingName );



SWI32    ENV_IMPORT_STDCALL
dynlog_for_getlogger_( SWI32 *         context,
                       SWChar const *  fullyQualifiedName,
                       SWChar const *  libEXEName,
                       SWChar const *  moduleName,
                       SWChar const *  funcName,
                       SWChar const *  qualifyingName,
                       SWU32           fullyQualifiedNameLen,
                       SWU32           libEXENameLen,
                       SWU32           moduleNameLen,
                       SWU32           funcNameLen,
                       SWU32           qualifyingNameLen );





/*-----------------------------------------------------------------------------
 *
 *	DynLog_GetRootLogger
 * DynLog_VB_GetRootLogger
 * dynlog_for_getrootlogger_
 *	=========================
 *
 *		Retrieve the root logger for a logging context.
 *
 *
 * Parameters
 * ----------
 *
 *    context
 *       The log context from which to get the root logger.
 *
 *
 *	Return Value
 *	------------
 *
 *		The root logger for the context.
 *    NULL_LOGGER if the root logger has not been created (this would be an
 *    error condition) or the supplied log context is NULL_LOG_CONTEXT.
 *
 *
 *	Remarks
 *	-------
 *
 *		Every log context has a root logger which is the default logger to which
 *    all log requests get to.
 *
 */


Logger   ENV_IMPORT_STDCALL
DynLog_GetRootLogger( LogCntxt    context );


SWI32    ENV_IMPORT_STDCALL
DynLog_VB_GetRootLogger( SWI32   context );


SWI32    ENV_IMPORT_STDCALL
dynlog_for_getrootlogger_( SWI32 *     context );




/*-----------------------------------------------------------------------------
 *
 *	DynLog_LoggingPri
 * DynLog_VB_LoggingPri
 * dynlog_for_loggingpri_
 *	======================
 *
 *		Test if the supplied logger will process messages associated with the
 *    named priority.
 *
 *
 *	Parameters
 *	----------
 *
 *		logr
 *			The logger to test if it will process messages of the supplied
 *       priority.
 *
 *       Must not be NULL.
 *
 *    priority
 *       The message priority to test.
 *
 *       If this priority is outside the range of MSG_PRI_LOWEST to 
 *       MSG_PRI_HIGHEST, the priority tested will be the appropriate
 *       limit.
 *
 *
 *	Return Value
 *	------------
 *
 *		TRUE     Messages having the supplied priority will be logged by the
 *             supplied logger.
 *
 *    FALSE    Messages having the supplied priority will be suppressed by
 *             the supplied logger and have no chance at being logged within
 *             the overall log context.
 *
 *
 *	Remarks
 *	-------
 *
 *		Even though this routine will return a 'TRUE' value, there is no 
 *    guarantee a message will actually be logged through an appender for
 *    a couple of reasons:
 *       -  Individual appenders also have message priority filters and it may 
 *          be that while the logger would like to see the message logged, the
 *          appenders to which the message is directed will suppress the 
 *          message.  This routine does not test for this condition.
 *
 *       -  The identified logger may not have any appenders associated with it
 *          and in the course of processing, the message will be passed on to 
 *          the logger's ancestors.  Any of those ancestor loggers may in turn
 *          suppress the message because they do not allow messages of the
 *          identfied priority.  This routine does not test for this condition.
 *
 */


SWBool   ENV_IMPORT_STDCALL
DynLog_LoggingPri( Logger  logr,    LogMsgPriority    priority );


SWI32    ENV_IMPORT_STDCALL
DynLog_VB_LoggingPri( SWI32   logr,  SWI32   priority );


SWI32    ENV_IMPORT_STDCALL
dynlog_for_loggingpri_( SWI32 *    logr,    SWI32 *   priority );




/*-----------------------------------------------------------------------------
 *
 *	DynLog_Msg
 *	==========
 *
 *		Write a single message out to the logger with the specified message
 *    priority.
 *
 *
 *	Parameters
 *	----------
 *
 *		logr
 *			The message logger to write the message to.
 *
 *    pri
 *       The log message priority associated with the log message.
 *
 *       If outside the range of MSG_PRI_LOWEST to MSG_PRI_HIGHEST, the
 *       priority used will be set to the appropriate limit.
 *
 *    lineNum
 *       The line number from the source code indicating the line containing
 *       the code being logged.
 *
 *    furtherIndent
 *       Additional spaces to prepend to the final message to effectively
 *       indent the message.
 *       May be 0.
 *
 *    fmt
 *       The printf style format string for the remaining arguments.
 *       Must not be null.
 *
 *    ...
 *       Arguments to be printed using the 'fmt' string using standard
 *       'printf' formatting rules..
 *
 *
 *	Return Value
 *	------------
 *
 *		The number of characters converted and written to the message context's
 *    internal buffer.
 *
 *    0 if the message did not pass through the logger's message priority
 *    filters.
 *
 *    Negative value indicates an error.
 *
 *
 *	Remarks
 *	-------
 *
 *		If successfully generated, the log message will be passed on to appenders
 *    according to the logging rules.
 *
 *    If the log message does not pass the logger's message priority gate, the
 *    message will die at this logger without being passed on to any appenders
 *    associated with this logger.  If this is the case, the message will also 
 *    not be passed on the parent logger.
 *
 *    The number of characters written into the buffer must not exceed the
 *    message context's maximum message length of MAX_LOG_MSG_LEN (not 
 *    including the null terminating character).
 *
 *    The message will be suppressed if the log context or this logger is
 *    not currently active.
 *
 */


int     ENV_IMPORT_CDECL
DynLog_Msg( Logger            logr,
            LogMsgPriority    pri,
            SWU32             lineNum,
            SWU32             furtherIndent,
            SWChar const *    fmt,
            ... );




/*-----------------------------------------------------------------------------
 *
 *	Function Name
 *	=============
 *
 *		Brief Description of what this function does
 *
 *
 *	Parameters (Optional Heading)
 *	----------
 *
 *		Param1
 *			parameter description
 *
 *
 *	Return Value (Optional Heading)
 *	------------
 *
 *		What the return value is and what it means (if applicable)
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 *
 *	Dependencies (Optional Heading)
 *	------------
 *
 *		Object/Function Name			Module Where Located
 *
 *
 *	Functional Description (Optional Heading)
 *	----------------------
 *
 *		More detailed information about how the function does what it does.
 *
 */


#ifdef __cplusplus
}
#endif



/*=============================================================================
 *
 *	END
 *
 */

#endif

