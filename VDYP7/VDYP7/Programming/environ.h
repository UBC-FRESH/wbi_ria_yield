#if 0
/*=============================================================================
 *
 * Module Name.... Standard Definition Module
 * Filename....... Common\environ.h
 *
 * Copyright...... Source Code (c) 1992 - 2016
 *                 Government of British Columbia
 *                 All Rights Reserved
 *
 *
 *-----------------------------------------------------------------------------
 *
 * Contents:
 * ---------
 *
 * Individual Operating System Constants
 * Generic Type Definitions and Constants
 * Miscellaneous Definitions and Declarations
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
 *    identical coding across a number of operating environments.  Any module
 *    which incorporates this header file MUST be written to handle all
 *    the environments declared by this header.
 *
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
 *       ENV_STDCALL             - Defines how symbols are to be handled in DLL's
 *       ENV_CDECL                 and such.
 *       ENV_EXPORT_STDCALL
 *       ENV_EXPORT_CDECL
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
 *  1992/11/27 |  Adapted from Original Zinc Implementation (Shawn Brant)
 *             |
 *  1993/05/24 |  Added definitions for the VAX-C/VAX-VMS environment.
 *             |  (Shawn Brant)
 *             |
 *  1993/09/09 |  Added definitions for the EMX C++ compiler for OS/2
 *             |  (Shawn Brant)
 *             |
 *  1993/11/04 |  Made the keyword '_Far' and '_Near' an available modifier
 *             |  for MS-DOS.  This keyword will be defined out of existance.
 *             |  for other Operating Systems.  (Shawn Brant)
 *             |
 *  1994/01/11 |  Fixed a number of minor bugs in the definitions.
 *             |  (Shawn Brant)
 *             |
 *  1994/01/25 |  Added a definition for determining if you have virtual
 *             |  memory or not.  (Shawn Brant)
 *             |
 *  1994/02/03 |  Added support for the EMX G++ compiler under UNIX.
 *             |  (Shawn Brant)
 *             |
 *  1994/02/21 |  Added support for the EMX G++ compiler under OS/2
 *             |  Converted to 3-space tab format.
 *             |  (Shawn Brant)
 *             |
 *  1994/10/18 |  Changed basic type names to remove possibilities between
 *             |  other packages.  (Shawn Brant)
 *             |
 *  1995/05/09 |  Added support for the Sun 'C' compiler.
 *             |  (Shawn Brant)
 *             |
 *  1998/11/28 |  Added support for Win32.
 *             |  (Shawn Brant)
 *             |
 *  2015/06/19 |  Added support for a ENV_IMPORT macro to complement the
 *             |  companion ENV_EXPORT macro.  This is becoming necessary
 *             |  with modern compilers and multi-language interfaces.
 *             |  (Shawn Brant)
 *             |
 *  2015/09/18 |  00107 - Factored out Preprocessor macros into it's own
 *             |  header file.
 *             |  (Shawn Brant)
 *             |
 *  2015/12/05 |  00117 - Added standard definitions for exporting and 
 *             |  importing functions to and from a DLL using the standard
 *             |  and cdecl calling conventions.
 *             |  (Shawn Brant)
 *             |
 *  2016/11/22 |  00133 - Redefined ENV_PATHSEP to define a string and
 *             |  character equivalent definitions.
 *             |  (Shawn Brant)
 *             |
 *  2016/12/01 |  00135 - Defined the integer/pointer equivalence type that
 *             |  defines the integer size capable of holding an integer and
 *             |  such that casting between the integer and pointer does not
 *             |  alter the pointer value from the original.
 *             |
 *             |  Added declarations for ENV_STDCALL and ENV_CDECL which do
 *             |  not automatically export a routine from a library.
 *             |  (Shawn Brant)
 *             |
 *
 */
#endif

#ifndef __ENVIRON_H
#define __ENVIRON_H



#if 0
/*=============================================================================
 *
 * File Dependencies:
 *
 */
#endif


#ifndef  __ENVIRON_STDDEFS_H
#include "environ_stddefs.h"
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
 * Individual Operating System Constants
 * =====================================
 *
 *    Define constants and other symbols unique to different operating systems.
 *
 *
 * Members
 * -------
 *
 *    _Far
 *       MS-DOS only.  Modifies a data object to be accessed through
 *       a 'far' reference or function call.
 *
 *    _Near
 *       MS-DOS only.  Modifies a data object to be accesses through
 *       a 'near' reference or function call.
 *
 *    ENV_STDCALL
 *    ENV_CDECL
 *       This is a function declaration annotation that sets the calling
 *       convention for a particular routine.
 *
 *       This declaration does not automatically export the routine from
 *       a DLL, but it can be manually exported by informing the linker
 *       (in Windows, by using a .DEF file).
 *
 *       The CDECL calling convention should only be used when there are
 *       a variable number of arguments in the function prototype.  For 
 *       example, a routine similar to 'printf' would be declared with the
 *       CDECL calling convention.
 *
 *    ENV_EXPORT_STDCALL
 *    ENV_EXPORT_CDECL
 *       Windows Only.  Used when generating 'DLL's or importing from
 *       'DLL's, we define the object associated with it to be exportable,
 *       otherwise it simply gets defined away.
 *
 *       This declaration automatically informs the DLL Linker to export
 *       the routine out of the library.
 *
 *       Either calling convention can be used but the standard for Windows 
 *       DLL's is to use the Standard Call calling convention.
 *
 *       The CDECL calling convention should only be used when there are
 *       a variable number of arguments in the function prototype.  For 
 *       example, a routine similar to 'printf' would be declared with the
 *       CDECL calling convention.
 *
 *    ENV_IMPORT_STDCALL
 *    ENV_IMPORT_CDECL
 *       Windows Only.  The companion for ENV_EXPORT, this decorates the
 *       symbol name to which it is associated to match the exported symbol
 *       coming from the DLL.
 *
 *
 * Remarks
 * -------
 *
 *    These constants should be specific to each operating system and
 *    not specific to the compiler environment.
 *
 */
#endif


#if   ENV_WIN32
#  define   _Far
#  define   _Near

#  ifndef   __WINDOWS_H
#  include  "windows.h"
#  define   __WINDOWS_H
#  endif

#  ifndef ENV_GCC
#     define   ENV_STDCALL          WINAPI
#     define   ENV_CDECL            WINAPIV

#     define   ENV_EXPORT_STDCALL   WINAPI
#     define   ENV_IMPORT_STDCALL   WINAPI

#     define   ENV_EXPORT_CDECL     WINAPIV
#     define   ENV_IMPORT_CDECL     WINAPIV

#  else
#     define   ENV_STDCALL          __attribute__ (( stdcall ))
#     define   ENV_CDECL            __attribute__ (( cdecl ))

#     define   ENV_EXPORT_STDCALL   __attribute__ (( stdcall , dllexport ))
#     define   ENV_IMPORT_STDCALL   __attribute__ (( stdcall ))

#     define   ENV_EXPORT_CDECL     __attribute__ (( cdecl , dllexport ))
#     define   ENV_IMPORT_CDECL     __attribute__ (( cdecl ))

#  endif

#  define ENV_PATHSEP_CHR  '\\'
#  define ENV_PATHSEP_STR  "\\"

#endif




#if   ENV_MSWINDOWS
#  define   _Far                 __far
#  define   _Near                __near

#  define   ENV_STDCALL          far pascal
#  define   ENV_CDECL            far cdecl

#  define   ENV_EXPORT_STDCALL   far pascal _export
#  define   ENV_IMPORT_STDCALL   far pascal _export

#  define   ENV_EXPORT_CDECL     far cdecl _export
#  define   ENV_IMPORT_CDECL     far cdecl _export

#  define   ENV_PATHSEP_CHR  '\\'
#  define   ENV_PATHSEP_STR  "\\"

#endif




#if   ENV_MSDOS
#  ifndef __STDC__
#     define   _Far           __far
#     define   _Near          __near

#  else
#     define   _Far
#     define   _Near

#  endif

#  define      ENV_EXPORT_STDCALL
#  define      ENV_IMPORT_STDCALL

#  define      ENV_EXPORT_CDECL
#  define      ENV_IMPORT_CDECL


#  define ENV_PATHSEP_CHR  '\\'
#  define ENV_PATHSEP_STR  "\\"

#endif




#if   ENV_OS2
#  define   _Far
#  define   _Near

#  define      ENV_EXPORT_STDCALL
#  define      ENV_IMPORT_STDCALL

#  define      ENV_EXPORT_CDECL
#  define      ENV_IMPORT_CDECL


#  define   HIWORD( arg )     (((ULong)arg >> 16) & 0x0000FFFF)
#  define   LOWORD( arg )     ((ULong)arg & 0x0000FFFF)

#  define ENV_PATHSEP_CHR  '\\'
#  define ENV_PATHSEP_STR  "\\"

#endif



#if   ENV_UNIX || ENV_X11 || ENV_MOTIF
#  define   _Far
#  define   _Near

#  define   ENV_EXPORT_STDCALL
#  define   ENV_IMPORT_STDCALL

#  define   ENV_EXPORT_CDECL
#  define   ENV_IMPORT_CDECL

#  define   ENV_PATHSEP_CHR  '/'
#  define   ENV_PATHSEP_STR  "/"

#endif





#if   ENV_VAXVMS
#  define   _Far
#  define   _Near

#  define      ENV_EXPORT_STDCALL
#  define      ENV_IMPORT_STDCALL

#  define      ENV_EXPORT_CDECL
#  define      ENV_IMPORT_CDECL


#  define ENV_PATHSEP_CHR  ':'
#  define ENV_PATHSEP_STR  ":"

#endif



#if 0
/*-----------------------------------------------------------------------------
 *
 * Generic Type Definitions and Constants
 * ======================================
 *
 *    Type definitions and constants bridged across all environments.
 *
 *
 * Members
 * -------
 *
 *    SWVoid .. SWF64
 *       Type definitions which are guaranteed (as much as is possible)
 *       to be identically size'd data objects across all environments.
 *
 *       The names begin with SW standing for 'Sterling Wood'.  We also
 *       have 'I', 'U', and 'F' standing for 'Integer', 'Unsigned', and 'Float
 *       respectively.  Finally, the number indicates the number of bits
 *       in the data type.
 *
 *    SWIntPtr
 *    SWUIntPtr
 *       Integer types that can hold a pointer value such that casting from
 *       a pointer to an integer and back to a pointer will not result in a
 *       pointer different from the original.
 *
 *    NULL
 *       Declare a NULL pointer value.
 *
 *    TRUE/FALSE
 *       Declare the Boolean Values.
 *
 *
 * Remarks
 * -------
 *
 *    These typedef's should represent types of the same size if that is
 *    at all possible.  For instance, on the VAX an 'int' and a 'long' are
 *    both 32 bits long.  Therefore you should define an 'Int' as a 'short'
 *    when compiling on the VAX.
 *
 */
#endif


#if   ENV_MSDOS || ENV_MSWINDOWS || ENV_OS2
   /* 16-Bit system. */

   typedef        void              SWVoid;

   typedef        char              SWChar;
   typedef        char              SWI8;       /*  8 bits  */
   typedef        unsigned char     SWU8;       /*  8 bits  */

   typedef        int               SWI16;      /* 16 bits  */
   typedef        unsigned int      SWU16;      /* 16 bits  */

   typedef        long              SWI32;      /* 32 bits  */
   typedef        unsigned long     SWU32;      /* 32 bits  */

   typedef        float             SWF32;      /* 32 bits  */
   typedef        double            SWF64;      /* 64 bits  */

   typedef        SWU32             SWUIntPtr;
   typedef        SWI32             SWIntPtr;


#  ifndef   NULL
#     ifdef __TINY__
#        define   NULL              0U

#     endif

#     ifdef __SMALL__
#        define   NULL              0U

#     endif

#     ifdef __MEDIUM__
#        define   NULL              0U

#     endif

#     ifdef __COMPACT__
#        define   NULL              0L

#     endif

#     ifdef __LARGE__
#        define   NULL              0L

#     endif

#     ifdef __HUGE__
#        define   NULL              0L

#     endif
#  endif



#  ifndef   __ERRNO_H
#  include  <errno.h>
#  define   __ERRNO_H
#  endif

#endif




#if   ENV_WIN32
   typedef           void              SWVoid;

#  ifdef ENV_GCC
      /* Win32 and a newer GCC compiler. */
#     if __GNUC__ >= 4
#        ifndef   __INTTYPES_H
#        include  <inttypes.h>
#        define   __INTTYPES_H
#        endif

         typedef           char              SWChar;
         typedef           int8_t            SWI8;
         typedef           uint8_t           SWU8;

         typedef           int16_t           SWI16;
         typedef           uint16_t          SWU16;

         typedef           int32_t           SWI32;
         typedef           uint32_t          SWU32;

         typedef           float             SWF32;
         typedef           double            SWF64;

         typedef           uintptr_t         SWUintPtr;
         typedef           intptr_t          SWIntPtr;

      /* Win32 and an older GCC compiler. */
#     else
         typedef           char              SWChar;
         typedef           char              SWI8;
         typedef           unsigned char     SWU8;

         typedef           short             SWI16;
         typedef           unsigned short    SWU16;

         typedef           long              SWI32;
         typedef           unsigned long     SWU32;

         typedef           float             SWF32;
         typedef           double            SWF64;

         typedef           SWU32             SWUIntPtr;
         typedef           SWI32             SWIntPtr;

#     endif

   /* Win32 and not a GCC compiler. */
#  else
         typedef           char              SWChar;
         typedef           char              SWI8;
         typedef           unsigned char     SWU8;

         typedef           short             SWI16;
         typedef           unsigned short    SWU16;

         typedef           long              SWI32;
         typedef           unsigned long     SWU32;

         typedef           float             SWF32;
         typedef           double            SWF64;

         typedef           SWU32             SWUIntPtr;
         typedef           SWI32             SWIntPtr;

#  endif

   /* Win32 */
#  ifndef  NULL
#     define         NULL              0L

#  endif
#endif




#if   ENV_CFRONT
   typedef           void              SWVoid;

   typedef           char              SWChar;
   typedef           char              SWI8;
   typedef           unsigned char     SWU8;

   typedef           short             SWI16;
   typedef           unsigned short    SWU16;

   typedef           long              SWI32;
   typedef           unsigned long     SWU32;

   typedef           float             SWF32;
   typedef           double            SWF64;

   typedef           SWU32             SWUIntPtr;
   typedef           SWI32             SWIntPtr;


#  ifndef  NULL
#     define         NULL              0L

#  endif
#endif




#if   ENV_UNIX || ENV_X11 || ENV_MOTIF
#  ifndef   __INTTYPES_H
#  include  <inttypes.h>
#  define   __INTTYPES_H
#  endif

   typedef        void              SWVoid;

   typedef        char              SWChar;
   typedef        int8_t            SWI8;
   typedef        uint8_t           SWU8;

   typedef        int16_t           SWI16;
   typedef        uint16_t          SWU16;

   typedef        int32_t           SWI32;
   typedef        uint32_t          SWU32;

   typedef        float             SWF32;
   typedef        double            SWF64;

   typedef        uintptr_t         SWUIntPtr;
   typedef        intptr_t          SWIntPtr;



#  ifndef  NULL
#     define      NULL              0L

#  endif
#endif





#if   ENV_VAXVMS
#  if ENV_VAXC
#     define         SWVoid            void

#  else

      typedef        void              SWVoid;

#  endif


      typedef        char              SWChar;
      typedef        char              SWI8;
      typedef        unsigned char     SWU8;

      typedef        short             SWI16;
      typedef        unsigned short    SWU16;

      typedef        long              SWI32;
      typedef        unsigned long     SWU32;

      typedef        float             SWF32;
      typedef        double            SWF64;



#  ifndef  NULL
#     define         NULL              0L

#  endif
#endif



typedef     SWU8           SWBool;

typedef     SWI8           SWSChar;
typedef     SWU8           SWUChar;
typedef     SWU8           SWByte;

typedef     SWI16          SWShort;
typedef     SWU16          SWUShort;

typedef     SWI16          SWInt;
typedef     SWU16          SWUInt;
typedef     SWU16          SWSize_T;

typedef     SWI32          SWLong;
typedef     SWU32          SWULong;

typedef     SWF32          SWFloat;
typedef     SWF64          SWDouble;




#ifndef  TRUE
#  define   TRUE           1

#endif

#ifndef  FALSE
#  define   FALSE          0

#endif





/*-----------------------------------------------------------------------------
 *
 * Miscellaneous Definitions and Declarations
 * ==========================================
 *
 *    Definitions and Declarations which are envrinoment independant
 *
 *
 * Members
 * -------
 *
 *    Class
 *       This is only necessary for Borland MS-DOS.  Because of the crazy way
 *       the standard classes (like 'fstream') are declared, we need to
 *       automatically declare the classes the same way.
 *
 *    VoidF
 *       Cast a function pointer to type 'Void *'
 *
 *    VoidP
 *       Cast a regular pointer to type 'Void *'
 *
 *    NullP
 *       Returns a NULL pointer of the type specified.
 *
 *    NullF
 *       Returns a NULL function pointer of the type specified.
 *
 *
 * Remarks
 * -------
 *
 *    These declarations should not have '#ifdef's across environments.
 *
 */


#ifndef  VoidF
#define  VoidF( function )       ((Void *)(function))
#endif

#ifndef  VoidP
#define  VoidP( pointer )        ((Void *)(pointer))
#endif


#ifndef  NullP
#define  NullP( type )           ((type *) NULL)
#endif

#ifndef  NullF
#define  NullF( type )           ((type *) NULL)
#endif





/*=============================================================================
 *
 * Function Prototypes:
 *
 */


#ifdef __cplusplus
extern "C" {
#endif


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





#ifdef __cplusplus
}
#endif






/*=============================================================================
 *
 * END
 *
 */

#endif

