#if 0
/*=============================================================================
 *
 * Module Name.... Standard Definition Module
 * Filename....... Common\environ_stddefs.h
 *
 * Copyright...... Source Code (c) 2015 - 2016
 *                 Government of British Columbia
 *                 All Rights Reserved
 *
 *
 *-----------------------------------------------------------------------------
 *
 * Contents:
 * ---------
 *
 * Compiler
 * Warnings, Errors and the Environment
 * Operating Systems
 * Source File Languages
 * Build Configuration
 *
 *
 *-----------------------------------------------------------------------------
 *
 * Notes:
 * ------
 *
 *    Written in ANSI C
 *
 *    The intention of this module is to provide as seamless as is possible
 *    platform independent macro definitions across a number of operating
 *    environments.
 *
 *    This header file is generally automatically used when #include'ing
 *    "environ.h" but that include file is platform specific whereas this
 *    include file codes Pre-Processor definitions only.  This allows use of
 *    this file to be used in environments other than 'C' source code
 *    (e.g. Windows Resource Compiler files or FORTRAN source code).
 *
 *    This header file contains code which provides uniform access across
 *    ALL operating environments and computer systems.
 *
 *    This header file provides unique symbol definitions for those operating
 *    environments and computer systems.
 *
 *
 *    Only the following Compilers are currently supported:
 *
 *       Borland/Turbo C++             ENV_BORLAND
 *       Zortech C++                   ENV_ZORTECH
 *       HP CFront                     ENV_CFRONT
 *       FSF DJGPP                     ENV_DJGPP
 *       Microsoft C                   ENV_MICROSOFT
 *       VAX C                         ENV_VAXC
 *       GNU GCC                       ENV_GCC
 *       EMX C++                       ENV_EMX
 *       Sun C                         ENV_SUNC
 *
 *
 *
 *    Within each of the above compilers, we may be targeting one of the
 *    following operating environments:
 *
 *       MS-DOS                        ENV_MSDOS
 *       Microsoft Windows (16-bit)    ENV_MSWINDOWS
 *       Microsoft Windows 95/98/NT    ENV_WIN32
 *       OS/2                          ENV_OS2
 *       UNIX                          ENV_UNIX
 *       X-Windows                     ENV_X11
 *       Motif                         ENV_MOTIF
 *       VAX VMS                       ENV_VAXVMS
 *
 *    Note: 'ENV_MOTIF' is a superset of 'ENV_X11' so both may be defined.
 *
 *
 *    The following symbols will be defined for all environments:
 *
 *       VoidF                   - casts a function pointer to 'void *'
 *       VoidP                   - casts a regular pointer to  'void *'
 *
 *       ENV_EXPORT              - Defines how symbols are to be handled in DLL's
 *                                 and such.
 *
 *       ENV_BITS32              - Indicates the system is a 32 bit system.
 *       ENV_BITS16              - Indicates we are running under a 16 bit
 *                                 system.
 *
 *       ENV_LITTLEENDIAN        - The basic architecture has the least
 *                                 significant byte of a value first.
 *       ENV_BIGENDIAN           - The basic architecture has the most
 *                                 significant byte of a value first.
 *
 *       ENV_VIRTUALMEM          - 0   The system is not running with virtual
 *                                     memory.  Generally indicates MSDOS.
 *                                 1   The system is running with virtual
 *                                     memory.
 *
 *       ENV_PROTOTYPES          - 0   Full ANSI function prototypes are NOT
 *                                     allowed.
 *                                 1   Full ANSI function prototypes are
 *                                     allowed.
 *
 *       ENV_LINKBUG             - If defined, all object files must have
 *                                 executable code in the module linked into
 *                                 the executable.  You can't have a module
 *                                 consisting of only data.
 *
 *
 *       The following constants are defined for the following known
 *       operating systems (note that these symbols are not necessarily mutually
 *       exclusive.  You may have 'ENV_UNIX', 'ENV_X11', and 'ENV_MOTIF'
 *       declared at the same time).
 *
 *          Symbol Name     Value Taken   Description
 *          -----------     -----------   -----------
 *          ENV_OS2              1        OS/2 Version 2.0
 *          ENV_MSWINDOWS        1        Microsoft Windows Version 3.x
 *          ENV_WIN32            1        Win32 Systems (not Win32s)
 *          ENV_MSDOS            1        MS-DOS all versions.
 *          ENV_UNIX             1        HP-UX
 *          ENV_X11              1        X-Windows version 4
 *          ENV_MOTIF            1        Motif version 1.1
 *          ENV_VAXVMS           1        VAX VMS
 *
 *
 *       The following symbols are defined for the following compilation
 *       environments (These are mutually exclusive):
 *
 *          Symbol Name             Description
 *          -----------             -----------
 *          ENV_BORLAND             Borland/Turbo C++
 *          ENV_ZORTECH             Zortech C++
 *          ENV_MICROSOFT           Microsoft C++ 7.0 or higher
 *          ENV_CFRONT              cfront from HP
 *          ENV_DJGPP               DJGPP G++
 *          ENV_GNUC                GNU C
 *          ENV_EMX                 EMX C++
 *          ENV_VAXC                VAX C
 *          ENV_SUNC                Sun OS Sun C
 *
 *
 *       See the specific environments for definitions specific to individual
 *       operating systems.
 *
 *
 *=============================================================================
 *
 *
 * Modification History:
 * ---------------------
 *
 *
 *  Date       |  Details
 * ------------+---------------------------------------------------------------
 *  yyyy/mm/dd |
 *             |
 *  2015/09/18 |  00107: Refactored Preprocessor defines out from 'environ.h'
 *             |  (Shawn Brant)
 *             |
 *  2016/03/02 |  Added a section to determine the target build configuration
 *             |  (DEBUG or RELEASE) based on the compiler being used.
 *             |  (Shawn Brant)
 *             |
 *
 */
#endif

#ifndef __ENVIRON_STDDEFS_H
#define __ENVIRON_STDDEFS_H



#if 0
/*=============================================================================
 *
 * File Dependencies:
 *
 */
#endif


#if 0
/*=============================================================================
 *
 * Data and Data Structures:
 *
 */
#endif


#if 0
/*-----------------------------------------------------------------------------
 *
 * Compiler
 * ========
 *
 *    Determine the Compiler we are working with.
 *
 *
 * Remarks
 * -------
 *
 *    We have definitions for the following compilers:
 *
 *       Borland C++       Version 3.x and above
 *       Zortech C++       Version ??
 *       CFront            Version ??
 *       DJGPP             Version ??
 *       GNU C             Version ??
 *       Microsoft C       Version ??
 *       VAX C             Version ??
 *       Sun C             Version ??
 *
 *    Only one of these definitions may be active for a particular
 *    compilation.  That is, it does not make sense to be compiling with
 *    two different compilers at the same time.
 *
 *    You may specify your particular compiler if you find for some reason
 *    these Pre-Processor statements are not correctly determining the
 *    compiler.
 *
 */
#endif


#if 0
/*
 * Determine the Compiler we are working with.
 *
 * Borland Compiler.
 *
 */
#endif

#ifdef  __BORLANDC__

#  define ENV_BORLAND         1
#  define ENV_COMPILER        Borland
#  define ENV_COMPILER_VER    -100


#else
#  ifdef  __TURBOC__

#     define ENV_BORLAND      1
#     define ENV_COMPILER     Borland
#     define ENV_COMPILER_VER -100

#  endif
#endif




#if 0
/*
 * Zortech Compiler
 *
 */
#endif

#ifdef  __ZTC
#  define ENV_ZORTECH         1
#  define ENV_COMPILER        Zortech
#  define ENV_COMPILER_VER    -100


#endif



#if 0
/*
 * CFront Compiler
 *
 */
#endif

#ifdef  __hpux
#  define ENV_CFRONT          1
#  define ENV_COMPILER        CFront
#  define ENV_COMPILER_VER    -100

#endif




#if 0
/*
 * DJGPP Compiler
 *
 */
#endif

#ifdef  __MSDOS__
#  ifdef  i386
#     define ENV_DJGPP        1
#     define ENV_COMPILER     DJGPP
#     define ENV_COMPILER_VER -100

#  endif
#endif




#if 0
/*
 * Microsoft Compiler
 *
 */
#endif

#ifdef   _MSC_VER
#  define ENV_MICROSOFT       1
#  define ENV_COMPILER        Microsoft C
#  define ENV_COMPILER_VER    _MSC_VER

#endif



#if 0
/*
 * Compaq Visual FORTRAN Compiler
 *
 */
#endif

#ifdef   _DF_VERSION_
#  define ENV_COMPAQ_DF       1
#  define ENV_COMPILER        CompaqDF
#  define ENV_COMPILER_VER    _DF_VERSION_

#endif



#if 0
/*
 * VAX C Compiler.
 *
 */
#endif

#ifdef  VAXC
#  define ENV_VAXC            1
#  define ENV_COMPILER        VaxC
#  define ENV_COMPILER_VER    -100

#endif



#if 0
/*
 * OS/2 EMX Compiler
 *
 */
#endif

#ifdef  __EMX__
#  define ENV_EMX             1
#  define ENV_COMPILER        EMX
#  define ENV_COMPILER_VER    -100

#endif




#if 0
/*
 * GNU GCC Compiler
 *
 */
#endif

#ifdef __GNUC__
#  define  ENV_GCC            1
#  define  ENV_COMPILER       GCC
#  define  ENV_COMPILER_VER   -100

#endif



#if 0
/*
 * AIX xlC Compiler (RS/6000)
 *
 */
#endif

#ifdef AIXV3
#  define  ENV_xlC            1
#  define  ENV_COMPILER       xlC
#  define  ENV_COMPILER_VER   -100

#endif




#if 0
/*
 * SunOS Sun C Compiler (RS/6000)
 *
 */
#endif

#ifdef sun
#  define  ENV_SUNC           1
#  define  ENV_COMPILER       SunC
#  define  ENV_COMPILER_VER   -100

#endif




#if 0
/*
 * Test if we got a valid compiler defined.
 * This testing doesn't seem to work under VAX-C
 *
 */
#endif

#if !ENV_VAXC
#  if    !ENV_BORLAND      &&       \
         !ENV_ZORTECH      &&       \
         !ENV_CFRONT       &&       \
         !ENV_DJGPP        &&       \
         !ENV_MICROSOFT    &&       \
         !ENV_COMPAQ_DF    &&       \
         !ENV_VAXC         &&       \
         !ENV_EMX          &&       \
         !ENV_GCC          &&       \
         !ENV_xlC          &&       \
         !ENV_OS2          &&       \
         !ENV_SUNC


      No Compiler Environment was Determined.

#  else
#     if (ENV_BORLAND   + ENV_ZORTECH + ENV_CFRONT + ENV_DJGPP + ENV_xlC +    \
          ENV_SUNC + ENV_MICROSOFT + ENV_COMPAQ_DF + ENV_VAXC  + ENV_EMX  +   \
          ENV_GCC) > 1

         More than one Compiler Environment was Determined.

#     endif
#  endif
#endif




#if 0
/*-----------------------------------------------------------------------------
 *
 * Operating Systems
 * =================
 *
 *    Determine the operating system we are operating under.
 *
 *
 * Remarks
 * -------
 *
 *    The operating system is gotten from each of the compilers.  Because
 *    each compiler defines contants unique to that system, we have to
 *    get the compiler before we can get the operating system.
 *
 *    The following constants will be defined to 1 depending on the
 *    situation:
 *
 *          ENV_OS2
 *          ENV_MSWINDOWS
 *          ENV_WIN32
 *          ENV_MSDOS
 *          ENV_UNIX
 *          ENV_X11
 *          ENV_MOTIF
 *          ENV_VAXVMS
 *
 *
 *    One of the following definitions will also be defined to 1:
 *
 *          ENV_BITS32
 *          ENV_BITS16
 *
 *    These indicate whether we are running under a 32-bit operating
 *    system or a 16-bit operating system.
 *
 *
 *    We define the following constants for each environment:
 *
 *       _Cdecl            - affects calling and naming conventions
 *                           for 'C' objects.
 *       _CType            - affects calling and naming conventions
 *                           for 'C' and 'Pascal' objects.
 *
 *
 *    We define the macro 'ENV_VIRTUALMEM' to be defined with:
 *
 *       1                 The system runs with virtual memory (essentially
 *                         unlimited memory).  May indicate other compensations
 *                         to make for the system.
 *
 *       0                 The system is not running with virtual memory.
 *                         This means that the only memory available to you is
 *                         what is available through the stack and through
 *                         the heap.
 *
 *
 *    Finally, one of the following constants will also be defined to 1:
 *
 *       ENV_LITTLEENDIAN
 *       ENV_BIGENDIAN
 *
 *       Little Endian machines place bytes in memory so that the least
 *       significant byte is stored at the lower memory address followed
 *       by the next significant byte etc.  80x86 processors are
 *       little endian.
 *
 *       Big Endian machines place bytes in memory so that the most
 *       significant byte is stored at the lower memory address followed
 *       by the next less significant byte etc.  68000 series processors
 *       are big endian.
 *
 *
 *    If 'ENV_LINKBUG' gets defined to 1, then the linker associated with that
 *    compiler has problems linking modules which contain no executable code,
 *    only data.  Therefore, if 'ENV_LINKBUG' is defined to 1, you should
 *    create a dummy routine which does absolutely nothing in the 'data'
 *    module and call that module from some other function which will
 *    DEFINITELY be linked in (assuming the data needs to be linked in).
 *
 *    The last thing this section does is define standard function names
 *    to the non-standard name used by each compiler in each of the
 *    different environments it can be used in (see Zortech MS-DOS).
 *
 */
#endif


#if 0
/*
 * Borland First
 *
 */
#endif

#if ENV_BORLAND
   /*
    * Are we running Borland OS/2?
    *
    */

#  ifdef __OS2__
      Error, Borland OS/2 is defined!!

#     define ENV_OS2                   1
#     define ENV_OS                    OS2
#     define ENV_BITS32                1
#     define ENV_ARCH                  686
#     define ENV_LITTLEENDIAN          1
#     define ENV_VIRTUALMEM            1
#     define ENV_PROTOTYPES            1

#     ifdef __DLL__
#        define   ENV_DLL              1

#     endif


#  if 0
   /*
    * Are we running Microsoft Windows 3.x
    *
    */
#  endif

#  else
#     ifdef _Windows
#        define ENV_MSWINDOWS          1
#        define ENV_OS                 Win16
#        define ENV_BITS16             1
#        define ENV_ARCH               x86
#        define ENV_LITTLEENDIAN       1
#        define ENV_VIRTUALMEM         1
#        define ENV_PROTOTYPES         1

#        ifdef __DLL__
#           define   ENV_DLL           1

#        endif



#     else
#        if 0
         /*
          * Define the operating constants for MS-DOS
          *
          */
#        endif

#        define ENV_MSDOS              1
#        define ENV_OS                 MSDOS
#        define ENV_BITS16             1
#        define ENV_ARCH               x86
#        define ENV_LITTLEENDIAN       1
#        define ENV_VIRTUALMEM         0
#        define ENV_PROTOTYPES         1

#     endif
#  endif
#endif



#if 0
/*
 * Now Microsoft C and derivatives
 *
 */
#endif

#if   ENV_MICROSOFT || ENV_COMPAQ_DF
#  if 0
   /*
    * Are we running Microsoft Windows 3.x
    *
    */
#  endif

#  ifdef _WIN32
#     define ENV_WIN32                 1
#     define ENV_OS                    Win32
#     define ENV_BITS32                1
#     define ENV_ARCH                  686
#     define ENV_LITTLEENDIAN          1
#     define ENV_VIRTUALMEM            1
#     define ENV_PROTOTYPES            1

#  else
#     ifdef _Windows
#        define ENV_MSWINDOWS          1
#        define ENV_OS                 Win16
#        define ENV_ARCH               x86
#        define ENV_BITS16             1
#        define ENV_LITTLEENDIAN       1
#        define ENV_VIRTUALMEM         1
#        define ENV_PROTOTYPES         1

#        ifdef _DLL
#           define   ENV_DLL           1

#        endif

#     else
#        if 0
        /*
         *  Define the operating constants for MS-DOS
         *
         */
#        endif

#        define ENV_MSDOS              1
#        define ENV_OS                 MSDOS
#        define ENV_BITS16             1
#        define ENV_ARCH               x86
#        define ENV_LITTLEENDIAN       1
#        define ENV_VIRTUALMEM         0
#        define ENV_PROTOTYPES         1


#     endif
#  endif
#endif



#if 0
/*
 * Now Zortech
 *
 */
#endif


#if   ENV_ZORTECH

   Zortech Compiler Environment defined!!


#endif



#if 0
/*
 * Now CFront
 *
 */
#endif

#if   ENV_CFRONT

   CFront Compiler Environment defined!!


#endif



#if 0
/*
 * Now DJGPP
 *
 */
#endif

#if   ENV_DJGPP

   DJGPP Compiler Environment defined!!


#endif



#if 0
/*
 * Running on a VAX
 *
 */
#endif

#if   ENV_VAXC

#  define ENV_VAXVMS                1
#  define ENV_OS                    VaxVMS
#  define ENV_BITS32                1
#  define ENV_ARCH                  Unknown
#  define ENV_BIGENDIAN             1
#  define ENV_VIRTUALMEM            1
#  define ENV_PROTOTYPES            1


#endif




#if 0
/*
 * Running EMX on OS/2
 *
 */
#endif

#if   ENV_EMX

#  define ENV_OS2                   1
#  define ENV_OS                    OS2
#  define ENV_BITS32                1
#  define ENV_ARCH                  686
#  define ENV_LITTLEENDIAN          1
#  define ENV_VIRTUALMEM            1
#  define ENV_PROTOTYPES            1


#endif




#if 0
/*
 * Running GCC on UNIX
 *
 */
#endif

#if   ENV_GCC

#  ifdef    __WIN32
#     define ENV_WIN32                 1
#     define ENV_OS                    Win32
#     define ENV_BITS32                1
#     define ENV_ARCH                  686
#     define ENV_LITTLEENDIAN          1
#     define ENV_VIRTUALMEM            1
#     define ENV_PROTOTYPES            1

#  else
#     define ENV_UNIX                  1
#     define ENV_OS                    UNIX
#     define ENV_BITS32                1
#     define ENV_ARCH                  686
#     define ENV_LITTLEENDIAN          1
#     define ENV_VIRTUALMEM            1
#     define ENV_PROTOTYPES            1

#  endif
#endif



#if 0
/*
 * Running xlC on AIX
 *
 */
#endif

#if   ENV_xlC

#  define ENV_UNIX                  1
#  define ENV_OS                    UNIX
#  define ENV_BITS32                1
#  define ENV_ARCH                  Unknown
#  define ENV_BIGENDIAN             1     /* ??? should be 0 ??? */
#  define ENV_VIRTUALMEM            1
#  define ENV_PROTOTYPES            1


#endif


#if 0
/*
 * Running Sun C on SunOS UNIX
 *
 */
#endif

#if   ENV_SUNC

#  define ENV_UNIX                  1
#  define ENV_OS                    UNIX
#  define ENV_BITS32                1
#  define ENV_ARCH                  Unknown
#  define ENV_BIGENDIAN             1     /* ??? should be 0 ??? */
#  define ENV_VIRTUALMEM            1
#  define ENV_PROTOTYPES            1


#endif




#if 0
/*
 * Check that at least one operating system was defined.
 *
 */
#endif

#if !ENV_OS2 && !ENV_MSWINDOWS && !ENV_WIN32 && !ENV_MSDOS && !ENV_VAXVMS && !ENV_UNIX

   No Operating System was defined!!



#else
#  if ENV_OS2 + ENV_MSWINDOWS + ENV_WIN32 + ENV_MSDOS + ENV_VAXVMS + ENV_UNIX > 1
      More than one operating system defined!!

#  endif
#endif






#if 0
/*-----------------------------------------------------------------------------
 *
 * Warnings, Errors and the Environment
 * ====================================
 *
 *    Activate all possible warnings and error messages.
 *    Set certain aspects of the environment.
 *
 *
 * Remarks
 * -------
 *
 *    Each compiler may have a different set of warning and error messages
 *    that may be activated or suppressed, so these are not equivalent
 *    environment settings across all compilation environments
 *
 *    Further, it may not even be possible to change the warning/error
 *    settings from source code.
 *
 */
#endif

#if   ENV_BORLAND

#   if 0
   /*
    * ANSI Violations:
    *
    */
#   endif

#if   0
#  pragma warn +bbf     /* Bit fields must be 'Int' or 'UInt'.                */
#  pragma warn +big     /* Hex value contains more than three digits.         */
#  pragma warn +dpu     /* Declare 'type' prior to use in prototype.          */
#  pragma warn +dup     /* Redefinition of 'macro' is not identical.          */
#  pragma warn +eas     /* Assigning 'type' to 'enumeration'.                 */
#  pragma warn +ext     /* 'Identifier' is declared 'external' and 'static'.  */
#  pragma warn +pin     /* Initialization is partially bracketed.             */
#  pragma warn +ret     /* Both 'return' and 'return with value' used.        */
#  pragma warn +stu     /* Undefined structure 'structure'.                   */
#  pragma warn +sus     /* Suspicious pointer conversion.                     */
#  pragma warn +voi     /* Void functions may not return a value.             */
#  pragma warn +zdi     /* Division by zero.                                  */



#   if 0
   /*
    * Frequent Errors:
    *
    */
#   endif

#  pragma warn +amb     /* Ambiguous operators need parentheses.              */
#  pragma warn +amp     /* Superfluous '&' with function or array.            */
#  pragma warn +asm     /* Unknown assembler instruction.                     */
#  pragma warn +aus     /* 'Identifier' is assigned a value but not used.     */
#  pragma warn +ccc     /* Condition is always true/false.                    */
#  pragma warn +def     /* Possible use of 'identifier' before definition.    */
#  pragma warn +eff     /* Code has no effect.                                */
#  pragma warn +ias     /* Array variable 'identifier' is near.               */
#  pragma warn +ill     /* Ill-formed pragma.                                 */
#  pragma warn +nod     /* No declaration for function 'function'.            */
#  pragma warn +par     /* Parameter 'parameter' is never used.               */
#  pragma warn +pia     /* Possibly incorrect assignment.                     */
#  pragma warn +pro     /* Call to function with no prototype.                */
#  pragma warn +rch     /* Unreachable code.                                  */
#  pragma warn +rvl     /* Function should return a value.                    */
#  pragma warn +stv     /* Structure passed by value.                         */
#  pragma warn +use     /* 'Identifier' declared but never used.              */



#   if 0
   /*
    * Portablility Warnings:
    *
    */
#   endif

#  pragma warn +cin     /* Constant is long.                                  */
#  pragma warn +cpt     /* Nonportable pointer comparison.                    */
#  pragma warn +rng     /* Constant out of range in comparison.               */
#  pragma warn +sig     /* Conversion may lose significant digits.            */
#  pragma warn +ucp     /* Mixing pointers to 'Char' and 'UChar'.             */



#   if 0
   /*
    * C++ Warnings:
    *
    */
#   endif

#  pragma warn +bei     /* Initializing enumeration with 'type'.              */
#  pragma warn +dsz     /* Array size for 'delete' ignored.                   */
#  pragma warn +hid     /* 'Function1' hides virtual 'function2'.             */
#  pragma warn +ibc     /* 'Base1' is inaccessible because also in 'Base2'.   */
#  pragma warn +inl     /* Functions containing 'identifier' not inline.      */
#  pragma warn +lin     /* Temporary used to initialize identifier.           */
#  pragma warn +lvc     /* Temporary used for parameter in call to 'func'.    */
#  pragma warn +mpc     /* Convert to 'type' will fail for members.           */
#  pragma warn +mpd     /* Max precisionused for member pointer type 'type'.  */
#  pragma warn +ncf     /* Non-const 'function' called const object.          */
#  pragma warn +nci     /* Constant member 'identifier' is not initialized.   */
#  pragma warn +nst     /* Use qualified name to access nested type 'type'.   */
#  pragma warn +nvf     /* Non-volatile function called for volatile object.  */
#  pragma warn +obi     /* Base initialization without class name obsolete.   */
#  pragma warn +ofp     /* Style of function definition is now obsolete.      */
#  pragma warn +ovl     /* Overload is now unnecessary and obsolete.          */
#  pragma warn +pre     /* Prefix '++'/'--' used as a postfix operator.       */

#endif


#   if 0
   /*
    * Make sure 'enum's are the same size as 'int's (word size)
    *
    */
#   endif

#  pragma option -b



#   if 0
   /*
    * Set up for ANSI if that's what we're compiling for,
    *
    */
#   endif

#  ifdef __STDC__
#     define  __cdecl

#  endif


#endif



#if   ENV_ZORTECH

#endif



#if   ENV_CFRONT

#endif



#if   ENV_DJGPP

#endif



#if   ENV_MICROSOFT

#endif



#if   ENV_VAXC

#endif



#if   ENV_EMX

#endif


#if   ENV_GCC

#endif





#if 0
/*-----------------------------------------------------------------------------
 *
 * Source File Languages
 * =====================
 *
 *    This section attempts to determine the source development language
 *    based on macro definitions.
 *
 *
 * Parameters
 * ----------
 *
 *    ENV_CPLUSPLUS
 *       If defined, the compiler is compiling a C++ source file.
 *
 *    ENV_C
 *       If defined, the compiler is compiling a C source file.
 *
 *    ENV_FORTRAN
 *       If defined, the compiler is compiling a FORTRAN source file.
 *
 *    ENV_OTHER_LANG
 *       If defined, culd not determine the language of the source file.
 *
 * Remarks (Optional Heading)
 * -------
 *
 *    Remarks, warnings, special conditions to be aware of, etc.
 *
 *
 * Functional Description (Optional Heading)
 * ----------------------
 *
 *    More detailed information about how the function does what it does.
 *
 */
#endif

#if   defined(__cplusplus)
#define  ENV_CPLUSPLUS  1

#endif

#if (!defined(ENV_CPLUSPLUS)) && (defined(__LANGUAGE_FORTRAN__) || defined(_LANGUAGE_FORTRAN))
#define  ENV_FORTRAN    1

#endif

#if (!defined(ENV_CPLUSPLUS)) && (!defined(ENV_FORTRAN)) && defined(__STDC__)
#define  ENV_C          1

#endif

#if (!defined(ENV_CPLUSPLUS)) && (!defined(ENV_FORTRAN)) && (!defined(ENV_C))
#define  ENV_LANG_OTHER 1

#endif



#if 0
/*-----------------------------------------------------------------------------
 *
 * Build Configuration
 * ===================
 *
 *    Determine the Build Configuration for the current compilation.
 *
 *
 * Remarks
 * -------
 *
 *    Typically, this will be one of 'DEBUG' or 'RELEASE'
 *
 *    For compilers where it is not obvious what the target build 
 *    configuration, assume 'DEBUG'.
 *
 */
#endif

#if 0
ENV_BORLAND
ENV_ZORTECH
ENV_CFRONT
ENV_DJGPP
ENV_MICROSOFT
ENV_COMPAQ_DF
ENV_VAXC
ENV_EMX
ENV_GCC
ENV_xlC
ENV_SUNC
#endif

#if !defined(ENV_MICROSOFT)
#error Not Microsoft compiler.
#endif

#if defined(ENV_MICROSOFT)
#  if    defined(_DEBUG)
#     define   ENV_BUILD_DEBUG   1

#  else
#     define   ENV_BUILD_RELEASE 1

#  endif

#elif defined(ENV_COMPAQ_DF)
#  if    defined(_DEBUG)
#     define   ENV_BUILD_DEBUG   1

#  else
#     define   ENV_BUILD_RELEASE 1

#  endif


#else
#  define   ENV_BUILD_DEBUG   1

#endif



#if   defined(ENV_BUILD_DEBUG)
#  define   ENV_BUILD_CONFIG  DEBUG

#elif defined(ENV_BUILD_RELEASE)
#  define   ENV_BUILD_CONFIG  RELEASE

#else
#  define   ENV_BUILD_DEBUG   1
#  define   ENV_BUILD_CONFIG  DEBUG

#endif



#if 0
/*-----------------------------------------------------------------------------
 *
 * Function Name
 * =============
 *
 *    Brief Description of what this function does
 *
 *
 * Parameters (Optional Heading)
 * ----------
 *
 *    Param1
 *       parameter description
 *
 *
 * Return Value (Optional Heading)
 * ------------
 *
 *    What the return value is and what it means (if applicable)
 *
 *
 * Remarks (Optional Heading)
 * -------
 *
 *    Remarks, warnings, special conditions to be aware of, etc.
 *
 *
 * Functional Description (Optional Heading)
 * ----------------------
 *
 *    More detailed information about how the function does what it does.
 *
 */
#endif

#if 0
/*=============================================================================
 *
 * END
 *
 */
#endif

#endif

