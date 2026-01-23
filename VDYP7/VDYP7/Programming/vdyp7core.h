/*=============================================================================
 *
 * Module Name....   VDYP7CORE Interface 'C' Definition Module
 * Filename.......   wincode\vdyp7core.h
 *
 * Copyright......   Source Code (c) 2003 - 2016
 *                   Government of British Columbia
 *                   All Rights Reserved
 *
 *
 *-----------------------------------------------------------------------------
 *
 * Contents:
 * ---------
 *
 * V7IntVDYP7Layer
 * V7ExtVDYP7Layer
 * V7IntVDYP7ProjectionType
 * V7ExtVDYP7ProjectionType
 * VDYP7_cPRIMARYLAYER
 * VDYP7_sPRIMARYLAYER
 * VDYP7_cVETERANLAYER
 * VDYP7_sVETERANLAYER
 * VDYP7_cRESIDUALLAYER
 * VDYP7_sRESIDUALLAYER
 * VDYP7_cREGENLAYER
 * VDYP7_sREGENLAYER
 * VDYP7_cDEADLAYER
 * VDYP7_sDEADLAYER
 * VDYP7_cDONOTPROJECTLAYER
 * VDYP7_sDONOTPROJECTLAYER
 *
 * vdyp7core_coredllversion
 * vdyp7core_calclibversion
 * vdyp7core_init
 * vdyp7core_shutdown
 * vdyp7core_numspecies
 * vdyp7core_speciescode
 * vdyp7core_speciesindex
 * vdyp7core_becindex
 * vdyp7core_beciscoastal
 *	vdyp7core_writefippolygon
 * vdyp7core_writefiplayer
 * vdyp7core_writefiplayerend
 * vdyp7core_writefipspecies
 * vdyp7core_writefipspeciesend
 * vdyp7core_runfipmodel
 * vdyp7core_writevripolygon
 * vdyp7core_writevrilayer
 * vdyp7core_writevrilayerend
 * vdyp7core_writevrispecies
 * vdyp7core_writevrisiteindex
 * vdyp7core_writevrisiteindexend
 * vdyp7core_retrieveadjstseeds
 * vdyp7core_setadjstadjustments
 * vdyp7core_setadjstadjustmentsend
 * vdyp7core_runadjstmodel
 * vdyp7core_runvdypmodel
 * vdyp7core_reloadprojectiondata
 * vdyp7core_requestyeardata
 *	vdyp7core_setprojectiontype
 *	vdyp7core_getprojectiontype
 *
 *
 *-----------------------------------------------------------------------------
 *
 * Notes:
 * ------
 *
 * Written in ANSI C
 *
 *
 *=============================================================================
 *
 * Modification History:
 * ---------------------
 *
 *
 *  Date       |  Details
 * ------------+---------------------------------------------------------------
 *  yyyy/mm/dd |
 *             |
 *  2003/03/12 |  Initial Implementation
 *             |  (Shawn Brant)
 *             |
 *  2003/08/30 |  Adjusted interface to account for ages no longer necessarily
 *             |  being integers.
 *             |  (Shawn Brant)
 *             |
 *  2003/09/23 |  When requesting year data, an indication is now returned
 *             |  if the polygon data was projected for that year.
 *             |  (Shawn Brant)
 *             |
 *  2004/01/05 |  Return the year of valid yields when reporting the FIP/VRI
 *             |  processing information.
 *             |  (Shawn Brant)
 *             |
 *  2004/03/23 |  Modified 'vdyp7core_requestyeardata' to return the site
 *             |  curve and dominant species info.
 *             |
 *             |  Modified 'vdyp7core_runvdypmodel' to allow the caller to
 *             |  explicitly disable VDYP7 or VDYPBACK on the call.
 *             |  (Shawn Brant)
 *             |
 *  2004/08/18 |  Added support for 2 layer processing - see IPSCB460
 *             |  (Shawn Brant)
 *             |
 *  2007/12/06 |  Added support for reloading previously projected data
 *             |  at different utilization levels (vdyp7core_reloadprojectiondata)
 *             |  (Shawn Brant)
 *             |
 *  2008/02/02 |  Return the error code (IER) and Model Pass Code (iPASS(10))
 *             |  as separate values whereas they returned as a combined
 *             |  value prior to this change and information was found to be
 *             |  lost.
 *             |  (Shawn Brant)
 *             |
 *  2015/06/19 |  Now using ENV_IMPORT macro for routines intended to be
 *             |  imported from a DLL.
 *             |  (Shawn Brant)
 *             |
 *  2015/08/16 |  00102
 *             |  Changes to support projections for different projection
 *             |  types (e.g. live stems vs. dead stems).
 *             |  (Shawn Brant)
 *             |
 *  2016/01/11 |  00116:
 *             |  Modifications to support new Dynamic Logging library.
 *             |  (Shawn Brant)
 *             |
 *
 */


#ifndef __VDYP7CORE_H
#define __VDYP7CORE_H




/*=============================================================================
 *
 * File Dependencies:
 *
 */


#ifndef  __ENVIRON_H
#include "environ.h"
#endif




/*=============================================================================
 *
 * Data and Data Structures
 *
 */


/*-----------------------------------------------------------------------------
 *
 * V7IntVDYP7Layer
 * V7ExtVDYP7Layer
 * ===============
 *
 *    Enumerates each of the layers supported by VDYP7CORE
 *
 *
 * Members
 * -------
 *
 *    enumV7CORE_Layer_P
 *       Indicates that the layer was processed as the primary VDYP7 layer.
 *
 *    enumV7CORE_Layer_V
 *       Indicates that the layer was processed as the veteran VDYP7 layer.
 *
 *    enumV7CORE_Layer_OTHER
 *       Generally indicates that this is a layer not to be processed or
 *       has not been processed by VDYP7CORE.  This layer code should not be
 *       passed into the V7CORE libraries.
 *
 *
 * Remarks
 * -------
 *
 *    Because an enumeration does not have a fixed data size type, the
 *    type 'V7ExtVDYP7Layer' provides this fixed size type.  In all cases
 *    through external interfaces, instances of 'V7IntVDYP7Layer' will
 *    be cast to 'V7ExtVDYP7Layer'.
 *
 *    2005/09/24:
 *    In order to support the non-processing of layers that do not get selected
 *    as the primary or veteran layers, we have added the 'OTHER' layer type
 *    to indicate that the layer was not processed or should not be processed.
 *
 */


typedef  enum
            {
            enumV7CORE_Layer_OTHER   = -1,

            enumV7CORE_Layer_FIRST   = 1,

            enumV7CORE_Layer_P       = enumV7CORE_Layer_FIRST,
            enumV7CORE_Layer_V,


            enumV7CORE_Layer_LAST    = enumV7CORE_Layer_V,
            enumV7CORE_Layer_COUNT   = enumV7CORE_Layer_LAST - enumV7CORE_Layer_FIRST + 1,
            enumV7CORE_Layer_DEFAULT = enumV7CORE_Layer_P

            }  V7IntVDYP7Layer;


typedef  SWI32    V7ExtVDYP7Layer;




/*-----------------------------------------------------------------------------
 *
 * VDYP7_cPRIMARYLAYER
 * VDYP7_sPRIMARYLAYER
 * VDYP7_cVETERANLAYER
 * VDYP7_sVETERANLAYER
 * VDYP7_cRESIDUALLAYER
 * VDYP7_sRESIDUALLAYER
 * VDYP7_cREGENLAYER
 * VDYP7_sREGENLAYER
 * VDYP7_cDEADLAYER
 * VDYP7_sDEADLAYER
 * VDYP7_cDONOTPROJECTLAYER
 * VDYP7_sDONOTPROJECTLAYER
 * ========================
 *
 *    Identifies the codes used to identify the VDYP7 primary, veteran or dead
 *    layers internally to the VDYP7CORE library.
 *
 *
 * Remarks
 * -------
 *
 *    There are two versions of each code:
 *       1. A character constant version.
 *       2. A string constant version.
 *
 *    These constants correspond to the constants associated to the
 *    enumeration V7IntVDYP7ProjectionType
 */


#define  VDYP7_cPRIMARYLAYER        'P'
#define  VDYP7_sPRIMARYLAYER        "P"

#define  VDYP7_cVETERANLAYER        'V'
#define  VDYP7_sVETERANLAYER        "V"

#define  VDYP7_cRESIDUALLAYER       'R'
#define  VDYP7_sRESIDUALLAYER       "R"

#define  VDYP7_cREGENLAYER          'Y'
#define  VDYP7_sREGENLAYER          "Y"

#define  VDYP7_cDEADLAYER           'D'
#define  VDYP7_sDEADLAYER           "D"

#define  VDYP7_cDONOTPROJECTLAYER   'X'
#define  VDYP7_sDONOTPROJECTLAYER   "X"



/*-----------------------------------------------------------------------------
 *
 * V7IntVDYP7ProjectionType
 * V7ExtVDYP7ProjectionType
 * ========================
 *
 *    Describes, for a projection (VDYP7, VDYPBACK) for which type of layer
 *    the projection represents.
 *
 *
 * Members
 * -------
 *
 *    enumV7CORE_PrjType_FIRST
 *    enumV7CORE_PrjType_LAST
 *    enumV7CORE_PrjType_COUNT
 *    enumV7CORE_PrjType_DEFAULT
 *    enumV7CORE_PrjType_UNKNOWN
 *       Metadata for the Projection Type enumeration pattern.
 *
 *    enumV7Core_PrjType_Primary
 *       The projection is for the stand's primary layer.
 *
 *    enumV7Core_PrjType_Veteran
 *       The projection is for the stand's veteran layer.
 *
 *    enumV7CORE_PrjType_Residual
 *       The projection is for the stand's residual layer.
 *
 *    enumV7CORE_PrjType_Regeneration
 *       The projection is for the stand's regeneration layer.
 *
 *    enumV7Core_PrjType_Dead
 *       The projection is for the stand's dead stem layer.
 *
 *    enumV7Core_PrjType_DoNoProject
 *       A live layer that should not be projected.
 *
 *
 * Remarks
 * -------
 *
 *    It is essential the constant values of this enumeration match the
 *    corresponding constant/parameter values in the VDYP7IO header file:
 *    'vdyp7io_prjtypes_enum.fi'
 *
 *    The projection types should be ordered in a sort of priority order
 *    projection types.
 *
 */


typedef  enum
            {
            enumV7CORE_PrjType_DoNotProject = -2,
            enumV7CORE_PrjType_UNKNOWN      = -1,
            enumV7CORE_PrjType_FIRST        = 0,

            enumV7CORE_PrjType_Primary      = enumV7CORE_PrjType_FIRST,
            enumV7CORE_PrjType_Veteran,
            enumV7CORE_PrjType_Residual,
            enumV7CORE_PrjType_Regeneration,
            enumV7CORE_PrjType_Dead,


            enumV7CORE_PrjType_LAST         = enumV7CORE_PrjType_Dead,
            enumV7CORE_PrjType_COUNT        = enumV7CORE_PrjType_LAST - enumV7CORE_PrjType_FIRST + 1,
            enumV7CORE_PrjType_DEFAULT      = enumV7CORE_PrjType_Primary

            }  V7IntVDYP7ProjectionType;


typedef  SWI32    V7ExtVDYP7ProjectionType;



/*-----------------------------------------------------------------------------
 *
 * Object Name
 * ===========
 *
 *    Brief Description of what this object represents or contains
 *
 *
 * Members (Optional Heading)
 * -------
 *
 *    Member1
 *       member description
 *
 *
 * Remarks (Optional Heading)
 * -------
 *
 *    Remarks, warnings, special conditions to be aware of, etc.
 *
 */


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
 *	vdyp7core_coredllversion
 *	========================
 *
 *		Returns the current version number of the VDYP7CORE DLL.
 *
 *
 *	Parameters
 *	----------
 *
 *		versionBuffer
 *			The buffer into which to place the version number.
 *
 *    versionBufferLen
 *       The maximum size of the 'versionBuffer' buffer.
 *
 *
 *	Remarks
 *	-------
 *
 *    The buffer should be at 16 characters in length.
 *		The buffer is right padded with spaces.
 *
 */


void     ENV_IMPORT_STDCALL  vdyp7core_coredllversion( SWChar  *  versionBuffer,
                                                       SWU32      versionBufferLen );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_calclibversion
 *	========================
 *
 *		Returns the current version number of the Supporting Calculation Library
 *
 *
 *	Parameters
 *	----------
 *
 *		versionBuffer
 *			The buffer into which to place the version number.
 *
 *    versionBufferLen
 *       The maximum size of the 'versionBuffer' buffer.
 *
 *
 *	Remarks
 *	-------
 *
 *    The buffer should be at 16 characters in length.
 *		The buffer is right padded with spaces.
 *
 */


void     ENV_IMPORT_STDCALL  vdyp7core_calclibversion( SWChar  *  versionBuffer,
                                                       SWU32      versionBufferLen );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_init
 *	==============
 *
 *		Initialize the VDYP7CORE library.
 *
 *
 *	Parameters
 *	----------
 *
 *		sConfigDir
 *			Directory name containing the VDYP7CORE configuiration files.
 *       A terminating directory separator must be supplied.
 *
 *    bSaveIntermediate
 *       TRUE     Intermediate calculations are saved.
 *       FALSE    Intermediate calculations are not saved.
 *
 *    bFileIO
 *       TRUE     File I/O will be used.
 *       FALSE    Memory I/O will be used.
 *
 *    iLogContext
 *       The logging context to associate all logging activities within the
 *       VDYP7CORE library against.
 *       May be NULL_LOG_CONTEXT
 *
 *    sLogContextConfigFileName
 *       The name of the Log Context Configuration File to use if the
 *       'iLogContext' parameter is set to NULL_LOG_CONTEXT.
 *       This parameter is ignored if 'iLogContext' is not NULL_LOG_CONTEXT.
 *       May be NULL or ""
 *
 *    iConfigDirLen
 *       The length of the configuration directory 'sConfigDir' name.
 *
 *    iLogContextConfigFileNameLen
 *       The length of the Log Context Config File Name
 *       'sLogContextConfigFileName'.
 *
 *
 *	Return Value
 *	------------
 *
 *    0     Indicates successful initialization.
 *
 *
 *	Remarks
 *	-------
 *
 *		If a LogContext handle is supplied through 'iLogContext', the
 *    'sLogContextConfigFileName' parameter is ignored.
 *
 *    If both 'iLogContext' is NULL_LOG_CONTEXT and 'sLogContextConfigFileName'
 *    is NULL or "", the VDYP7CORE library will produce no logging output.
 *
 */


SWI32  ENV_IMPORT_STDCALL
vdyp7core_init( SWChar const *      sConfigDir,
                SWI16 const *       bSaveIntermediate,
                SWI16 const *       bFileIO,
                SWI32 *             iLogContext,
                SWChar const *      sLogContextConfigFileName,
                SWU32               iConfigDirLen,
                SWU32               iLogContextConfigFileNameLen );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_shutdown
 *	==================
 *
 *		Shuts down operation of the VDYP7CORE library.
 *
 *
 *	Remarks
 *	-------
 *
 *		Once the library has been shut down, it must be re-initialized to be
 *    used again.
 *
 */

void  ENV_IMPORT_STDCALL  vdyp7core_shutdown();




/*-----------------------------------------------------------------------------
 *
 * vdyp7core_numspecies
 * ====================
 *
 *		Determine the number of VDYP7 supported species.
 *
 *
 *	Return Value
 *	------------
 *
 *		Total number of supported species.
 *
 *
 *	Remarks
 *	-------
 *
 *		The library must be successfully initialized prior to calling this
 *    routine.
 *
 */


SWI32    ENV_IMPORT_STDCALL  vdyp7core_numspecies( void );




/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_speciescode
 *	=====================
 *
 *		Returns the two character code of the corresponding species index.
 *
 *
 *	Parameters
 *	----------
 *
 *		spcsCode
 *			The buffer into which to place the species code.
 *
 *    spcsIndx
 *       The species index for which you wish the code for.
 *       The value must range between 1 and the value returned by
 *          vdyp7core_numspecies
 *
 *    spcsCodeLen
 *       The maximum size of the 'spcsCode' buffer.
 *
 *
 *	Remarks
 *	-------
 *
 *		The buffer is right padded with spaces.
 *
 */


void     ENV_IMPORT_STDCALL  vdyp7core_speciescode( SWChar  *  spcsCode,
                                                    SWI32 *    spcsIndx,
                                                    SWU32      spcsCodeLen );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_speciesindex
 *	======================
 *
 *		Converts a VDYP7 species code into a species index.
 *
 *
 *	Parameters
 *	----------
 *
 *		spcsCode
 *			The VDYP7 species code to convert to an index.
 *
 *    spcsCodeLen
 *       The species code length.
 *
 *
 *	Return Value
 *	------------
 *
 *		The index value of the VDYP7 Species.
 *
 */


SWI32    ENV_IMPORT_STDCALL  vdyp7core_speciesindex( SWChar const * spcsCode,
                                                     SWU32          spcsCodeLen );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_writefippolygon
 *	=========================
 *
 *		Writes the VDYP7CORE polygon information for a FIPSTART projection.
 *
 *
 *	Parameters
 *	----------
 *
 *		sDistrict
 *       District name responsible for the polygon.
 *
 *    sMapSheet
 *       The mapsheet name of the polygon.
 *
 *    sMapQuad
 *       The map quadrant of the polygon.
 *
 *    sMapSubQuad
 *			The the map sub-quadrant of the polygon.
 *
 *    iPolyNum
 *       The polygon number of the polygon.
 *
 *    iMeasurementYear
 *       The year the polygon attributes were measured.
 *
 *    sFIZ
 *       The Forest Inventory Zone of the polygon.
 *
 *    sBEC
 *       The BEC Zone of the polygon.
 *
 *    fPctFLand
 *       The Percent Forested Land of the polygon.
 *
 *    iMode
 *       The FIPSTART processing mode for the initial processing start.
 *
 *    sNonProdDesc
 *       The Non-Productive Description (if any).
 *
 *    fYldFactor
 *       The factor by which to multiply volume yields.
 *
 *    iDistrictLen
 *    iMapSheetLen
 *    iMapQuadLen
 *    iMapSubQuadLen
 *    iFIZLen
 *    iBECLen
 *    iNonProdDescLen
 *       The length of the corresponding strings.
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Indicates success.
 *    Otherwise an error occurred.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_writefippolygon( SWChar const *       sDistrict,
                           SWChar const *       sMapSheet,
                           SWChar const *       sMapQuad,
                           SWChar const *       sMapSubQuad,
                           SWI32 *              iPolyNum,
                           SWI32 *              iMeasurementYear,
                           SWChar const *       sFIZ,
                           SWChar const *       sBEC,
                           SWF32 *              fPctFLand,
                           SWI32 *              iMode,
                           SWChar const *       sNonProdDesc,
                           SWF32 *              fYldFactor,
                           SWU32                iDistrictLen,
                           SWU32                iMapSheetLen,
                           SWU32                iMapQuadLen,
                           SWU32                iMapSubQuadLen,
                           SWU32                iFIZLen,
                           SWU32                iBECLen,
                           SWU32                iNonProdDescLen );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_writefiplayer
 *	=======================
 *
 *		Writes one record of data of a particular FIP layer.
 *
 *
 *	Parameters
 *	----------
 *
 *		sDistrict
 *       District name responsible for the polygon.
 *
 *    sMapSheet
 *       The mapsheet name of the polygon.
 *
 *    sMapQuad
 *       The map quadrant of the polygon.
 *
 *    sMapSubQuad
 *			The the map sub-quadrant of the polygon.
 *
 *    iPolyNum
 *       The polygon number of the polygon.
 *
 *    iMeasurementYear
 *       The year the polygon attributes were measured.
 *
 *    sLayer
 *       The Layer ID for the layer we are adding.
 *
 *    fCC
 *       The crown closure of the layer.
 *
 *    sSiteSP0
 *       The SP0 site species which make up the site index information for
 *       this layer.
 *
 *    sSiteSP64
 *       The SP64 site species which make up the site index information for
 *       this layer.
 *
 *    fTotalAge
 *       The total age of the each of the SP0s.
 *
 *    fHeight
 *       The dominant heights of each of the SP0s.
 *
 *    iSiteCurve
 *       The site curve to be used for each of the SP0s.
 *
 *    fSI
 *       The site index values associated with each of the SP0s.
 *
 *    fYTBH
 *       The Years to Breast Heights for each of the SP0s.
 *
 *    fBHAge
 *       The Breast Height Ages for each of the SP0s.
 *
 *    iDistrictLen
 *    iMapSheetLen
 *    iMapQuadLen
 *    iMapSubQuadLen
 *    iLayerLen
 *    iSiteSP0Len
 *    iSiteSP64Len
 *
 *
 *	Return Value
 *	------------
 *
 *		0  Indicates success
 *    Otherwise an error occurred.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_writefiplayer( SWChar const *         sDistrict,
                         SWChar const *         sMapSheet,
                         SWChar const *         sMapQuad,
                         SWChar const *         sMapSubQuad,
                         SWI32 *                iPolyNumber,
                         SWI32 *                iMeasurementYear,
                         SWChar const *         sLayer,
                         SWF32 *                fCC,
                         SWChar const *         sSiteSP0,
                         SWChar const *         sSiteSP64,
                         SWF32 *                fTotalAge,
                         SWF32 *                fHeight,
                         SWI32 *                iSiteCurve,
                         SWF32 *                fSI,
                         SWF32 *                fYTBH,
                         SWF32 *                fBHAge,
                         SWU32                  iDistrictLen,
                         SWU32                  iMapSheetLen,
                         SWU32                  iMapQuadLen,
                         SWU32                  iMapSubQuadLen,
                         SWU32                  iLayerLen,
                         SWU32                  iSiteSP0Len,
                         SWU32                  iSiteSP64Len );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_writefiplayerend
 *	==========================
 *
 *		Terminates the list of layers to be added to the polygon.
 *
 *
 *	Parameters
 *	----------
 *
 *		sDistrict
 *       District name responsible for the polygon.
 *
 *    sMapSheet
 *       The mapsheet name of the polygon.
 *
 *    sMapQuad
 *       The map quadrant of the polygon.
 *
 *    sMapSubQuad
 *			The the map sub-quadrant of the polygon.
 *
 *    iPolyNum
 *       The polygon number of the polygon.
 *
 *    iMeasurementYear
 *       The year the polygon attributes were measured.
 *
 *    iDistrictLen
 *    iMapSheetLen
 *    iMapQuadLen
 *    iMapSubQuadLen
 *       Lengths of the strings being passed into the VDYP7CORE library.
 *
 *
 *	Return Value
 *	------------
 *
 *		0  Indicates success
 *    Otherwise an error occurred.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_writefiplayerend( SWChar const *         sDistrict,
                            SWChar const *         sMapSheet,
                            SWChar const *         sMapQuad,
                            SWChar const *         sMapSubQuad,
                            SWI32 *                iPolyNumber,
                            SWI32 *                iMeasurementYear,
                            SWU32                  iDistrictLen,
                            SWU32                  iMapSheetLen,
                            SWU32                  iMapQuadLen,
                            SWU32                  iMapSubQuadLen );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_writefipspecies
 *	=========================
 *
 *		Brief Description of what this function does
 *
 *
 *	Parameters
 *	----------
 *
 *		sDistrict
 *       District name responsible for the polygon.
 *
 *    sMapSheet
 *       The mapsheet name of the polygon.
 *
 *    sMapQuad
 *       The map quadrant of the polygon.
 *
 *    sMapSubQuad
 *			The the map sub-quadrant of the polygon.
 *
 *    iPolyNum
 *       The polygon number of the polygon.
 *
 *    iMeasurementYear
 *       The year the polygon attributes were measured.
 *
 *    sLayer
 *       The Layer ID for the layer we are adding.
 *
 *    sSP0
 *       The SP0 to be written out.
 *
 *    fSP0Pcnt
 *       The percent of the stand this SP0 comprises.
 *
 *    sSP64
 *       The SP64s which comprise this SP0.
 *
 *    fSP64Pcnt
 *       The relative percents of each species within this SP0
 *
 *    iDistrictLen
 *    iMapSheetLen
 *    iMapQuadLen
 *    iMapSubQuadLen
 *    iLayerLen
 *    iSP0Len
 *    iSP64Len
 *       Lengths of the strings being passed into the VDYP7CORE library.
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Indicates success
 *    Otherwise an error occurred.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_writefipspecies( SWChar const *       sDistrict,
                           SWChar const *       sMapSheet,
                           SWChar const *       sMapQuad,
                           SWChar const *       sMapSubQuad,
                           SWI32 *              iPolyNumber,
                           SWI32 *              iMeasurementYr,
                           SWChar const *       sLayer,
                           SWChar const *       sSP0,
                           SWF32 *              fSP0Pcnt,
                           SWChar const *       sSP64,
                           SWF32 *              fSP64Pcnt,
                           SWU32                iDistrictLen,
                           SWU32                iMapSheetLen,
                           SWU32                iMapQuadLen,
                           SWU32                iMapSubQuadLen,
                           SWU32                iLayerLen,
                           SWU32                iSP0Len,
                           SWU32                iSP64Len );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_writefipspeciesend
 *	============================
 *
 *		Writes out the end of species marker for a layer.
 *
 *
 *	Parameters
 *	----------
 *
 *		sDistrict
 *       District name responsible for the polygon.
 *
 *    sMapSheet
 *       The mapsheet name of the polygon.
 *
 *    sMapQuad
 *       The map quadrant of the polygon.
 *
 *    sMapSubQuad
 *			The the map sub-quadrant of the polygon.
 *
 *    iPolyNum
 *       The polygon number of the polygon.
 *
 *    iMeasurementYear
 *       The year the polygon attributes were measured.
 *
 *    iDistrictLen
 *    iMapSheetLen
 *    iMapQuadLen
 *    iMapSubQuadLen
 *       Lengths of the strings being passed into the VDYP7CORE library.
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Indicates success
 *    Otherwise an error occurred.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_writefipspeciesend( SWChar const *       sDistrict,
                              SWChar const *       sMapSheet,
                              SWChar const *       sMapQuad,
                              SWChar const *       sMapSubQuad,
                              SWI32 *              iPolyNum,
                              SWI32 *              iMeasurementYear,
                              SWU32                iDistrictLen,
                              SWU32                iMapSheetLen,
                              SWU32                iMapQuadLen,
                              SWU32                iMapSubQuadLen );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_runfipmodel
 *	=====================
 *
 *		Actually perform the FIPSTART initial processing step.
 *
 *
 * Parameters
 * ----------
 *
 *    iRunCode
 *       On output, contains the error code that occurred during processing.
 *       Only valid if the return value is non-zero.
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Indicates success
 *    -1    Error occurred (refer to iRunCode).  Do not attempt VRISTART
 *    -2    Error occurred (refer to iRunCode).  Attempt VRISTART.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL     vdyp7core_runfipmodel( SWI32 *   iRunCode );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_writevripolygon
 *	=========================
 *
 *		Writes the VDYP7CORE polygon information for a VRISTART projection.
 *
 *
 *	Parameters
 *	----------
 *
 *		sDistrict
 *       District name responsible for the polygon.
 *
 *    sMapSheet
 *       The mapsheet name of the polygon.
 *
 *    sMapQuad
 *       The map quadrant of the polygon.
 *
 *    sMapSubQuad
 *			The the map sub-quadrant of the polygon.
 *
 *    iPolyNum
 *       The polygon number of the polygon.
 *
 *    iMeasurementYear
 *       The year the polygon attributes were measured.
 *
 *    sBEC
 *       The BEC Zone of the polygon.
 *
 *    fPctFLand
 *       The Percent Forested Land of the polygon.
 *
 *    iMode
 *       The FIPSTART processing mode for the initial processing start.
 *
 *    sNonProdDesc
 *       The Non-Productive Description (if any).
 *
 *    fYldFactor
 *       The factor by which to multiply volume yields.
 *
 *    iDistrictLen
 *    iMapSheetLen
 *    iMapQuadLen
 *    iMapSubQuadLen
 *    iBECLen
 *    iNonProdDescLen
 *       The length of the corresponding strings.
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Indicates success.
 *    Otherwise an error occurred.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_writevripolygon( SWChar const *       sDistrict,
                           SWChar const *       sMapSheet,
                           SWChar const *       sMapQuad,
                           SWChar const *       sMapSubQuad,
                           SWI32 *              iPolyNum,
                           SWI32 *              iMeasurementYear,
                           SWChar const *       sBEC,
                           SWF32 *              fPctFLand,
                           SWI32 *              iMode,
                           SWChar const *       sNonProdDesc,
                           SWF32 *              fYldFactor,
                           SWU32                iDistrictLen,
                           SWU32                iMapSheetLen,
                           SWU32                iMapQuadLen,
                           SWU32                iMapSubQuadLen,
                           SWU32                iBECLen,
                           SWU32                iNonProdDescLen );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_writevrilayer
 *	=======================
 *
 *		Writes a single VRI layer out.
 *
 *
 *	Parameters
 *	----------
 *
 *		sDistrict
 *       District name responsible for the polygon.
 *
 *    sMapSheet
 *       The mapsheet name of the polygon.
 *
 *    sMapQuad
 *       The map quadrant of the polygon.
 *
 *    sMapSubQuad
 *			The the map sub-quadrant of the polygon.
 *
 *    iPolyNum
 *       The polygon number of the polygon.
 *
 *    iMeasurementYear
 *       The year the polygon attributes were measured.
 *
 *    sLayerID
 *       The layer identifier for this layer record.
 *
 *    fCrownClosure
 *       The crown closure for this layer.
 *
 *    fBasalArea
 *       The basal area for this layer.
 *
 *    fTreePerHectare
 *       The number of Trees per Hectare corresponding to this layer.
 *
 *    fUtilLevel
 *       The utilization level at which the values were measured.
 *
 *    iDistrictLen
 *    iMapSheetLen
 *    iMapQuadLen
 *    iMapSubQuadLen
 *    iLayerIDLen
 *       The length of the corresponding strings.
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Successfully wrote the layer record out.
 *    Otherwise an error occurred writing out the record.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_writevrilayer( SWChar const *         sDistrict,
                         SWChar const *         sMapSheet,
                         SWChar const *         sMapQuad,
                         SWChar const *         sMapSubQuad,
                         SWI32 *                iPolygonNumber,
                         SWI32 *                iMeasurementYear,
                         SWChar const *         sLayerID,
                         SWF32 *                fCrownClosure,
                         SWF32 *                fBasalArea,
                         SWF32 *                fTreesPerHectare,
                         SWF32 *                fUtilLevel,
                         SWU32                  iDistrictLen,
                         SWU32                  iMapSheetLen,
                         SWU32                  iMapQuadLen,
                         SWU32                  iMapSubQuadLen,
                         SWU32                  iLayerIDLen );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_writevrilayerend
 *	==========================
 *
 *		Marks the end of VRI layer records.
 *
 *
 *	Parameters
 *	----------
 *
 *		sDistrict
 *       District name responsible for the polygon.
 *
 *    sMapSheet
 *       The mapsheet name of the polygon.
 *
 *    sMapQuad
 *       The map quadrant of the polygon.
 *
 *    sMapSubQuad
 *			The the map sub-quadrant of the polygon.
 *
 *    iPolyNum
 *       The polygon number of the polygon.
 *
 *    iMeasurementYear
 *       The year the polygon attributes were measured.
 *
 *    iDistrictLen
 *    iMapSheetLen
 *    iMapQuadLen
 *    iMapSubQuadLen
 *       The length of the corresponding strings.
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Indicates that the end of layers marker was successfully
 *          written.
 *
 *    Otherwise, an error occurred writing the marker record.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_writevrilayerend( SWChar const *         sDistrict,
                            SWChar const *         sMapSheet,
                            SWChar const *         sMapQuad,
                            SWChar const *         sMapSubQuad,
                            SWI32 *                iPolyNumber,
                            SWI32 *                iMeasurementYear,
                            SWU32                  iDistrictLen,
                            SWU32                  iMapSheetLen,
                            SWU32                  iMapQuadLen,
                            SWU32                  iMapSubQuadLen );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_writevrispecies
 *	=========================
 *
 *		Write out one record of VRI Species information.
 *
 *
 *	Parameters
 *	----------
 *
 *		sDistrict
 *       District name responsible for the polygon.
 *
 *    sMapSheet
 *       The mapsheet name of the polygon.
 *
 *    sMapQuad
 *       The map quadrant of the polygon.
 *
 *    sMapSubQuad
 *			The the map sub-quadrant of the polygon.
 *
 *    iPolyNum
 *       The polygon number of the polygon.
 *
 *    iMeasurementYear
 *       The year the polygon attributes were measured.
 *
 *    sLayerID
 *       The layer for which this species record applied.
 *
 *    sSP0
 *       The VDYP7 Species corresponding to this record.
 *
 *    fSP0Pcnt
 *       The percent of the stand this VDYP7 Species makes up.
 *
 *    sSP64
 *       The list of SP64 species which comprise this SP0.
 *
 *    fSP64Pcnt
 *       The relative amounts of each SP64 in this SP0.
 *
 *    iDistrictLen
 *    iMapSheetLen
 *    iMapQuadLen
 *    iMapSubQuadLen
 *    iLayerIDLen
 *    iSP0Len
 *    iSP64Len
 *       The length of the corresponding strings.
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Successfully wrote the species record out.
 *    Otherwise an error occurred writing the record out.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_writevrispecies( SWChar const *       sDistrict,
                           SWChar const *       sMapSheet,
                           SWChar const *       sMapQuad,
                           SWChar const *       sMapSubQuad,
                           SWI32 *              iPolyNumber,
                           SWI32 *              iMeasurementYear,
                           SWChar const *       sLayer,
                           SWChar const *       sSP0,
                           SWF32 *              fSP0Pcnt,
                           SWChar const *       sSP64,
                           SWF32 *              fSP64Pcnt,
                           SWU32                iDistrictLen,
                           SWU32                iMapSheetLen,
                           SWU32                iMapQuadLen,
                           SWU32                iMapSubQuadLen,
                           SWU32                iLayerLen,
                           SWU32                iSP0Len,
                           SWU32                iSP64Len );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_writevrispeciesend
 *	============================
 *
 *		Mark the end of the species which makes up this stand.
 *
 *
 *	Parameters
 *	----------
 *
 *		sDistrict
 *       District name responsible for the polygon.
 *
 *    sMapSheet
 *       The mapsheet name of the polygon.
 *
 *    sMapQuad
 *       The map quadrant of the polygon.
 *
 *    sMapSubQuad
 *			The the map sub-quadrant of the polygon.
 *
 *    iPolyNum
 *       The polygon number of the polygon.
 *
 *    iMeasurementYear
 *       The year the polygon attributes were measured.
 *
 *    iDistrictLen
 *    iMapSheetLen
 *    iMapQuadLen
 *    iMapSubQuadLen
 *       The length of the corresponding strings.
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Successfully wrote the end of species record out.
 *    Otherwise an error occurred writing the record out.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_writevrispeciesend( SWChar const *       sDistrict,
                              SWChar const *       sMapSheet,
                              SWChar const *       sMapQuad,
                              SWChar const *       sMapSubQuad,
                              SWI32 *              iPolyNum,
                              SWI32 *              iMeasurementYear,
                              SWU32                iDistrictLen,
                              SWU32                iMapSheetLen,
                              SWU32                iMapQuadLen,
                              SWU32                iMapSubQuadLen );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_writevrisiteindex
 *	===========================
 *
 *		Write out a single VRI Site Index record.
 *
 *
 *	Parameters
 *	----------
 *
 *		sDistrict
 *       District name responsible for the polygon.
 *
 *    sMapSheet
 *       The mapsheet name of the polygon.
 *
 *    sMapQuad
 *       The map quadrant of the polygon.
 *
 *    sMapSubQuad
 *			The the map sub-quadrant of the polygon.
 *
 *    iPolyNumber
 *       The polygon number of the polygon.
 *
 *    iMeasurementYear
 *       The year the polygon attributes were measured.
 *
 *    sLayerID
 *       The layer for which this species record applied.
 *
 *    fTotalAge
 *       The total age of the species.
 *       If not known, supply -9.0
 *
 *    fDomHeight
 *       The dominant height of the species.
 *       If not known, supply -9.0
 *
 *    fSiteIndex
 *       The site index of the species.
 *       If not known, supply -9.0
 *
 *    sSP0
 *       The name of the VDYP7 species.
 *
 *    sSP64
 *       The name of the major SP64 making up this SP0.
 *
 *    fYTBH
 *       The Years to Breast Height for the species.
 *       If not known, supply -9.0
 *
 *    fBHAge
 *       The Breast Height Age for the species.
 *       If not known, supply -9.0
 *
 *    iSiteCurve
 *       The site curve number associated with the site SP64
 *
 *    iDistrictLen
 *    iMapSheetLen
 *    iMapQuadLen
 *    iMapSubQuadLen
 *    iLayerIDLen
 *       The length of the corresponding strings.
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Successfully wrote the site index record out.
 *    Otherwise an error occurred writing out the record.
 *
 *
 *	Remarks
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_writevrisiteindex( SWChar const *       sDistrict,
                             SWChar const *       sMapSheet,
                             SWChar const *       sMapQuad,
                             SWChar const *       sMapSubQuad,
                             SWI32 *              iPolyNumber,
                             SWI32 *              iMeasurementYear,
                             SWChar const *       sLayerID,
                             SWF32 *              fTotalAge,
                             SWF32 *              fDomHeight,
                             SWF32 *              fSiteIndex,
                             SWChar const *       sSiteSP0,
                             SWChar const *       sSiteSP64,
                             SWF32 *              fYTBH,
                             SWF32 *              fBHAge,
                             SWI32 *              iSiteCurve,
                             SWU32                iDistrictLen,
                             SWU32                iMapSheetLen,
                             SWU32                iMapQuadLen,
                             SWU32                iMapSubQuadLen,
                             SWU32                iLayerIDLen,
                             SWU32                iSiteSP0Len,
                             SWU32                iSiteSP64Len );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_writevrisiteindexend
 *	==============================
 *
 *		Mark the end of the site index records for the polygon.
 *
 *
 *	Parameters
 *	----------
 *
 *		sDistrict
 *       District name responsible for the polygon.
 *
 *    sMapSheet
 *       The mapsheet name of the polygon.
 *
 *    sMapQuad
 *       The map quadrant of the polygon.
 *
 *    sMapSubQuad
 *			The the map sub-quadrant of the polygon.
 *
 *    iPolyNum
 *       The polygon number of the polygon.
 *
 *    iMeasurementYear
 *       The year the polygon attributes were measured.
 *
 *    iDistrictLen
 *    iMapSheetLen
 *    iMapQuadLen
 *    iMapSubQuadLen
 *       The length of the corresponding strings.
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Successfully wrote the site index record out.
 *    Otherwise an error occurred writing out the record.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_writevrisiteindexend( SWChar const *       sDistrict,
                                SWChar const *       sMapSheet,
                                SWChar const *       sMapQuad,
                                SWChar const *       sMapSubQuad,
                                SWI32 *              iPolyNumber,
                                SWI32 *              iMeasurementYear,
                                SWU32                iDistrictLen,
                                SWU32                iMapSheetLen,
                                SWU32                iMapQuadLen,
                                SWU32                iMapSubQuadLen );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_runvrimodel
 *	=====================
 *
 *		Actually perform the VRISTART initial processing step.
 *
 *
 * Parameters
 * ----------
 *
 *    iRunCode
 *       On output, contains the error code that occurred during processing.
 *       Only valid if the return value is non-zero.
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Indicates success
 *    Otherwise an error occurred.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL     vdyp7core_runvrimodel( SWI32 *   iRunCode );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_getfipvriprocessinginfo
 *	=================================
 *
 *		Determines the actual Processing Mode and Percent Forested Land values
 *    that were actually used in initial processing.
 *
 *
 *	Parameters
 *	----------
 *
 *		iMode
 *			On output, determines which processing mode for the growth model
 *       was actually used.
 *
 *    iYearYields
 *       On output, holds the first year at which yields can be predicted.
 *       Note that there may be years in the past that also can predict
 *       yields.  However, this year refers to the first year on or after
 *       the stated establishment year when supplying stand parameters.
 *
 *    fPctForestedLand
 *       On output, determines the actual Percent Forested Land value which
 *       was determined for initial processing.
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Indicates success.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_getfipvriprocessinginfo( SWI32 *              iMode,
                                   SWI32 *              iYearYields,
                                   SWF32 *              fPctForestedLand );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_retrieveadjstseeds
 *	============================
 *
 *		Retrieves the adjustment seeds after performing initial processing.
 *
 *
 *	Parameters
 *	----------
 *
 *    fBA075
 *       On output, contains the Basal Area at the 7.5cm+ utilization level.
 *
 *		fLH075
 *			On output, contains the Lorey Height at the 7.5cm+ utilization level.
 *
 *    fWSV075
 *       On output, contains the Whole Stem Volume at the 7.5cm+ utilization
 *       level.
 *
 *    fBA125
 *       On output, contains the Basal Area at the 12.5cm+ utilization level.
 *
 *    fWSV125
 *       On output, contains the Whole Stem Volume at the 12.5cm+ utilization
 *       level.
 *
 *    fVCU125
 *       On output, contains the Close Utilization Volume at the 12.5cm+
 *       utilization level.
 *
 *    fVD125
 *       On output, contains the Decay Only Volume at the 12.5cm+ utilization
 *       level.
 *
 *    fDW125
 *       On output, contains the Decay/Waste Volume at the 12.5cm+ utilization
 *       level.
 *
 *    fRsrvd1
 *    fRsrvd2
 *    fRsrvd3
 *       Reserved parameters not returning any information.
 *
 *    iReqLayer
 *       The VDYP7 Layer to retrieve adjustment seed information for.
 *          1  Indicates the Primary Layer
 *          2  Indicates the Veteran Layer
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Indicates successful return of the adjustment seeds.
 *    Otherwise some other error occurred.
 *
 *
 *	Remarks
 *	-------
 *
 *		The reserved values are not set to any particular value but must
 *    be supplied for future use.
 *
 *    Basal Area 7.5cm+ is not strictly an adjustment seed, but its use is
 *    required in multiple layer processing as it is used for weighting
 *    seeds such as Lorey Height across different layers.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_retrieveadjstseeds( SWF32 *              fBA075,
                              SWF32 *              fLH075,
                              SWF32 *              fWSV075,
                              SWF32 *              fBA125,
                              SWF32 *              fWSV125,
                              SWF32 *              fVCU125,
                              SWF32 *              fVD125,
                              SWF32 *              fVDW125,
                              SWF32 *              fRsrvd1,
                              SWF32 *              fRsrvd2,
                              SWF32 *              fRsrvd3,
                              SWI32 *              iReqLayer );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_setadjstadjustments
 *	=============================
 *
 *		Sets the adjustments for a particular layer for processing by VRIADJST
 *
 *
 *	Parameters
 *	----------
 *
 *		sDistrict
 *       District name responsible for the polygon.
 *
 *    sMapSheet
 *       The mapsheet name of the polygon.
 *
 *    sMapQuad
 *       The map quadrant of the polygon.
 *
 *    sMapSubQuad
 *			The the map sub-quadrant of the polygon.
 *
 *    iPolyNum
 *       The polygon number of the polygon.
 *
 *    iMeasurementYear
 *       The year the polygon attributes were measured.
 *
 *    sLayer
 *       The Layer ID for the layer we are adding.
 *
 *    iPolyNum
 *       The polygon number for the polygon.
 *
 *    iMeasYear
 *       The measurement year for the stand.
 *
 *    sLayerID
 *       The layer id to apply the adjustments to.
 *
 *    iMode
 *       Processing mode for this adjustment record.
 *       Should always be 0.
 *
 *    sSP0
 *       The SP0 to apply this record to.
 *       Should always be "  ".
 *
 *    fLH075
 *    fWSV075
 *    fBA125
 *    fWSV125
 *    fVCU125
 *    fVD125
 *    fVDW125
 *       The adjustments to be applied.
 *
 *    fRsrvd1
 *    fRsrvd2
 *    fRsrvd3
 *       Rerved parameters and not otherwise used.
 *
 *    iDistrictLen
 *    iMapSheetLen
 *    iMapQuadLen
 *    iMapSubQuadLen
 *    iLayerLen
 *    iSP0Len
 *       Lengths of the corresponding strings supplied through
 *       the previous parameters.
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Successfully added an adjustment record for VRIADJST
 *    An error occurred adding the adjustment record.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */

SWI32    ENV_IMPORT_STDCALL
vdyp7core_setadjstadjustments( SWChar const *         sDistrict,
                               SWChar const *         sMapSheet,
                               SWChar const *         sMapQuad,
                               SWChar const *         sMapSubQuad,
                               SWI32 *                iPolyNum,
                               SWI32 *                iMeasYear,
                               SWChar const *         sLayer,
                               SWI32 *                iMode,
                               SWChar const *         sSP0,
                               SWF32 *                fLH075,
                               SWF32 *                fWSV075,
                               SWF32 *                fBA125,
                               SWF32 *                fWSV125,
                               SWF32 *                fVCU125,
                               SWF32 *                fVD125,
                               SWF32 *                fVDW125,
                               SWF32 *                fRsrvd1,
                               SWF32 *                fRsrvd2,
                               SWF32 *                fRsrvd3,
                               SWU32                  iDistrictLen,
                               SWU32                  iMapSheetLen,
                               SWU32                  iMapQuadLen,
                               SWU32                  iMapSubQuadLen,
                               SWU32                  iLayerLen,
                               SWU32                  iSP0Len );




/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_setadjstadjustmentsend
 *	================================
 *
 *		Indicates no more adjustment records will be supplied.
 *
 *
 *	Parameters
 *	----------
 *
 *		sDistrict
 *       District name responsible for the polygon.
 *
 *    sMapSheet
 *       The mapsheet name of the polygon.
 *
 *    sMapQuad
 *       The map quadrant of the polygon.
 *
 *    sMapSubQuad
 *			The the map sub-quadrant of the polygon.
 *
 *    iPolyNum
 *       The polygon number of the polygon.
 *
 *    iMeasurementYear
 *       The year the polygon attributes were measured.
 *
 *    iDistrictLen
 *    iMapSheetLen
 *    iMapQuadLen
 *    iMapSubQuadLen
 *       The lengths of their corresponding strings.
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Successfully added the terminating adjustment record for VRIADJST
 *    An error occurred adding the adjustment record.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_setadjstadjustmentsend( SWChar const *         sDistrict,
                                  SWChar const *         sMapSheet,
                                  SWChar const *         sMapQuad,
                                  SWChar const *         sMapSubQuad,
                                  SWI32 *                iPolyNumber,
                                  SWI32 *                iMeasYear,
                                  SWU32                  iDistrictLen,
                                  SWU32                  iMapSheetLen,
                                  SWU32                  iMapQuadLen,
                                  SWU32                  iMapSubQuadLen );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_runadjstmodel
 *	=======================
 *
 *		Performs the VRIADJST model on any adjustment records added to the stand.
 *
 *
 *	Parameters
 *	----------
 *
 *    iRtrnCode
 *       On output, indicates whether or not the model completed with an error
 *       or with warnings.  Refer to iRunCode for the specific message.
 *
 *       0 indicates success.
 *
 *    iRunCode
 *       On output, contains the error code that occurred during processing.
 *       Only valid if the return value is non-zero.
 *
 *		iPassThrough
 *			-1    No processing takes place.  Input values are copied to output.
 *       0     VRIADJST processing takes place with adjustment records.
 *
 *
 *	Return Value
 *	------------
 *
 *		0     Successfully processed the stand through VRIADJST
 *    Otherwise an error occurred processing the stand.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


void    ENV_IMPORT_STDCALL
vdyp7core_runadjstmodel( SWI32 *                iRtrnCode,
                         SWI32 *                iRunCode,
                         SWI16 *                iPassThrough );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_runvdypmodel
 *	======================
 *
 *		Projects the stand through a specific age range.
 *
 *
 *	Parameters
 *	----------
 *
 *    iVDYP7Rtrn
 *       On output, contains the results of projecting the stand forward
 *                  using the VDYP7 model.
 *
 *    iVDYP7RunCode
 *       On output, contains the processing code of the VDYP7 model.
 *                  Corresponds to VDYPPASS(10).
 *
 *    iBACKRtrn
 *       On output, contains the results of projecting the stand backwards
 *                  using the BACKGROW model.
 *
 *    iBACKRunCode
 *       On output, contains the processing code of the BACKGROW model.
 *                  Corresponds to BACKPASS(10).
 *
 *		iMeasurementYear
 *			The year the stand was measured.
 *
 *    fStandAge
 *       The age of the stand at measurement year.
 *
 *    iStartYear
 *       The starting calendar year from which we wish to project.
 *
 *    iFinishYear
 *       The finishing calendar year to which we wish to project.
 *
 *    sSP0Spcs
 *       The 6 SP0 species within the stand concatenated together.
 *       Use blanks to denote empty place holders.
 *
 *    iUtilLvls
 *       The reporting utilization levels associated with each of the
 *       SP0 codes in 'sSP0Spcs'.
 *
 *    iSP0SpcsLen
 *       The length of the buffer containing the 6 SP0 species.
 *
 *    bDisableVDYP7
 *       If TRUE, the VDYP7 application will not be run despite what the
 *       age range indicates.
 *
 *       If FALSE, the VDYP7 application may be run if the age range indicates
 *       that it should.
 *
 *    bDisableBACK
 *       If TRUE, the VDYPBACK application will not be run despite what the
 *       age range indicates.
 *
 *       If FALSE, the VDYPBACK application may be run if the age range
 *       indicates that it should.
 *
 *
 *	Remarks
 *	-------
 *
 *		The stand age and start/finish ages are independent; the start and finish
 *    ages may be less than or greater than the stand age.
 *
 *    2004/03/24
 *    Allow the caller to explicitly disable VDYP7 and/or VDYPBACK.
 *    See Cam's 2004/03/23 e-mail.
 *
 */


void    ENV_IMPORT_STDCALL
vdyp7core_runvdypmodel( SWI32 *              iVDYP7Rtrn,
                        SWI32 *              iVDYP7RunCode,
                        SWI32 *              iBACKRtrn,
                        SWI32 *              iBACKRunCode,
                        SWI32 *              iMeasurementYear,
                        SWF32 *              fStandAge,
                        SWI32 *              iStartYear,
                        SWI32 *              iFinishYear,
                        SWChar const *       sSP0Spcs,
                        SWI32 *              iRprtUtils,
                        SWI16 *              bDisableVDYP7,
                        SWI16 *              bDisableBACK,
                        SWU32                iSP0SpcsLen );




/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_reloadprojectiondata
 *	==============================
 *
 *		Reloads the projected data that resulted from a previous run of
 *    vdyp7core_runvdypmodel.
 *
 *
 *	Parameters
 *	----------
 *
 *    iVDYP7Rtrn
 *       On output, contains the results of reloading the data resulting from
 *                  the VDYP7 model.
 *
 *    iBACKRtrn
 *       On output, contains the results of reloading the data resulting from
 *                  the BACKGROW model.
 *
 *    prjType
 *       Defines the layer projection type for which the projection 
 *       is being run.
 *
 *		iMeasurementYear
 *			The year the stand was measured.
 *       Must be the same as used by vdyp7core_runvdypmodel
 *
 *    fStandAge
 *       The age of the stand at measurement year.
 *       Must be the same as used by vdyp7core_runvdypmodel
 *
 *    iStartYear
 *       The starting calendar year from which we wish to project.
 *       Must be the same as used by vdyp7core_runvdypmodel
 *
 *    iFinishYear
 *       The finishing calendar year to which we wish to project.
 *       Must be the same as used by vdyp7core_runvdypmodel
 *
 *    sSP0Spcs
 *       The 6 SP0 species within the stand concatenated together.
 *       Use blanks to denote empty place holders.
 *       Must be the same as used by vdyp7core_runvdypmodel
 *
 *    iUtilLvls
 *       The reporting utilization levels associated with each of the
 *       SP0 codes in 'sSP0Spcs'.
 *       May vary from values used in vdy7core_runvdypmodel
 *
 *    iSP0SpcsLen
 *       The length of the buffer containing the 6 SP0 species.
 *       Must be the same as used by vdyp7core_runvdypmodel
 *
 *    bDisableVDYP7
 *       If TRUE, the VDYP7 application will not be run despite what the
 *       age range indicates.
 *
 *       If FALSE, the VDYP7 application may be run if the age range indicates
 *       that it should.
 *
 *       Must be the same as used by vdyp7core_runvdypmodel
 *
 *    bDisableBACK
 *       If TRUE, the VDYPBACK application will not be run despite what the
 *       age range indicates.
 *
 *       If FALSE, the VDYPBACK application may be run if the age range
 *       indicates that it should.
 *
 *       Must be the same as used by vdyp7core_runvdypmodel
 *
 *
 *	Remarks
 *	-------
 *
 *    This routine is used to load projection data at a different
 *    utilization level as was used for the original projection.
 *
 *    This routine must be used after a successful call to
 *    vdyp7core_runvdypmodel
 *
 */


void    ENV_IMPORT_STDCALL
vdyp7core_reloadprojectiondata( SWI32 *                    iVDYP7Rtrn,
                                SWI32 *                    iBACKRtrn,
                                V7ExtVDYP7ProjectionType * prjType,
                                SWI32 *                    iMeasurementYear,
                                SWF32 *                    fStandAge,
                                SWI32 *                    iStartYear,
                                SWI32 *                    iFinishYear,
                                SWChar const *             sSP0Spcs,
                                SWI32 *                    iRprtUtils,
                                SWI16 *                    bDisableVDYP7,
                                SWI16 *                    bDisableBACK,
                                SWU32                      iSP0SpcsLen );




/*-----------------------------------------------------------------------------
 *
 * vdyp7core_requestyeardata
 * =========================
 *
 *    Requests yield information at a specific stand age.
 *
 *
 * Parameters
 * ----------
 *
 *    bYearProjected
 *       On output,
 *          TRUE     The year was projected by VDYP7.
 *          FALSE    The year was not projected by VDYP7.
 *
 *          A requested year may not have been projected by VDYP7 if the
 *          stand was not mature enough for it to have generated a stable
 *          enough profile for a valid volume measurement.
 *
 *    bDominantSP0
 *       On output,
 *          TRUE     The requested species was listed as the dominant SP0
 *                   for the requested year's projection.
 *          FALSE    Stand level statistics were requested or the requested
 *                   SP0 was dominant for the requested year.
 *
 *    fTotalAge
 *       On output, contains the total age of the stand.
 *
 *    fDomHeight
 *       On output, contains the dominant height of the stand.
 *
 *    fLoreyHeight
 *       On output, contains the Lorey Height of the stand.
 *
 *    fSI
 *       On output, contains the Site Index of the stand.
 *
 *    fDiameter
 *       On output, contains the diameter of the stand.
 *
 *    fTPH
 *       On output, contains the Trees Per Hectare of the stand.
 *
 *    fVolumeWS
 *       On output, contains the Whole Stem Volume of the stand.
 *
 *    fVolumeCU
 *       On output, contains the Close Utilization Volume of the stand.
 *
 *    fVolumeD
 *       On output, contains the Volume less Decay Volume of the stand.
 *
 *    fVolumeDW
 *       On output, contains the Volume less Decay, Waste Volume of
 *       the stand.
 *
 *    fVolumeDWB
 *       On output, contains the Volume less Decay, Waste and Breakage
 *       Volume of the stand.
 *
 *    fBasalArea
 *       On output, contains the Basal Area of the stand.
 *
 *    fStndPcnt
 *       On output, contains the percentage of the SP0s in the stand.
 *       If the iSP0Ndx is 0, indicating stand summary information,
 *       this value should always be 100.0%
 *
 *    iSICurveUsed
 *       On output, contains the Site Index Curve used to grow the species.
 *       If the iSP0Ndx is 0, this is always -9.
 *
 *    prjType
 *       Defines the projection type to be processed.
 *
 *    iProjectedYear
 *       On input, specifies the projected calendar year for which you wish
 *       yield information.
 *
 *    iLayer
 *       The particular layer we are extracting data for:
 *          1     Primary Layer
 *          2     Veteran Layer
 *
 *    iSP0Ndx
 *       The SP0Index of the stand to request the information for.  A zero
 *       indicates you wish the summary information for the entire stand.
 *
 *
 * Return Value
 * ------------
 *
 *    0     Successfully requested the yield data.
 *    Otherwise, we could not get the yield information and output values
 *    are not valid.
 *
 *
 * Remarks
 * -------
 *
 *    Remarks, warnings, special conditions to be aware of, etc.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_requestyeardata( SWI16 *              bYearProjected,
                           SWU16 *              bDominantSP0,
                           SWF32 *              fTotalAge,
                           SWF32 *              fDomHeight,
                           SWF32 *              fLoreyHeight,
                           SWF32 *              fSI,
                           SWF32 *              fDiameter,
                           SWF32 *              fTPH,
                           SWF32 *              fVolumeWS,
                           SWF32 *              fVolumeCU,
                           SWF32 *              fVolumeD,
                           SWF32 *              fVolumeDW,
                           SWF32 *              fVolumeDWB,
                           SWF32 *              fBasalArea,
                           SWF32 *              fStndPcnt,
                           SWI32 *              iSICruveUsed,
                           SWI32 *              iProjectedYear,
                           V7ExtVDYP7Layer *    iLayer,
                           SWI32 *              iSP0Ndx );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_becindex
 *	==================
 *
 *		Converts a BEC Code to an Index.
 *
 *
 *	Parameters
 *	----------
 *
 *		sBECCode
 *			The BEC Code to be converted into an index code.
 *
 *    iBECLen
 *       The length of the BEC Code Buffer.
 *
 *
 *	Return Value
 *	------------
 *
 *		The BEC Code converted to an Index.
 *
 */


SWI32    ENV_IMPORT_STDCALL
vdyp7core_becindex( SWChar const *  sBECCode,
                    SWU32           iBECLen );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_beciscoastal
 *	======================
 *
 *		Determines if the supplied BEC Code is coastal or not.
 *
 *
 *	Parameters
 *	----------
 *
 *		iBECIndex
 *			The BEC Code Index to be determined if it is coastal or not.
 *       This Index can be determined with a call to 'vdyp7core_becindex'.
 *
 *
 *	Return Value
 *	------------
 *
 *		TRUE  The BEC Code is a coastal BEC.
 *    FALSE The BEC Code is an interior BEC.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */

SWI16    ENV_IMPORT_STDCALL
vdyp7core_beciscoastal( SWI32 *  iBECIndex );





/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_setprojectiontype
 *	===========================
 *
 *		Set the Projection Type to the supplied value.
 *
 *
 *	Parameters
 *	----------
 *
 *		newPrjType
 *		   A value ranging from 'enumV7CORE_PrjType_FIRST' and 
 *       'enumV7CORE_PrjType_LAST' as part of the V7IntVDYP7ProjectionType
 *       enumeration.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */

void  ENV_IMPORT_STDCALL  vdyp7core_setprojectiontype( SWI32 *   newPrjType );




/*-----------------------------------------------------------------------------
 *
 *	vdyp7core_getprojectiontype
 *	===========================
 *
 *		Return the currently set Layer Projection Type.
 *
 *
 *	Return Value
 *	------------
 *
 *		A value ranging from 'enumV7CORE_PrjType_FIRST' and 
 *    'enumV7CORE_PrjType_LAST' as part of the V7IntVDYP7ProjectionType
 *    enumeration.
 *
 *    'enumV7CORE_PrjType_UNKNOWN' indicates an internal error.
 *
 */


SWI32    ENV_IMPORT_STDCALL  vdyp7core_getprojectiontype( void );





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
