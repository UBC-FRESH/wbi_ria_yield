/*=============================================================================
 *
 * Module Name....   VDYP7 Extended Core Modules Interface
 * Filename.......   vdyp7interface.h
 *
 * Copyright......   Source Code (c) 2003 - 2017
 *                   Government of British Columbia
 *                   All Rights Reserved
 *
 *
 *-----------------------------------------------------------------------------
 *
 * Contents:
 * ---------
 *
 * V7ExtPolygonHandle
 * V7IntReturnCode
 * V7ExtReturnCode
 * V7IntSilviculturalBase
 * V7ExtSilviculturalBase
 * V7IntGrowthModel
 * V7ExtGrowthModel
 * V7IntProcessingMode
 * V7ExtProcessingMode
 *	V7IntCFSEcoZone
 * V7ExtCFSEcoZone
 * V7IntMessageSeverity
 * V7ExtMessageSeverity
 * V7IntMessageCode
 * V7ExtMessageCode
 * V7IntOtherVegType
 * V7ExtOtherVegType
 * V7IntNonVegType
 * V7ExtNonVegType
 * V7IntInventoryStandard
 * V7ExtInventoryStandard
 * V7IntLayerSummarizationMode
 * V7ExtLayerSummarizationMode
 * V7IntSpeciesIndex
 * V7ExtSpeciesIndex
 * V7IntSpeciesSorting
 * V7ExtSpeciesSorting
 * V7IntInterfaceOption
 * V7ExtInterfaceOption
 * V7EXT_INVALID_POLYGON_DESCRIPTOR
 * V7EXT_NULL_POLYGON_DESCRIPTOR
 * V7EXT_MAX_NUM_LAYERS_PER_POLYGON
 * V7EXT_MAX_NUM_SPECIES_PER_LAYER
 * V7EXT_MAX_LEN_VERSION
 * V7EXT_MAX_LEN_DISTRICT
 * V7EXT_MAX_LEN_MAPSHEET
 * V7EXT_MAX_LEN_MAPQUAD
 * V7EXT_MAX_LEN_MAPSUBQUAD
 * V7EXT_MAX_LEN_FIZ_LEN
 * V7EXT_MAX_LEN_BEC_LEN
 * V7EXT_MAX_LEN_RANK
 * V7EXT_MAX_LEN_NON_PROD_DESC
 * V7EXT_MAX_LEN_LAYER_ID
 * V7EXT_MAX_LEN_SP64
 * V7EXT_MAX_LEN_SP0
 * V7EXT_MAX_LEN_MESSAGE
 *
 * V7Ext_Version
 * V7Ext_Initialize
 * V7Ext_Shutdown
 * V7Ext_AllocatePolygonDescriptor
 * V7Ext_FreePolygonDescriptor
 * V7Ext_SetInterfaceOptionInt
 * V7Ext_GetInterfaceOptionInt
 * V7Ext_SetInterfaceOptionString
 * V7Ext_GetInterfaceOptionString
 * V7Ext_SetReportingUtilLevel
 * V7Ext_SetSpcsReportingUtilLevel
 * V7Ext_GetSpcsReportingUtilLevel
 *	V7Ext_GetSpcsMoFBiomassUtilLevel
 *	V7Ext_GetSpcsCFSBiomassUtilLevel
 * V7Ext_StartNewPolygon
 * V7Ext_PolygonIsCoastal
 * V7Ext_AddNonVegetationInfo
 * V7Ext_AddOtherVegetationInfo
 * V7Ext_AddLayer
 * V7Ext_AddLayerHistory
 * V7Ext_AddSpeciesComponent
 * V7Ext_CompletedPolygonDefinition
 * V7Ext_WasLayerProcessed
 * V7Ext_GetPolygonInfo
 * V7Ext_GetLayerInfo
 * V7Ext_GetNumLayers
 * V7Ext_GetNumSpecies
 * V7Ext_GetSpeciesName
 * V7Ext_GetSpeciesComponent
 * V7Ext_GetNumSpeciesGroups
 * V7Ext_GetSpeciesGroupName
 * V7Ext_GetSpeciesGroupComponent
 * V7Ext_GetNumSiteSpecies
 * V7Ext_GetNumSiteSpeciesGroups
 * V7Ext_GetSiteSpeciesComponent
 * V7Ext_GetSiteSpeciesGroupComponent
 * V7Ext_DetermineStandAgeAtYear
 * V7Ext_DetermineLayerAgeAtYear
 *	V7Ext_DetermineLayerYearOfDeath
 * V7Ext_DetermineVDYP7ProcessingLayer
 * V7Ext_InitialProcessingModeToBeUsed
 * V7Ext_PerformInitialProcessing
 * V7Ext_GetPolygonInitialProcessingInfo
 * V7Ext_GetFirstYearYieldsValid
 * V7Ext_GetStandAdjustmentSeeds
 * V7Ext_SetStandAdjustments
 * V7Ext_ProjectStandToYear
 * V7Ext_ProjectStandByAge
 * V7Ext_ReloadProjectedData
 * V7Ext_DetermineLayerStockability
 *
 * V7Ext_GetProjectedPolygonGrowthInfo
 * V7Ext_GetProjectedLayerStandGrowthInfo
 * V7Ext_GetProjectedLayerGroupGrowthInfo
 * V7Ext_GetProjectedLayerSpeciesGrowthInfo
 *
 *	V7Ext_GetProjectedPolygonVolumes
 * V7Ext_GetProjectedLayerStandVolumes
 * V7Ext_GetProjectedLayerStandMoFBiomass
 * V7Ext_GetProjectedLayerGroupVolumes
 *
 *	V7Ext_GetProjectedPolygonCFSBiomass
 *	V7Ext_GetProjectedLayerCFSBiomass
 *	V7Ext_GetProjectedPolygonMoFBiomass
 * V7Ext_GetProjectedLayerGroupMoFBiomass
 * V7Ext_GetProjectedLayerSpeciesVolumes
 * V7Ext_GetProjectedLayerSpeciesMoFBiomass
 * V7Ext_GetProjectedSpeciesPercent
 * V7Ext_GetProjectedSpeciesGroupPercent
 * V7Ext_GetProjectedDomSpcsAgeAtYear
 *
 * V7Ext_InitialProcessingReturnCode
 * V7Ext_AdjustmentProcessingReturnCode
 * V7Ext_PolygonProjectionReturnCode
 *
 * V7Ext_ReturnCodeToString
 * V7Ext_GrowthModelToString
 * V7Ext_ProcessingModeToString
 * V7Ext_LogPolygonDescriptor
 * V7Ext_NumProcessingMessages
 * V7Ext_GetProcessingMessage
 *
 * V7Ext_VB_Version
 * V7Ext_VB_AllocatePolygonDescriptor
 * V7Ext_VB_FreePolygonDescriptor
 * V7Ext_VB_ReturnCodeToString
 * V7Ext_VB_GrowthModelToString
 * V7Ext_VB_ProcessingModeToString
 * V7Ext_VB_GetSpeciesName
 * V7Ext_VB_GetSpeciesGroupName
 * V7Ext_VB_GetProcessingMessage
 * V7Ext_VB_DetermineVDYP7ProcessingLayer
 *
 * v7ext_for_version_
 * v7ext_for_allocatepolygondescriptor_
 * v7ext_for_freepolygondescriptor_
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
 *  2003/07/25 |  Added support for a Rank Code in the Layer.
 *             |  (Shawn Brant)
 *             |
 *  2003/08/20 |  Added Historical SI Species to the Layer parameters.
 *             |  Created constants for supplying Inventory Standard.
 *             |  (Shawn Brant)
 *             |
 *  2003/08/22 |  Changed name of Historical SI to Estimated SI.
 *             |  (Shawn Brant)
 *             |
 *  2003/09/25 |  Added support for an 'exclude' utilization level.
 *             |  (Shawn Brant)
 *             |
 *  2003/11/16 |  Added the routine 'V7Ext_GetProjectedSpeciesPercent'
 *             |  (Shawn Brant)
 *             |
 *  2004/01/05 |  Now return the first yield yields are reliably predicted
 *             |  after performing the initial processing through the
 *             |  'V7Ext_PerformInitialProcessing' routine.
 *             |  (Shawn Brant)
 *             |
 *  2004/01/19 |  Added error message codes and associated them with the
 *             |  error messages that are generated throughout the library.
 *             |  (Shawn Brant)
 *             |
 *  2004/02/15 |  Added support for Layer Summarization Modes and which VDYP7
 *             |  Layer a particular inventory layer got processed in.
 *             |
 *             |  Added a routine to check if a specific layer was processed
 *             |  (V7Ext_WasLayerProcessed).
 *             |  (Shawn Brant)
 *             |
 *  2004/02/19 |  Because of interactions between Stand/Species age, Site
 *             |  Index, and Estimated Site Index, the supplied site index
 *             |  may not be the value used when projecting the stand.  As
 *             |  a result, the site index used is now returned as a
 *             |  "projected" value.
 *             |  (Shawn Brant)
 *             |
 *  2004/02/29 |  Support the condition where a projected species percent
 *             |  may drop to 0.0%.
 *             |  (Shawn Brant)
 *             |
 *  2004/03/23 |  Modified to return dominant species flag and site curve
 *             |  used at a particular year in the projection for a specific
 *             |  SP0.
 *             |  (Shawn Brant)
 *             |
 *  2004/03/29 |  Added support for recording Site Species ordering.
 *             |  (Shawn Brant)
 *             |
 *  2004/04/05 |  Added a Species Index enumeration.
 *             |  (Shawn Brant)
 *             |
 *  2004/04/22 |  Modified 'V7Ext_GetSiteSpeciesGroupComponent' to return
 *             |  the percent total for an aggregate SP0 rather than the
 *             |  percent for the leading SP0 within the aggregate.
 *             |  (Shawn Brant)
 *             |
 *  2004/06/14 |  Added message codes to catch no leading species and
 *             |  a general inconsistent polygon definition.
 *             |  (Shawn Brant)
 *             |
 *  2004/08/23 |  Added basic support for multiple layer processing and
 *             |  merging.
 *             |  (Shawn Brant)
 *             |
 *  2004/09/08 |  Added support to identify the VDYP7 Layer a particular
 *             |  Inventory Layer is processed as.
 *             |  (Shawn Brant)
 *             |
 *  2004/10/15 |  Modified the interface to return the Yield Factor used when
 *             |  performing the initial processing.
 *             |  (Shawn Brant)
 *             |
 *  2005/01/13 |  Added support to suppress projected per hectare yields
 *             |  according to IPSCB206.
 *             |  (Shawn Brant)
 *             |
 *  2005/03/06 |  Modified as a result of making species sorting a public
 *             |  parameter.
 *             |  (Shawn Brant)
 *             |
 *  2005/03/28 |  Added the 'V7Ext_GetFirstYearYieldsValid' routine.
 *             |  (Shawn Brant)
 *             |
 *  2005/11/30 |  Added the concept of interface processing and configuration
 *             |  options to the interface.
 *             |  (Shawn Brant)
 *             |
 *  2006/11/23 |  Modified the input to allow -9 for an unknown Start Year
 *             |  when supplying History information.
 *             |  (Shawn Brant)
 *             |
 *  2007/12/06 |  Added support for reloading projection results as at
 *             |  different utilization levels without having to reproject.
 *             |  (Shawn Brant)
 *             |
 *  2009/03/26 |  Allow identical species to be supplied for a single layer.
 *             |  See Sam Otukol's Mar. 25 e-mail on the subject.
 *             |  (Shawn Brant)
 *             |
 *  2009/06/24 |  Provide support for enabling/disabling the substitution of
 *             |  Basal Area and TPH in situations where the projected stand
 *             |  is not viable but the BA and TPH should exist given the
 *             |  stand age.  See Sam Otukol's Apr. 23, 2009 e-mail.
 *             |  (Shawn Brant)
 *             |
 *  2010/06/30 |  Added Projected MoF Biomass capability.
 *             |  (Shawn Brant)
 *             |
 *  2011/02/06 |  0000006
 *             |  Added the routine 'V7Ext_GetPolygonInitialProcessingInfo'to
 *             |  return the Polygon Level Projected Values that are returned
 *             |  through the 'V7Ext_PerformInitialProcessing' routine.
 *             |  (Shawn Brant)
 *             |
 *  2011/12/22 |  0000042
 *             |  Add the following two routines to support reporting MoF
 *             |  Biomass at the Layer and at the Species Group by Layer
 *             |  levels:
 *             |        V7Ext_GetProjectedLayerStandMoFBiomass
 *             |        V7Ext_GetProjectedLayerGroupMoFBiomass
 *             |  (Shawn Brant)
 *             |
 *  2012/01/05 |  0000044
 *             |  Support for supplying options to control the logging of
 *             |  Timestamps and Routine Names in debug log files.
 *             |  (Shawn Brant)
 *             |
 *  2013/07/25 |  Additional support for the display of debug log file entries.
 *             |  (Shawn Brant)
 *             |
 *  2015/06/19 |  Now using ENV_IMPORT macro for routines intended to be
 *             |  imported from a DLL.
 *             |  (Shawn Brant)
 *             |
 *  2015/08/16 |  0000101
 *             |  Added a new Silviculterual Base code to indicate an Insect
 *             |  attack (e.g. Mountain Pine Beetle).
 *             |  (Shawn Brant)
 *             |
 *  2015/10/07 |  0000110
 *             |  Added support for Layer Stockability and other enhancements
 *             |  to support Dead Stem processing.
 *             |  (Shawn Brant)
 *             |
 *  2016/01/10 |  00116:
 *             |  Modified for use with the new Dynamic Logging library.
 *             |  (Shawn Brant)
 *             |
 *  2017/01/28 |  VDYP-2:
 *             |  Creation of routines to report projected values at a 
 *             |  summarized polygon layer in addition to the existing layer
 *             |  and species level reporting routines.
 *             |
 *             |  Changed V7ExtPolygonHandle to be a pointer to an internal
 *             |  structure rather than a 'void *' for additional type safety.
 *             |  (Shawn Brant)
 *             |
 *  2017/02/12 |  VDYP-2:
 *             |  Renamed all Biomass routines and objects to refer to an
 *             |  MoF Definition of Biomass (as oppsoed to the eventual
 *             |  implementation of the CFS (Canadian Forest Service)
 *             |  definition of Biomass).
 *             |
 *             |  Added a routine to summarize MoF Biomass across all projected
 *             |  layers in the polygon: V7Ext_GetProjectedPolygonMoFBiomass
 *             |  (Shawn Brant)
 *             |
 *  2017/06/28 |  VDYP-11
 *             |  Provided support to supply the Canadian Forest Service 
 *             |  EcoZone in with the Polygon Record.
 *             |  (Shawn Brant)
 *             |
 *  2017/07/19 |  VDYP-10
 *             |  Added support to return a Projected Layer Level CFS Biomass
 *             |  values.
 *             |  (Shawn Brant)
 *             |
 *  2017/09/01 |  VDYP-2
 *             |  Added routines 'V7Ext_GetSpcsMoFBiomassUtilLevel' and
 *	            |  'V7Ext_GetSpcsCFSBiomassUtilLevel' to help automate the 
 *             |  utilization levels to be used when computing Biomass.
 *             |  (Shawn Brant)
 *             |
 *
 */


#ifndef __VDYP7INTERFACE_H
#define __VDYP7INTERFACE_H




/*=============================================================================
 *
 * File Dependencies:
 *
 */


#ifndef  __ENVIRON_H
#include "environ.h"
#endif


#ifndef  __DYNLOG_H
#include "dynlog.h"
#endif


#ifndef  __STDIO_H
#include <stdio.h>
#define  __STDIO_H
#endif




/*=============================================================================
 *
 * Data and Data Structures
 *
 */


/*-----------------------------------------------------------------------------
 *
 * V7IntReturnCode
 * V7ExtReturnCode
 * ===============
 *
 *    Defines the error codes that can be returned by routines in this
 *    module.
 *
 *
 * Members
 * -------
 *
 *    V7EXT_ERR_FIRST
 *    V7EXT_ERR_LAST
 *    V7EXT_ERR_COUNT
 *       Indentifies the range of legal return codes.
 *
 *    V7EXT_SUCCESS
 *       Indicates the routine completed successfully.
 *
 *    V7EXT_ERR_INTERNALERROR
 *       An internal error occurred.  This should never happen and indicates
 *       a logic error.  This should always be considered an internal error.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       Processing some aspect of the polygon through the internal libraries
 *       resulted in some sort of error.  Other resources will indicate the
 *       actual nature of the problem.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       Indicates one or more of the parameters to a routine were
 *       not supplied, not valid, or incosistent with other parameters.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       A search for a layer resulted in no matches.
 *
 *    V7EXT_ERR_LAYERALREADYEXISTS
 *       An attempt to add a layer but a layer with that layer id was
 *       already added to the polygon.
 *
 *    V7EXT_ERR_TOOMANYLAYERS
 *       An attempt was made to add too many layers to the stand.
 *       The maximum number is defined by V7EXT_MAX_NUM_LAYERS_PER_POLYGON.
 *
 *    V7EXT_ERR_INVALIDSPECIES
 *       A species was indicated but was not recognized by the SiteTools
 *       library.
 *
 *    V7EXT_ERR_TOOMANYSPECIES
 *       An attempt was made to add too many species to the layer.
 *       The maximum number is defined by V7EXT_MAX_NUM_SPECIES_PER_LAYER.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       A requested species was searched for but not found.
 *
 *    V7EXT_ERR_SPECIESALREADYEXISTS
 *       An attempt was made to add a species to the layer but the species
 *       has already been added to the stand.
 *
 *    V7EXT_ERR_INVALIDUTILLEVEL
 *       A specified utilization level is not recognized or otherwise
 *       invalid.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The requested operation is not possible in the current polygon
 *       state.  For instance, one can not change a species composition
 *       after the polygon has been projected.
 *
 *    V7EXT_ERR_PERCENTNOT100
 *       The stand composition percentages do not sum up to 100%.
 *
 *    V7EXT_ERR_POLYGONNONPRODUCTIVE
 *       The polygon was labelled as non-productive and therefore will not
 *       be processed.
 *
 *    V7EXT_ERR_RANK1ALREADYEXISTS
 *       An attempt to add a polygon layer labelled as Rank 1 was made when
 *       another layer labelled as rank 1 already exists in the polygon.
 *
 *       You can have at most 1 layer labelled as rank 1.
 *
 *    V7EXT_ERR_INVALIDSTANDADJUSTMENT
 *       An attempt to add stand adjustments were made which violated 1 or
 *       more constraints stand adjustments.
 *
 *    V7EXT_ERR_INVALIDSITEINFO
 *       Missing or inconsistent site information parameters were supplied
 *       and required.
 *
 *    V7EXT_ERR_LAYERNOTPROCESSED
 *       Indicates the requested layer was not processed and so projected
 *       or other computed values are not available.
 *
 *
 * Remarks
 * -------
 *
 *    The size of 'enum' data types do not have a portable data type
 *    size based on platform or even compiler size.
 *
 *    For this reason, the internal error code type (V7IntReturnCode) will
 *    be cast to the V7ExtReturnCode as the routine exits.  This data type
 *    is guaranteed to be constant in size across platforms and compilers.
 *
 *    This point is especially important when linking against precompiled
 *    libraries.  It would be tough to link against a 16bit or 32bit
 *    return code without knowing before hand.  This mechanism guarantees
 *    return code size; a 'V7ExtReturnCode' is always returned.
 *
 */


typedef  enum
            {
            V7EXT_ERR_LAST                   = 0,

            V7EXT_SUCCESS                    = V7EXT_ERR_LAST,
            V7EXT_ERR_INTERNALERROR          =  -1,
            V7EXT_ERR_INVALIDPARAMETER       =  -2,
            V7EXT_ERR_CORELIBRARYERROR       =  -3,
            V7EXT_ERR_INVALIDBEC             =  -4,
            V7EXT_ERR_LAYERNOTFOUND          =  -5,
            V7EXT_ERR_LAYERALREADYEXISTS     =  -6,
            V7EXT_ERR_TOOMANYLAYERS          =  -7,
            V7EXT_ERR_INVALIDSPECIES         =  -8,
            V7EXT_ERR_SPECIESALREADYEXISTS   =  -9,
            V7EXT_ERR_SPECIESNOTFOUND        = -10,
            V7EXT_ERR_TOOMANYSPECIES         = -11,
            V7EXT_ERR_INVALIDUTILLEVEL       = -12,
            V7EXT_ERR_INCORRECTSTATE         = -13,
            V7EXT_ERR_PERCENTNOT100          = -14,
            V7EXT_ERR_POLYGONNONPRODUCTIVE   = -15,
            V7EXT_ERR_RANK1ALREADYEXISTS     = -16,
            V7EXT_ERR_INVALIDSTANDADJUSTMENT = -17,
            V7EXT_ERR_INVALIDSITEINFO        = -18,
            V7EXT_ERR_LAYERNOTPROCESSED      = -19,

            V7EXT_ERR_FIRST                  = V7EXT_ERR_LAYERNOTPROCESSED,
            V7EXT_ERR_COUNT                  = V7EXT_ERR_LAST - V7EXT_ERR_FIRST + 1

            }  V7IntReturnCode;


typedef  SWI32    V7ExtReturnCode;




/*-----------------------------------------------------------------------------
 *
 * V7ExtPolygonHandle
 * V7EXT_INVALID_POLYGON_DESCRIPTOR
 * V7EXT_NULL_POLYGON_DESCRIPTOR
 * ================================
 *
 *    Contains a handle to a polygon descriptor.
 *
 *
 * Remarks
 * -------
 *
 *    Valid handles must be allacated with calls to
 *    'V7Ext_AllocatePolygonDescriptor'
 *
 *    Valid handles must be freed up with subsequent calls to
 *    'V7Ext_FreePolygonDescriptor'.
 *
 *    Individual descriptor handles may be used for any number of polygons,
 *    one at a time.
 *
 */


typedef  struct structPolygonInfo *          V7ExtPolygonHandle;

#define  V7EXT_INVALID_POLYGON_DESCRIPTOR    (NULL)
#define  V7EXT_NULL_POLYGON_DESCRIPTOR       (NULL)




/*-----------------------------------------------------------------------------
 *
 * V7EXT_MAX_LEN_VERSION
 * V7EXT_MAX_LEN_DISTRICT
 * V7EXT_MAX_LEN_MAPSHEET
 * V7EXT_MAX_LEN_MAPQUAD
 * V7EXT_MAX_LEN_MAPSUBQUAD
 * V7EXT_MAX_LEN_FIZ_LEN
 * V7EXT_MAX_LEN_BEC_LEN
 * V7EXT_MAX_LEN_NON_PROD_DESC
 * V7EXT_MAX_LEN_LAYER_ID
 * V7EXT_MAX_LEN_RANK
 * V7EXT_MAX_LEN_SP64
 * V7EXT_MAX_LEN_SP0
 * V7EXT_MAX_LEN_MESSAGE
 * V7EXT_MAX_LEN_NON_FOREST_DESC
 * =============================
 *
 *    Specifies the minimum length for various string buffers to receive
 *    their strings string.
 *
 *
 * Members
 * -------
 *
 *    V7EXT_MAX_LEN_VERSION
 *       The maximum length of the Version string that can be returned
 *       from this library.
 *
 *    V7EXT_MAX_LEN_DISTRICT
 *       The maximum length of a buffer to receive a District string.
 *
 *    V7EXT_MAX_LEN_MAPSHEET
 *       The maximum length of a Mapsheet string.
 *
 *    V7EXT_MAX_LEN_MAP_QUAD
 *       The maximum length of a Map Quadrant string.
 *
 *    V7EXT_MAX_LEN_MAP_SUBQUAD
 *       The maximum length of a Map Sub-Quadrant string.
 *
 *    V7EXT_MAX_LEN_FIZ
 *       The maximum length of a FIZ code string.
 *
 *    V7EXT_MAX_LEN_BEC
 *       The maximum length of a BEC code string.
 *
 *    V7EXT_MAX_LEN_NON_PROD_DESC
 *       The maximum length of a Non-Prod Descriptor string.
 *
 *    V7EXT_MAX_LEN_NON_FOREST_DESC
 *       The maximim length of a Non-Forest Descriptor string.
 *
 *    V7EXT_MAX_LEN_LAYER_ID
 *       The maximum length of a Layer ID string.
 *
 *    V7EXT_MAX_LEN_RANK
 *       The maximum length of a Layer Rank Code string.
 *
 *    V7EXT_MAX_LEN_SP64
 *       The maximum length of an SP64 (WinVDYP) species.
 *
 *    V7EXT_MAX_LEN_SP0
 *       The maximum length of an SP0 (VDYP7) species.
 *
 *    V7EXT_MAX_LEN_MESSAGE
 *       The maximum length of a processing message.
 *
 *
 * Remarks
 * -------
 *
 *    These buffers lengths do not include space for null terminating characters
 *    for the strings.
 *
 */


#define  V7EXT_MAX_LEN_VERSION            (11)
#define  V7EXT_MAX_LEN_DISTRICT           (3)
#define  V7EXT_MAX_LEN_MAPSHEET           (7)
#define  V7EXT_MAX_LEN_MAP_QUAD           (1)
#define  V7EXT_MAX_LEN_MAP_SUBQUAD        (1)
#define  V7EXT_MAX_LEN_FIZ                (1)
#define  V7EXT_MAX_LEN_BEC                (4)
#define  V7EXT_MAX_LEN_NON_PROD_DESC      (5)
#define  V7EXT_MAX_LEN_NON_FOREST_DESC    (5)
#define  V7EXT_MAX_LEN_LAYER_ID           (1)
#define  V7EXT_MAX_LEN_RANK               (1)
#define  V7EXT_MAX_LEN_SP64               (3)
#define  V7EXT_MAX_LEN_SP0                (2)
#define  V7EXT_MAX_LEN_MESSAGE            (255)




/*-----------------------------------------------------------------------------
 *
 * V7IntSilviculturalBase
 * V7ExtSilviculturalBase
 * ======================
 *
 *    Disturbances occur in History records and must fall into one of a number
 *    of different catagories.
 *
 *
 * Members
 * -------
 *
 *    V7EXT_SilvBase_FIRST
 *    V7EXT_SilvBase_LAST
 *    V7EXT_SilvBase_COUNT
 *    V7EXT_SilvBase_DEFAULT
 *       Identifies the range and number of valid disturbance codes.
 *
 *    V7EXT_SilvBase_UNKNOWN
 *       Some unknown disturbance occurred.
 *
 *    V7EXT_SilvBase_DISTURBED
 *       The layer was disturbed by some natural or man made activity.
 *
 *    V7EXT_SilvBase_SITEPREPARATION
 *       Site preparation activities have occurred.
 *
 *    V7EXT_SilvBase_PLANTING
 *       A tree planting occurred.
 *
 *    V7EXT_SilvBase_STANDTENDING
 *       Stand tending activities have occurred.
 *
 *
 * Remarks
 * -------
 *
 *    The size of 'enum' data types do not have a portable data type
 *    size based on platform or even compiler size.
 *
 *    For this reason, the internal code type (V7IntSilviculturalCode) will
 *    be cast to the V7ExtSilviculturalCode.  This data type is guaranteed to
 *    be constant in size across platforms and compilers.
 *
 *    This point is especially important when linking against precompiled
 *    libraries.  It would be tough to link against a 16bit or 32bit
 *    return code without knowing before hand.  This mechanism guarantees
 *    return code size; a 'V7ExtSilviculturalBase' is always returned.
 *
 */


typedef  enum
         {
         V7EXT_SilvBase_FIRST            = 0,

         V7EXT_SilvBase_UNKNOWN          = V7EXT_SilvBase_FIRST,
         V7EXT_SilvBase_DISTURBED,
         V7EXT_SilvBase_INSECTATTACK,
         V7EXT_SilvBase_SITEPREPARATION,
         V7EXT_SilvBase_PLANTING,
         V7EXT_SilvBase_STANDTENDING,

         V7EXT_SilvBase_LAST             = V7EXT_SilvBase_STANDTENDING,
         V7EXT_SilvBase_COUNT            = V7EXT_SilvBase_LAST - V7EXT_SilvBase_FIRST + 1,
         V7EXT_SilvBase_DEFAULT          = V7EXT_SilvBase_UNKNOWN

         }  V7IntSilviculturalBase;


typedef  SWI32    V7ExtSilviculturalBase;





/*-----------------------------------------------------------------------------
 *
 * V7IntGrowthModel
 * V7ExtGrowthModel
 * ================
 *
 *    Lists the growth models availble to be used to start the stand model.
 *
 *
 * Members
 * -------
 *
 *    V7EXT_GrowthModel_FIRST
 *    V7EXT_GrowthModel_LAST
 *    V7EXT_GrowthModel_COUNT
 *       Identifies the range of values legal values in this enumeration can
 *       can take on.
 *
 *    V7EXT_GrowthModel_FIP
 *       Defines that the stand characteristics has FIPSTART properties.
 *
 *    V7EXT_GrowthModel_VRI
 *       Defines that the stand characteristics has VRISTART properties.
 *
 *    V7EXT_GrowthModel_DEFAULT
 *       Identifies which of the growth models is the default growth model
 *       when initializing or when you have to guess.
 *
 *       Note that changes to this value should trigger a corresponding
 *       change in value with the enum value 'V7EXT_ProcMode_DEFAULT'.
 *
 *    V7EXT_GrowthModel_UNKNOWN
 *       Indicates a growth model which is not known or not recognized.  This
 *       is not a valid growth model.
 *
 *
 * Remarks
 * -------
 *
 *    There are currently two stand types defined:
 *       FIP
 *       VRI
 *
 *    These two modes determine how the stand is converted so that it is
 *    compatible for the VDYP7 projection model.
 *
 *
 *    The size of 'enum' data types do not have a portable data type
 *    size based on platform or even compiler size.
 *
 *    For this reason, the internal code type (V7IntGrowthModel) will
 *    be cast to the V7ExtGrowthModel.  This data type is guaranteed to
 *    be constant in size across platforms and compilers.
 *
 *    This point is especially important when linking against precompiled
 *    libraries.  It would be tough to link against a 16bit or 32bit
 *    return code without knowing before hand.  This mechanism guarantees
 *    return code size; a 'V7IntGrowthModel' is always returned.
 *
 */


typedef  enum
   {
   V7EXT_GrowthModel_FIRST   = 0,

   V7EXT_GrowthModel_FIP     = V7EXT_GrowthModel_FIRST,
   V7EXT_GrowthModel_VRI,

   V7EXT_GrowthModel_LAST    = V7EXT_GrowthModel_VRI,
   V7EXT_GrowthModel_COUNT   = V7EXT_GrowthModel_LAST - V7EXT_GrowthModel_FIRST + 1,
   V7EXT_GrowthModel_DEFAULT = V7EXT_GrowthModel_VRI,

   V7EXT_GrowthModel_UNKNOWN = V7EXT_GrowthModel_FIRST - 1

   }     V7IntGrowthModel;



typedef  SWI32    V7ExtGrowthModel;




/*-----------------------------------------------------------------------------
 *
 * V7IntProcessingMode
 * V7ExtProcessingMode
 * ===================
 *
 *    Lists all possible processing modes when running one of the two
 *    stand models.
 *
 *
 * Members
 * -------
 *
 *    V7EXT_ProcModeFIP_FIRST
 *    V7EXT_ProcModeFIP_LAST
 *    V7EXT_ProcModeFIP_COUNT
 *       Defines the range the legal values for processing modes for the
 *       FIPSTART stand model.
 *
 *    V7EXT_ProcModeFIP_DO_NOT_PROCESS
 *       Specifies that the underlying growth model will not process the
 *       stand.  This seems a useless processing mode.
 *
 *    V7EXT_ProcModeFIP_DEFAULT
 *       The underlying FIP model determines which processing mode to use
 *       based on the supplied stand characteristics.
 *
 *    V7EXT_ProcModeFIP_FIPSTART
 *    V7EXT_ProcModeFIP_FIPYOUNG
 *       The specific processing modes for the FIPSTART stand model.
 *
 *    V7EXT_ProcModeVRI_FIRST
 *    V7EXT_ProcModeVRI_LAST
 *    V7EXT_ProcModeVRI_COUNT
 *       Defines the range of legal values for tprocessing modes for the
 *       VRISTART stand model.
 *
 *    V7EXT_ProcModeVRI_DO_NOT_PROCESS
 *       Specifies that the underlying growth model will not process the
 *       stand.  This seems a useless processing mode.
 *
 *    V7EXT_ProcModeVRI_DEFAULT
 *       The underlying VRI model determines which processing mode to use
 *       based on the supplied stand characteristics.
 *
 *    V7EXT_ProcModeVRI_VRISTART
 *    V7EXT_ProcModeVRI_VRIYOUNG
 *    V7EXT_ProcModeVRI_MINIMAL
 *    V7EXT_ProcModeVRI_CC
 *       The specific processing modes for the VRISTART stand model.
 *
 *    V7EXT_ProcMode_DEFAULT
 *       Indicates the default processing mode for the default growth model.
 *       Note that this value should track with changes to the
 *       V7EXT_GrowthModel_DEFAULT.
 *
 * Remarks
 * -------
 *
 *    The lists of processing modes are combined into a single enumeration
 *    to simplify parameter passing to and from functions.  By combining
 *    the values into a single enumeration, all values can be returned without
 *    having to resort to things like unions or something equally ugly.
 *
 *    Because of the overlap of the range of values, you must use the
 *    'V7IntGrowthModel' enumeration to uniquely select the appropriate
 *    symbol for a particular enumeration value.
 *
 */


typedef  enum
   {
   V7EXT_ProcModeFIP_FIRST            = -1,

   V7EXT_ProcModeFIP_DO_NOT_PROCESS   = V7EXT_ProcModeFIP_FIRST,
   V7EXT_ProcModeFIP_DEFAULT,
   V7EXT_ProcModeFIP_FIPSTART,
   V7EXT_ProcModeFIP_FIPYOUNG,

   V7EXT_ProcModeFIP_LAST             = V7EXT_ProcModeFIP_FIPYOUNG,
   V7EXT_ProcModeFIP_COUNT            = V7EXT_ProcModeFIP_LAST - V7EXT_ProcModeFIP_FIRST + 1,




   V7EXT_ProcModeVRI_FIRST            = -1,

   V7EXT_ProcModeVRI_DO_NOT_PROCESS   = V7EXT_ProcModeVRI_FIRST,
   V7EXT_ProcModeVRI_DEFAULT,
   V7EXT_ProcModeVRI_VRISTART,
   V7EXT_ProcModeVRI_VRIYOUNG,
   V7EXT_ProcModeVRI_MINIMAL,
   V7EXT_ProcModeVRI_CC,

   V7EXT_ProcModeVRI_LAST             = V7EXT_ProcModeVRI_CC,
   V7EXT_ProcModeVRI_COUNT            = V7EXT_ProcModeVRI_LAST - V7EXT_ProcModeVRI_FIRST + 1,



   V7EXT_ProcMode_DEFAULT             = V7EXT_ProcModeVRI_DEFAULT

   }  V7IntProcessingMode;



typedef  SWI32    V7ExtProcessingMode;





/*-----------------------------------------------------------------------------
 *
 *	V7IntCFSEcoZone
 * V7ExtCFSEcoZone
 *	===============
 *
 *		An enumeration of the different Canadian Forest Service ECO Zones.
 *
 *
 *	Members
 *	-------
 *
 *		V7EXT_cfsEco_UNKNOWN
 *       Represents an error condition or an uninitialized value.
 *
 *    V7EXT_cfsEco_FIRST
 *    V7EXT_cfsEco_LAST
 *    V7EXT_cfsEco_COUNT
 *    V7EXT_cfsEco_DEFAULT
 *			Meta-data for this enumeration.
 *
 *    V7EXT_cfsEco_ArcticCordillera
 *    V7EXT_cfsEco_NorthernArctic
 *    V7EXT_cfsEco_SouthernArctic
 *    V7EXT_cfsEco_TaigaPlains
 *    V7EXT_cfsEco_TaigaShield
 *    V7EXT_cfsEco_BorealShield
 *    V7EXT_cfsEco_AtlanticMaritime
 *    V7EXT_cfsEco_MixedwoodPlains
 *    V7EXT_cfsEco_BorealPlains
 *    V7EXT_cfsEco_Prairies
 *    V7EXT_cfsEco_TaigaCordillera
 *    V7EXT_cfsEco_BorealCordillera
 *    V7EXT_cfsEco_PacificMaritime
 *    V7EXT_cfsEco_MontaneCordillera
 *    V7EXT_cfsEco_HudsonPlains
 *       Specific Ecological Zones as defined by the Canadian Forest Service.
 *
 *
 *	Remarks
 *	-------
 *
 *		Definitions found in 'Volume_to_Biomass.doc' found in the 
 *    'Documents/CFS-Biomass' folder.
 *
 *    The 'Ext' version provides a fixed size variable without the advantages
 *    of language specific enumeration. This data type would be useful in
 *    cross language interfaces where data types size must be fixed and not
 *    dependent on compiler settings.
 *
 *    Elements for this table are automatically generated and copy and pasted
 *    from the:
 *       -  'Eco Zone C Enum Definition' column of the 
 *       -  'EcoZoneTable' found on the 
 *       -  'Lookups' tab in the
 *       -  'BC_Inventory_updates_by_CBMv2bs.xlsx' located in the
 *       -  'Documents/CFS-Biomass' folder.
 *
 */

typedef  enum
         {
         V7EXT_cfsEco_UNKNOWN = -9,
         V7EXT_cfsEco_FIRST   = 1,

         V7EXT_cfsEco_ArcticCordillera = V7EXT_cfsEco_FIRST,   /*  1 */
         V7EXT_cfsEco_NorthernArctic,                          /*  2 */
         V7EXT_cfsEco_SouthernArctic,                          /*  3 */
         V7EXT_cfsEco_TaigaPlains,                             /*  4 */
         V7EXT_cfsEco_TaigaShield,                             /*  5 */
         V7EXT_cfsEco_BorealShield,                            /*  6 */
         V7EXT_cfsEco_AtlanticMaritime,                        /*  7 */
         V7EXT_cfsEco_MixedwoodPlains,                         /*  8 */
         V7EXT_cfsEco_BorealPlains,                            /*  9 */
         V7EXT_cfsEco_Prairies,                                /* 10 */
         V7EXT_cfsEco_TaigaCordillera,                         /* 11 */
         V7EXT_cfsEco_BorealCordillera,                        /* 12 */
         V7EXT_cfsEco_PacificMaritime,                         /* 13 */
         V7EXT_cfsEco_MontaneCordillera,                       /* 14 */
         V7EXT_cfsEco_HudsonPlains,                            /* 15 */

         V7EXT_cfsEco_LAST    = V7EXT_cfsEco_HudsonPlains,
         V7EXT_cfsEco_COUNT   = V7EXT_cfsEco_LAST - V7EXT_cfsEco_FIRST + 1,
         V7EXT_cfsEco_DEFAULT = V7EXT_cfsEco_UNKNOWN

         }  V7IntCFSEcoZone;


typedef  SWI32    V7ExtCFSEcoZone;





/*-----------------------------------------------------------------------------
 *
 * V7IntMessageSeverity
 * V7ExtMessageSeverity
 * ====================
 *
 *    Identifies the different severities a message may have.
 *
 *
 * Members
 * -------
 *
 *    V7EXT_MsgSev_FIRST
 *    V7EXT_MsgSev_LAST
 *    V7EXT_MsgSev_COUNT
 *       Lists the number of, and the range of valid values for all message
 *       severity levels defined by this enumeration.
 *
 *    V7EXT_MsgSev_DEFAULT
 *       Identifies the default value to use when initializing.
 *
 *    V7EXT_MsgSev_INFORMATION
 *       Provides information regarding some aspect of the application.
 *       This is not an error.
 *
 *    V7EXT_MsgSev_STATUS
 *       Provides some information as the status of an operation or of the
 *       library.
 *
 *    V7EXT_MsgSev_WARNING
 *       Indicates some missing or invalid information was supplied but
 *       did not prevent the application from continuing.
 *
 *    V7EXT_MsgSev_ERROR
 *       Indicates some condition exists that prevented the operation from
 *       completing.
 *
 *    V7EXT_MsgSev_FATAL_ERROR
 *       Some condition exists that prevents this and potentially preventing
 *       future operations from continuing.
 *
 *
 * Remarks
 * -------
 *
 *    These codes are associated with messages returned from the library
 *    through the 'V7Ext_GetProcessingMessage'.
 *
 *    These codes are this libraries interpretation of the messages to which
 *    they are applied.
 *
 *    The type 'V7ExtMessageSeverity' is a solution to the problem that
 *    enumerations are not fixed in data type size.  Therefore, any external
 *    access to this data type will be cast into the external data type.
 *
 */


typedef  enum
            {
            V7EXT_MsgSev_FIRST        = 0,

            V7EXT_MsgSev_INFORMATION  = V7EXT_MsgSev_FIRST,
            V7EXT_MsgSev_STATUS,
            V7EXT_MsgSev_WARNING,
            V7EXT_MsgSev_ERROR,
            V7EXT_MsgSev_FATAL_ERROR,

            V7EXT_MsgSev_LAST         = V7EXT_MsgSev_FATAL_ERROR,
            V7EXT_MsgSev_COUNT        = V7EXT_MsgSev_LAST - V7EXT_MsgSev_FIRST + 1,
            V7EXT_MsgSev_DEFAULT      = V7EXT_MsgSev_ERROR

            }     V7IntMessageSeverity;



typedef  SWI32    V7ExtMessageSeverity;





/*-----------------------------------------------------------------------------
 *
 * V7IntMessageCode
 * V7ExtMessageCode
 * ================
 *
 *    Enumerates all of the different Error Message types that can be
 *    generated and returned by this library.
 *
 *
 * Members
 * -------
 *
 *    V7EXT_MsgCode_FIRST
 *    V7EXT_MsgCode_LAST
 *    V7EXT_MsgCode_COUNT
 *       Lists the number of, and the range of valid values for all message
 *       codes defined by this enumeration.
 *
 *    V7EXT_MsgCode_DEFAULT
 *       Identifies the default value to use when initializing.
 *
 *    V7EXT_MsgCode_NONE
 *       Indicates that there is no message.  Usually used as a place holder
 *       or to indicate success.
 *
 *    V7EXT_MsgCode_CORRUPT_CONTEXT
 *       An internal error indicating the polygon context has been corrupted
 *       somehow.  Hopefully the text of the message will give some indication
 *       as to what the problem could be.
 *
 *    V7EXT_MsgCode_VDYP7CORE_MSG
 *       An message returned by the VDYP7CORE library.
 *
 *    V7EXT_MsgCode_NO_BEC
 *       BEC Zone is required but was not supplied.
 *
 *    V7EXT_MsgCode_BAD_START_MODEL
 *       The Start Model (generally FIPSTART or VRISTART) was not recognized.
 *
 *    V7EXT_MsgCode_NO_PRIMARY_LAYER
 *       A layer that could be classified as a primary layer was not supplied.
 *
 *    V7EXT_MsgCode_NO_CC
 *       No crown closure is available nor derivable from stand information.
 *
 *    V7EXT_MsgCode_DEFAULT_CC
 *       The default Crown Closure was used.
 *
 *    V7EXT_MsgCode_NO_LH075
 *       Lorey height at the 7.5cm+ level was not supplied.
 *
 *    V7EXT_MsgCode_NO_BA075
 *       Basal area at the 7.5cm+ level was not supplied.
 *
 *    V7EXT_MsgCode_NO_BA125
 *       Basal area at the 12.5cm+ level was not supplied.
 *
 *    V7EXT_MsgCode_NO_WSV125
 *       Whole Stem Volume 12.5cm+ was not supplied.
 *
 *    V7EXT_MsgCode_NO_VCU125
 *       Close Utilization Volume 12.5cm+ was not supplied.
 *
 *    V7EXT_MsgCode_NO_VD125
 *       Volume Net Decay 12.5cm+ was not supplied.
 *
 *    V7EXT_MsgCode_NO_VDW125
 *       Volume Net Decay and Waste 12.5cm+ was not supplied.
 *
 *    V7EXT_MsgCode_UTIL_CONSTRAINT
 *       A cross utilization level constraint was violated.
 *
 *    V7EXT_MsgCode_VOL_CONSTRAINT
 *       A cross volume type constraint was violated.
 *
 *    V7EXT_MsgCode_NONPROD_PRIMARY
 *       The primary layer is labelled as Non-Productive and has no stand
 *       description.
 *
 *    V7EXT_MsgCode_LOW_SITE
 *       The stand was unable to grow to a reasonable height within a
 *       reasonable period of time.
 *
 *    V7EXT_MsgCode_PROJECTION_FAILED
 *       The stand projection failed.
 *
 *    V7EXT_MsgCode_TOO_SHORT
 *       The stand did not reach a sufficient height by the target projection
 *       year to generate valid projection values.
 *
 *    V7EXT_MsgCode_DUP_SPCS
 *       A duplicate species was encountered.
 *
 *    V7EXT_MsgCode_YOUNG_OLD_SPCS_MIX
 *       The layer has a mixture of young and older species.  This is not
 *       necessarily an error and will not necessarily be reported each
 *       time it occurs.
 *
 *    V7EXT_MsgCode_NO_SPCS
 *       A required/expected species for a layer was not found.
 *
 *    V7EXT_MsgCode_BAD_STAND_DEFN
 *       A catch all message indicating something was missing or inconsistent
 *       with the stand definition.
 *
 *    V7EXT_MsgCode_AGE_RANGE
 *       Indicates a problem was encountered with the age range of the
 *       projection.
 *
 *    V7EXT_MsgCode_REASSIGNED_SITE
 *       Indicates Site Index was reassigned.
 *
 *    V7EXT_MsgCode_REASSIGNED_HEIGHT
 *       Indicates Input Height was reassigned.
 *
 *
 * Remarks
 * -------
 *
 *    These codes are associated with messages returned from the library
 *    through the 'V7Ext_GetProcessingMessage'.  These are numeric equivalents
 *    to the more descriptive text messages also returned.
 *
 *    The type 'V7ExtMessageCode' is a solution to the problem that
 *    enumerations are not fixed in data type size.  Therefore, any external
 *    access to this data type will be cast into the external data type.
 *
 *    There may be a number of actual text messages associated with each error
 *    code.  Examples of this is the 'V7EXT_MsgCode_VDYP7CORE_MSG'.  This
 *    catch all message code identifies any message generated by the lower
 *    level VDYP7CORE library.
 *
 */


typedef  enum
            {
            V7EXT_MsgCode_FIRST              = 0,

            V7EXT_MsgCode_NONE               = V7EXT_MsgCode_FIRST,
            V7EXT_MsgCode_CORRUPT_CONTEXT,
            V7EXT_MsgCode_VDYP7CORE_MSG,
            V7EXT_MsgCode_NO_BEC,
            V7EXT_MsgCode_BAD_START_MODEL,
            V7EXT_MsgCode_NO_PRIMARY_LAYER,
            V7EXT_MsgCode_NO_CC,
            V7EXT_MsgCode_DEFAULT_CC,
            V7EXT_MsgCode_NO_LH075,
            V7EXT_MsgCode_NO_BA075,
            V7EXT_MsgCode_NO_BA125,
            V7EXT_MsgCode_NO_WSV075,
            V7EXT_MsgCode_NO_WSV125,
            V7EXT_MsgCode_NO_VCU125,
            V7EXT_MsgCode_NO_VD125,
            V7EXT_MsgCode_NO_VDW125,
            V7EXT_MsgCode_UTIL_CONSTRAINT,
            V7EXT_MsgCode_VOL_CONSTRAINT,
            V7EXT_MsgCode_NONPROD_PRIMARY,
            V7EXT_MsgCode_LOW_SITE,
            V7EXT_MsgCode_PROJECTION_FAILED,
            V7EXT_MsgCode_TOO_SHORT,
            V7EXT_MsgCode_DUP_SPCS,
            V7EXT_MsgCode_YOUNG_OLD_SPCS_MIX,
            V7EXT_MsgCode_NO_SPCS,
            V7EXT_MsgCode_BAD_STAND_DEFN,
            V7EXT_MsgCode_AGE_RANGE,
            V7EXT_MsgCode_REASSIGNED_SITE,
            V7EXT_MsgCode_REASSIGNED_HEIGHT,

            V7EXT_MsgCode_LAST               = V7EXT_MsgCode_REASSIGNED_HEIGHT,
            V7EXT_MsgCode_COUNT              = V7EXT_MsgCode_LAST - V7EXT_MsgCode_FIRST + 1,
            V7EXT_MsgCode_DEFAULT            = V7EXT_MsgCode_NONE

            }     V7IntMessageCode;



typedef  SWI32    V7ExtMessageCode;





/*-----------------------------------------------------------------------------
 *
 * V7IntOtherVegType
 * V7ExtOtherVegType
 * =================
 *
 *    Describes other classes of vegetation that may reside on a polygon
 *    that are not trees.
 *
 *
 * Members
 * -------
 *
 *    V7EXT_OtherVeg_FIRST
 *    V7EXT_OtherVeg_LAST
 *    V7EXT_OtherVeg_COUNT
 *    V7EXT_OtherVeg_DEFAULT
 *       Describes the range, number and default valid values for this
 *       enumeration.
 *
 *    V7EXT_OtherVeg_SHRUB
 *    V7EXT_OtherVeg_HERB
 *    V7EXT_OtherVeg_BRYOID
 *       The individual non-tree vegetation covers classes.
 *
 *
 * Remarks
 * -------
 *
 *    The size of 'enum' data types do not have a portable data type
 *    size based on platform or even compiler size.
 *
 *    For this reason, the internal code type (V7IntOtherVegType) will
 *    be cast to the V7ExtOtherVegType.  This data type is guaranteed to
 *    be constant in size across platforms and compilers.
 *
 *    This point is especially important when linking against precompiled
 *    libraries.  It would be tough to link against a 16bit or 32bit
 *    return code without knowing before hand.  This mechanism guarantees
 *    return code size; a 'V7ExtOtherVegType' is always returned.
 *
 */


typedef  enum
            {
            V7EXT_OtherVeg_FIRST         = 0,

            V7EXT_OtherVeg_SHRUB         = V7EXT_OtherVeg_FIRST,
            V7EXT_OtherVeg_HERB,
            V7EXT_OtherVeg_BRYOID,

            V7EXT_OtherVeg_LAST          = V7EXT_OtherVeg_BRYOID,
            V7EXT_OtherVeg_COUNT         = V7EXT_OtherVeg_LAST - V7EXT_OtherVeg_FIRST + 1,
            V7EXT_OtherVeg_DEFAULT       = V7EXT_OtherVeg_SHRUB

            }  V7IntOtherVegType;


typedef  SWI32       V7ExtOtherVegType;




/*-----------------------------------------------------------------------------
 *
 * V7IntNonVegType
 * V7ExtNonVegType
 * ===============
 *
 *    Describes classes of non-vegetative outcroppings that occur on a polygon.
 *
 *
 * Members
 * -------
 *
 *    V7EXT_NonVeg_FIRST
 *    V7EXT_NonVeg_LAST
 *    V7EXT_NonVeg_COUNT
 *    V7EXT_NonVeg_DEFAULT
 *       Describes the range, number and default valid values for this
 *       enumeration.
 *
 *    V7EXT_NonVeg_WATER
 *    V7EXT_NonVeg_EXPOSEDSOIL
 *    V7EXT_NonVeg_BURNEDAREA
 *    V7EXT_NonVeg_ROCK
 *    V7EXT_NonVeg_SNOW
 *    V7EXT_NonVeg_OTHER
 *       The individual non-vegetation outcropping classes.
 *
 *
 * Remarks
 * -------
 *
 *    The size of 'enum' data types do not have a portable data type
 *    size based on platform or even compiler size.
 *
 *    For this reason, the internal code type (V7IntNonVegType) will
 *    be cast to the V7ExtNonVegType.  This data type is guaranteed to
 *    be constant in size across platforms and compilers.
 *
 *    This point is especially important when linking against precompiled
 *    libraries.  It would be tough to link against a 16bit or 32bit
 *    return code without knowing before hand.  This mechanism guarantees
 *    return code size; a 'V7ExtNonVegType' is always returned.
 *
 */


typedef  enum
            {
            V7EXT_NonVeg_FIRST         = 0,

            V7EXT_NonVeg_WATER         = V7EXT_NonVeg_FIRST,
            V7EXT_NonVeg_EXPOSEDSOIL,
            V7EXT_NonVeg_BURNEDAREA,
            V7EXT_NonVeg_ROCK,
            V7EXT_NonVeg_SNOW,
            V7EXT_NonVeg_OTHER,

            V7EXT_NonVeg_LAST          = V7EXT_NonVeg_OTHER,
            V7EXT_NonVeg_COUNT         = V7EXT_NonVeg_LAST - V7EXT_NonVeg_FIRST + 1,
            V7EXT_NonVeg_DEFAULT       = V7EXT_NonVeg_OTHER

            }  V7IntNonVegType;


typedef  SWI32       V7ExtNonVegType;




/*-----------------------------------------------------------------------------
 *
 * V7IntInventoryStandard
 * V7ExtInventoryStandard
 * ======================
 *
 *    Brief Description of what this object represents or contains
 *
 *
 * Members
 * -------
 *
 *    V7EXT_InvStd_FIRST
 *    V7EXT_InvStd_LAST
 *    V7EXT_InvStd_COUNT
 *    V7EXT_InvStd_DEFAULT
 *       Describes the range, number and default valid values for this
 *       enumeration.
 *
 *    V7EXT_InvStd_UNKNOWN
 *       Indicates the inventory standard is not known.  In this case, an
 *       attempt to determine Inventory Standard will be made based on
 *       supplied inventory attributes.
 *
 *    V7EXT_InvStd_FIP
 *       The inventory data was captured using FIP standards.
 *
 *    V7EXT_InvStd_VRI
 *       The inventory data was captured using VRI standards.
 *
 *
 * Remarks
 * -------
 *
 *    The size of 'enum' data types do not have a portable data type
 *    size based on platform or even compiler size.
 *
 *    For this reason, the internal code type (V7IntInventoryStandard) will
 *    be cast to the V7ExtInventoryStandard.  This data type is guaranteed to
 *    be constant in size across platforms and compilers.
 *
 *    This point is especially important when linking against precompiled
 *    libraries.  It would be tough to link against a 16bit or 32bit
 *    return code without knowing before hand.  This mechanism guarantees
 *    return code size; a 'V7ExtInventoryStandard' is always returned.
 *
 */


typedef  enum
            {
            V7EXT_InvStd_FIRST      = 0,

            V7EXT_InvStd_UNKNOWN    = V7EXT_InvStd_FIRST,
            V7EXT_InvStd_SILV,
            V7EXT_InvStd_VRI,
            V7EXT_InvStd_FIP,

            V7EXT_InvStd_LAST       = V7EXT_InvStd_FIP,
            V7EXT_InvStd_COUNT      = V7EXT_InvStd_LAST - V7EXT_InvStd_FIRST + 1,
            V7EXT_InvStd_DEFAULT    = V7EXT_InvStd_VRI

            }  V7IntInventoryStandard;



typedef  SWI32       V7ExtInventoryStandard;





/*-----------------------------------------------------------------------------
 *
 * V7IntLayerSummarizationMode
 * V7ExtLayerSummarizationMode
 *===========================
 *
 *    Indicates the layer summarization mode used to combine layers into the
 *    specific VDYP7 model.
 *
 *
 * Members
 * -------
 *
 *    V7EXT_LayerSummMode_FIRST
 *    V7EXT_LayerSummMode_LAST
 *    V7EXT_LayerSummMode_COUNT
 *    V7EXT_LayerSummMode_DEFAULT
 *       Describes the range, number and default valid values for this
 *       enumeration.
 *
 *    V7EXT_LayerSummMode_UNKNOWN
 *       An unknown layer summarization mode was employed.  This should never
 *       occur or should be used as a initialization value.
 *
 *    V7EXT_LayerSummMode_Rank1Only
 *       The layer labelled or determined to be the Rank 1 layer is the only
 *       layer processed.
 *
 *       This processing mode is no longer used and was replaced by
 *       2 Layer Processing.
 *
 *    V7EXT_LayerSummMode_2Layer
 *       Describes the Two layer Processing as described in IPSCB460
 *
 *
 * Remarks
 * -------
 *
 *    The size of 'enum' data types do not have a portable data type
 *    size based on platform or even compiler size.
 *
 *    For this reason, the internal code type (V7IntInventoryStandard) will
 *    be cast to the V7ExtInventoryStandard.  This data type is guaranteed to
 *    be constant in size across platforms and compilers.
 *
 *    This point is especially important when linking against precompiled
 *    libraries.  It would be tough to link against a 16bit or 32bit
 *    return code without knowing before hand.  This mechanism guarantees
 *    return code size; a 'V7ExtInventoryStandard' is always returned.
 *
 */


typedef  enum
            {
            V7EXT_LayerSummMode_FIRST      = 0,

            V7EXT_LayerSummMode_UNKNOWN    = V7EXT_LayerSummMode_FIRST,
            V7EXT_LayerSummMode_Rank1Only,
            V7EXT_LayerSummMode_2Layer,

            V7EXT_LayerSummMode_LAST       = V7EXT_LayerSummMode_2Layer,
            V7EXT_LayerSummMode_COUNT      = V7EXT_LayerSummMode_LAST - V7EXT_LayerSummMode_FIRST + 1,
            V7EXT_LayerSummMode_DEFAULT    = V7EXT_LayerSummMode_UNKNOWN

            }  V7IntLayerSummarizationMode;



typedef  SWI32       V7ExtLayerSummarizationMode;




/*-----------------------------------------------------------------------------
 *
 * V7IntSpeciesIndex
 * V7ExtSpeciesIndex
 * =================
 *
 *    Enumerated the range of possible species indices within a layer.
 *
 *
 * Members
 * -------
 *
 *    V7EXT_SpcsNdx_FIRST
 *    V7EXT_SpcsNdx_LAST
 *    V7EXT_SpcsNdx_COUNT
 *       Identifies the range of valid species indices.
 *
 *    V7EXT_SpcsNdx_DEFAULT
 *       If a default index is required, use this.
 *
 *    V7EXT_SpcsNdx_1
 *    V7EXT_SpcsNdx_2
 *    V7EXT_SpcsNdx_3
 *    V7EXT_SpcsNdx_4
 *    V7EXT_SpcsNdx_5
 *    V7EXT_SpcsNdx_6
 *       The valid species indices.
 *
 *
 * Remarks
 * -------
 *
 *    The size of 'enum' data types do not have a portable data type
 *    size based on platform or even compiler size.
 *
 *    For this reason, the internal code type (V7IntSpeciesIndex) will
 *    be cast to the V7ExtSpeciesIndex.  This data type is guaranteed to
 *    be constant in size across platforms and compilers.
 *
 *    This point is especially important when linking against precompiled
 *    libraries.  It would be tough to link against a 16bit or 32bit
 *    return code without knowing before hand.  This mechanism guarantees
 *    return code size; a 'V7ExtSpeciesIndex' is always returned.
 *
 */


typedef  enum
            {
            V7EXT_SpcsNdx_FIRST     = 0,

            V7EXT_SpcsNdx_1         = V7EXT_SpcsNdx_FIRST,
            V7EXT_SpcsNdx_2,
            V7EXT_SpcsNdx_3,
            V7EXT_SpcsNdx_4,
            V7EXT_SpcsNdx_5,
            V7EXT_SpcsNdx_6,

            V7EXT_SpcsNdx_LAST      = V7EXT_SpcsNdx_6,
            V7EXT_SpcsNdx_COUNT     = V7EXT_SpcsNdx_LAST - V7EXT_SpcsNdx_FIRST + 1,
            V7EXT_SpcsNdx_DEFAULT   = V7EXT_SpcsNdx_FIRST

            }  V7IntSpeciesIndex;


typedef  SWI32    V7ExtSpeciesIndex;




/*-----------------------------------------------------------------------------
 *
 * V7IntSpeciesSorting
 * V7ExtSpeciesSorting
 * ===================
 *
 *    Identifies the different collating mechanisms an array of species
 *    may be sorted.
 *
 *
 * Members
 * -------
 *
 *    V7EXT_SpcsSort_AS_SUPPLIED
 *       Identifies the ordering in which the species were originally
 *       supplied into the layer.
 *
 *    V7EXT_SpcsSort_BY_PERCENT
 *       Identifies the ordering where the species are ordered in decresing
 *       percent and ties are ordered in increasing alphabetical ordering.
 *
 *    V7EXT_SpcsSort_BY_NAME
 *       Identifies the ordering where the species are ordered in increasing
 *       alphabetical names.
 *
 */


typedef  enum
            {
            V7EXT_SpcsSort_FIRST            = 0,

            V7EXT_SpcsSort_AS_SUPPLIED      = V7EXT_SpcsSort_FIRST,
            V7EXT_SpcsSort_BY_PERCENT,
            V7EXT_SpcsSort_BY_NAME,

            V7EXT_SpcsSort_LAST             = V7EXT_SpcsSort_BY_NAME,
            V7EXT_SpcsSort_COUNT            = V7EXT_SpcsSort_LAST - V7EXT_SpcsSort_FIRST + 1,
            V7EXT_SpcsSort_DEFAULT          = V7EXT_SpcsSort_BY_PERCENT

            }  V7IntSpeciesSorting;


typedef  SWI32    V7ExtSpeciesSorting;





/*-----------------------------------------------------------------------------
 *
 * V7EXT_MAX_NUM_LAYERS_PER_POLYGON
 * V7EXT_MAX_NUM_SPECIES_PER_LAYER
 * ================================
 *
 *    Identifies a number of public constants important to outside
 *    applications.
 *
 *
 * Members
 * -------
 *
 *    V7EXT_MAX_NUM_LAYERS_PER_POLYGON
 *       Specifies the maximum number of layers that can be encountered within
 *       a single polygon.
 *
 *       As there are defined maximums in the MoF Standards, there is no need
 *       to define a dynamic data structure to handle an arbitrary number of
 *       layers.
 *
 *    V7EXT_MAX_NUM_SPECIES_PER_LAYER
 *       The maximum number of species that can be added to a single layer
 *       within a polygon.
 *
 */


#define  V7EXT_MAX_NUM_LAYERS_PER_POLYGON             (9)
#define  V7EXT_MAX_NUM_SPECIES_PER_LAYER              (V7EXT_SpcsNdx_COUNT)





/*-----------------------------------------------------------------------------
 *
 * V7IntInterfaceOption
 * V7ExtInterfaceOption
 * ====================
 *
 *    Identifies processing, configuration or other options that can be
 *    applied to the VDYP7Interface.
 *
 *
 * Members
 * -------
 *
 *    V7EXT_Option_FIRST
 *    V7EXT_Option_LAST
 *    V7EXT_Option_COUNT
 *			These values provide a means of enumerating through all possible
 *       options and provide a readily available count of all options.
 *
 *    V7EXT_Option_EnableBackGrow
 *       Backgrow are the computations that "shrink" a stand over time prior
 *       to its reference year.
 *
 *       If enabled, the BackGrow option will occur if other business rules
 *       allow it to happen.  If disabled, then BackGrow will definitely not
 *       happen.
 *
 *       The default is to allow BackGrow operations.
 *
 *    V7EXT_Option_EnableForwardGrow
 *       ForwardGrow are the computations that "grow" a stand over time at
 *       and after the stands reference year.
 *
 *       If enabled, the ForwardGrow option will occur if other business
 *       rules allow it to happen.  If disabled, then ForwardGrow will
 *       definitely not occur.
 *
 *       The default is to allow ForwardGrow operations.
 *
 *    V7EXT_Option_AllowBATPHSubstitution
 *       Provide support for enabling/disabling the substitution of Basal Area
 *       and TPH in situations where the projected stand is not viable but the
 *       BA and TPH should exist given the stand age.
 *
 *
 * Remarks
 * -------
 *
 *    The size of 'enum' data types do not have a portable data type
 *    size based on platform or even compiler size.
 *
 *    For this reason, the internal code type (V7IntInterfaceOption) will
 *    be cast to the V7ExtInterfaceOption.  This data type is guaranteed to
 *    be constant in size across platforms and compilers.
 *
 *    This point is especially important when linking against precompiled
 *    libraries.  It would be tough to link against a 16bit or 32bit
 *    return code without knowing before hand.  This mechanism guarantees
 *    return code size; a 'V7ExtInterfaceOption' is always returned.
 *
 *    IMPORTANT!!
 *    Changes to 'C' V7IntInterfaceOption enumeration MUST be mirrored in 
 *    the corresponding Visual Basic enumeration enumV7ExtInterfaceOption.
 *
 */

typedef  enum
            {
            V7EXT_Option_FIRST            = 0,

            V7EXT_Option_EnableBackGrow   = V7EXT_Option_FIRST,
            V7EXT_Option_EnableForwardGrow,
            V7EXT_Option_AllowBATPHSubstitution,

            V7EXT_Option_LAST             = V7EXT_Option_AllowBATPHSubstitution,
            V7EXT_Option_COUNT            = V7EXT_Option_LAST - V7EXT_Option_FIRST + 1

            }  V7IntInterfaceOption;


typedef  SWI32    V7ExtInterfaceOption;




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
 * V7Ext_Version
 * V7Ext_VB_Version
 * v7ext_for_version_
 * ==================
 *
 *    Returns the current version of this DLL.
 *
 *
 * Parameters
 * ----------
 *
 *    versionBuf (VB, FORTRAN Versions only)
 *       The buffer into which the version string is to be placed.
 *       Must not be NULL
 *
 *    bufferLen  (VB, FORTRAN Versions only)
 *       Input:  The maximum length of the 'buffer' to store data.
 *               (The input value is not used for the FORTRAN interface)
 *       Output: The actual amount of version string data stored in 'buffer'.
 *
 *    inputLen   (FORTRAN Version only)
 *       The maximum length of the input buffer.
 *
 *
 * Return Value
 * ------------
 *
 *    An internal constant buffer containing the current version of this
 *    library
 *
 *
 * Remarks
 * -------
 *
 *    Version strings are of the form:
 *
 *          "VV.vva.1234"
 *
 *    Where:
 *          VV    major version number
 *          vv    minor version number
 *          a     revision number
 *          1234  strictly increasing build number.
 *
 *    When supplying a buffer for the VB and FORTRAN interfaces, a buffer of at
 *    least 12 bytes in length (11 for the maximum version length, 1 for a null
 *    byte terminator).
 *
 *    The constant 'V7EXT_MIN_VERSION_STRING_BUF_LEN' defines this minimum
 *    buffer length.
 *
 *    Each component of the version string may not consist of its full length.
 *    For instance, a version string of "7.1a.32" could be returned.
 *
 */


SWChar const *    ENV_IMPORT_STDCALL     V7Ext_Version( void );

void              ENV_IMPORT_STDCALL     V7Ext_VB_Version( SWChar *    sBuffer,
                                                           SWI32 *     iBufLen );

void              ENV_IMPORT_STDCALL     v7ext_for_version_( SWChar *   sBuffer,
                                                             SWI32 *    iBufLen,
                                                             SWU32      iInputLen );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_Initialize
 *	================
 *
 *		Initialize the VDYP7 Extended Core Modules Library.
 *
 *
 *	Parameters
 *	----------
 *
 *    logContext
 *       The logging context to use to dump error, warning, tracing debugging,
 *       messages.
 *       May be NULL_LOG_CONTEXT
 *
 *    logContextConfigFile
 *       The name of the logging configuration file to use to define a logging
 *       context if 'logContext' is NULL_LOG_CONTEXT.
 *       May be NULL or "".
 *       
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully initialized the library.
 *
 *
 *	Remarks
 *	-------
 *
 *    This routine must be called prior to any other routines
 *    in this library except for the 'Version' related routines.
 *
 *		This routine does not also initialize the VDYP7CORE library.
 *    The VDYP7CORE library must be initialize separately and prior
 *    to this library.
 *
 *    If both 'logContext' is NULL_LOG_CONTEXT and 'logContextConfigFile'
 *    is NULL or "", then no logging will be performed.
 *
 */

V7ExtReturnCode    ENV_IMPORT_STDCALL
V7Ext_Initialize( LogCntxt          logContext,
                  SWChar const *    logContextConfigFile );





/*-----------------------------------------------------------------------------
 *
 * V7Ext_Shutdown
 * ==============
 *
 *    Shuts down the VDYP7 Extended Core Modules Library.
 *
 *
 * Remarks
 * -------
 *
 *    After calling this routine, 'V7Ext_Initialize' must be called prior
 *    to reusing this library.
 *
 */


void  ENV_IMPORT_STDCALL  V7Ext_Shutdown();




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_AllocatePolygonDescriptor
 * V7Ext_VB_AllocatePolygonDescriptor
 * v7ext_for_allocatepolygondescriptor_
 *	====================================
 *
 *		Creates a polygon descriptor for use with this library.
 *
 *
 *	Return Value
 *	------------
 *
 *		A handle to a new polygon descriptor.
 *    V7EXT_INVALID_POLYGON_DESCRIPTOR if there is an error.
 *
 *
 *	Remarks
 *	-------
 *
 *		This descriptor must be allocated prior to use with any of the other
 *    routines in this library.
 *
 *    A single descriptor can be resused for any number of polygons.  There
 *    is no need to continually allocate new descriptors for each polygon.
 *
 *    Any number of these descriptors may exist at any one time.
 *
 *    Each descriptor must be deallocated with a call to the deallocate
 *    routine.
 *
 */


V7ExtPolygonHandle   ENV_IMPORT_STDCALL  V7Ext_AllocatePolygonDescriptor();


SWI32                ENV_IMPORT_STDCALL  V7Ext_VB_AllocatePolygonDescriptor();


SWI32                ENV_IMPORT_STDCALL  v7ext_for_allocatepolygondescriptor_();




/*-----------------------------------------------------------------------------
 *
 * V7Ext_FreePolygonDescriptor
 * V7Ext_VB_FreePolygonDescriptor
 * v7ext_for_freepolygondescriptor_
 * ================================
 *
 *    Frees up resources held by a polygon descriptor.
 *
 *
 * Parameters
 * ----------
 *
 *    polygonDescriptor
 *       The polygon descriptor to be free'd up.
 *
 *
 * Remarks
 * -------
 *
 *    Each polygon descriptor allocated by 'V7Ext_AllocatePolygonDescriptor'
 *    must be deallocated by this routine.
 *
 */


void  ENV_IMPORT_STDCALL  V7Ext_FreePolygonDescriptor( V7ExtPolygonHandle polygonDescriptor );

void  ENV_IMPORT_STDCALL  V7Ext_VB_FreePolygonDescriptor( SWI32 polygonDescriptor );

void  ENV_IMPORT_STDCALL  v7ext_for_freepolygondescriptor_( SWI32 polygonDescriptor );




/*-----------------------------------------------------------------------------
 *
 * V7Ext_ReturnCodeToString
 * V7Ext_VB_ReturnCodeToString
 * ===========================
 *
 *    Converts a return code to a null terminated string.
 *
 *
 * Parameters
 * ----------
 *
 *    buffer     (VB Version only)
 *       The buffer into which the string is to be placed.
 *       Must not be NULL
 *
 *    bufferLen  (VB Version only)
 *       Input:  The maximum length of the 'buffer' to store data.
 *       Output: The actual amount of version string data stored in 'buffer'.
 *
 *    rtrnCode
 *       The return code to be converted to a string.
 *
 *
 * Return Value
 * ------------
 *
 *    The null terminated string corresponding to the return code.
 *
 *
 * Remarks
 * -------
 *
 *    For VB, the buffer length should be at least 64 characters in size.
 *
 */


SWChar const * ENV_IMPORT_STDCALL
V7Ext_ReturnCodeToString( V7ExtReturnCode rtrnCode );


void     ENV_IMPORT_STDCALL
V7Ext_VB_ReturnCodeToString( SWChar *     versionBuf,
                             SWI32 *      bufferLen,
                             SWI32        rtrnCode );






/*-----------------------------------------------------------------------------
 *
 * V7Ext_GrowthModelToString
 * V7Ext_VB_GrowthModelToString
 * ============================
 *
 *    Converts the supplied growth model to a string.
 *
 *
 * Parameters
 * ----------
 *
 *		buffer     (VB Version only)
 *			The buffer into which the string is to be placed.
 *       Must not be NULL
 *
 *    bufferLen  (VB Version only)
 *       Input:  The maximum length of the 'buffer' to store data.
 *       Output: The actual amount of version string data stored in 'buffer'.
 *
 *		iGrowthModel
 *			The growth model to be converted into a string.
 *
 *       This value is actually of type 'enumGrowthModel' but because of the
 *       varying size of enumerated types between varying platforms and
 *       compilers, this data type has been cast to a fixed size integer.
 *
 *
 *	Return Value
 *	------------
 *
 *		The string corresponding to the supplied growth model.
 *
 */


SWChar const *    ENV_IMPORT_STDCALL
V7Ext_GrowthModelToString( V7ExtGrowthModel     iGrowthModel );


void     ENV_IMPORT_STDCALL
V7Ext_VB_GrowthModelToString( SWChar *    buffer,
                              SWI32 *     bufferLen,
                              SWI32       iGrowthModel );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_ProcessingModeToString
 * V7Ext_VB_ProcessingModeToString
 *	===============================
 *
 *		Converts the supplied processing mode to a string.
 *
 *
 *	Parameters
 *	----------
 *
 *		buffer     (VB Version only)
 *			The buffer into which the string is to be placed.
 *       Must not be NULL
 *
 *    bufferLen  (VB Version only)
 *       Input:  The maximum length of the 'buffer' to store data.
 *       Output: The actual amount of version string data stored in 'buffer'.
 *
 *		iGrowthModel
 *			The growth model identifying the processing mode class to be
 *       converted.
 *
 *       This value is actually of type 'enumGrowthModel' but because of the
 *       varying size of enumerated types between varying platforms and
 *       compilers, this data type has been cast to a fixed size integer.
 *
 *    iProcessingMode
 *       The processing mode within the specified Growth Model class.
 *
 *       This value is actually of type 'enumProcessingMode' but because of the
 *       varying size of enumerated types between varying platforms and
 *       compilers, this data type has been cast to a fixed size integer.
 *
 *
 *	Return Value
 *	------------
 *
 *		The string corresponding supplied growth model/processing mode.
 *
 *
 *	Remarks
 *	-------
 *
 *		Because of the overlap of the processing modes between the growth
 *    models, the growth model must also be supplied to uniquely identify the
 *    correct processing mode we are interested in.
 *
 */


SWChar const *    ENV_IMPORT_STDCALL
V7Ext_ProcessingModeToString( V7ExtGrowthModel     iGrowthModel,
                              V7ExtProcessingMode  iProcessingMode );


void              ENV_IMPORT_STDCALL
V7Ext_VB_ProcessingModeToString( SWChar * buffer,
                                 SWI32 *  bufferLen,
                                 SWI32    iGrowthModel,
                                 SWI32    iProcessingMode );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_LogPolygonDescriptor
 *	==========================
 *
 *		Dumps the polygon descriptor to the internal file stream.
 *
 *
 *	Parameters
 *	----------
 *
 *    logger
 *       The logger to dump the polygon descriptor to.
 *       If NULL_LOGGER, this routine will supply its own logger.
 *
 *    priority
 *       The log message priority to dump this descriptor at.
 *
 *    lineNo
 *       The line number of the originating request.
 *       If -1, the line within this routine is used.
 *       Ignored if the 'logger' is not supplied.
 *
 *    indent
 *       The number of additional spaces to indent each message.
 *
 *    headerMsg
 *       (Optional) A message to be displayed with the polygon dump.
 *
 *    polygonDescriptor
 *       The polygon descriptor to be dumped to the diagnostic file.
 *
 *
 *	Remarks
 *	-------
 *
 *    Dumps a formatted version of the polygon descriptor to an internal
 *    file specified in the 'V7Ext_Initialize' routine.
 *
 */


void  ENV_IMPORT_STDCALL
V7Ext_LogPolygonDescriptor( Logger              logger,
                            LogMsgPriority      priority,
                            SWI32               lineNo,
                            SWI32               indent,
                            SWChar const *      headerMsg,
                            V7ExtPolygonHandle  polygonDescriptor );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_StartNewPolygon
 *	=====================
 *
 *		Starts a new polygon in the supplied polygon handle.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle to start a new polygon within.
 *       This handle must have previously been allocated with a call
 *       to 'V7Ext_AllocatePolygonDescriptor'.
 *
 *    sDistrict
 *       The map district responsible for the polygon.
 *       Maximum length defined by: V7EXT_MIN_DISTRICT_BUF_LEN
 *
 *    sMapSheet
 *       The map sheet of the polygon.
 *       Maximum length defined by: V7EXT_MIN_MAPSHEET_BUF_LEN
 *
 *    sMapQuad
 *       The map quad of the polygon.
 *       Maximum length defined by: V7EXT_MIN_MAPQUAD_BUF_LEN
 *
 *    sMapSubQuad
 *       The map sub-quad of the polygon.
 *       Maximum length defined by: V7EXT_MIN_MAPSUBQUAD_BUF_LEN
 *
 *    iPolyNum
 *       The polygon number within the map sheet.
 *
 *    iInventoryStandard
 *       The inventory standard at which the invetory data was captured.
 *
 *    iReferenceYear
 *       The year the polygon information is based on.
 *
 *    iYearOfDeath
 *       In the event of a significant kill of the stand, this parameter
 *       supplies the year in which the stand kill occurred.  This would
 *       normally be paired with the 'fPctStockableDead' parameter.
 *
 *       -9 indicates no stand kill has occurred.
 *
 *    sFIZ
 *       The Forest Inventory Zone of the polygon.
 *
 *    sBEC
 *       The BEC Zone of the polygon.
 *
 *    iCFSEcoZone
 *       Indicates the CFS EcoZone associated with the polygon (if known).
 *       If the CFS EcoZone is not known, supply V7EXT_cfsEco_UNKNOWN (-9).
 *
 *    fPctStockableLand
 *       The precent stockable land of the polygon.
 *
 *    fPctStockableDead
 *       Represents the percent of the stockable land consisting of dead stems
 *       (presumably due to an insect attack).  This value ranges from 0 to 100
 *       is the proportion of the stockable area that was killed.  
 *       This parameter would normally be paired with the 'iYearOfDeath' 
 *       parameter.
 *
 *       -9.0 if not known or there has been no kill of the stand.
 *
 *    sNonProdDescriptor
 *       The non productive descriptor of the polygon.
 *
 *    fYieldFactor
 *       The multiplier for the volumes to adjust by.
 *       If not known or if an internal factor is to be supplied, use -9.0.
 *       Any other value between 0.0 and 1.0 inclusive will be used as is
 *       without calculating an internal yield factor.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully set the new polygon information.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters are invalid, inconsistent or missing.
 *
 *
 *	Remarks
 *	-------
 *
 *		Any existing polygon information that may have been there will be
 *    reset with a call to this routine.
 *
 *    2004/11/17:
 *    Added a check to ensure the measurement year represents a valid year.
 *    The polygon will be rejected if it does not.  Refer to Cam's Nov. 9, 2004
 *    e-mail for details.
 *
 *    2005/11/25:
 *    Extended the allowable range for a yield factor to be between
 *    0.0 and 10.0 from 0.0 and 1.0
 *
 *    2007/11/17:
 *    Trap for the new (and unsupported) BEC Codes: BAFA, CMA, IMA and
 *    translate them to AT.
 *
 *    2015/10/07: 00110
 *    Added the ability to supply Year of Death and Pct Stockable Dead 
 *    attributes into the polygon definition.
 *
 *    2017/06/28: VDYP-11
 *    Added the ability to supply an optional explicit CFS Eco Zone with the 
 *    definition of the polygon.
 *
 */

V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_StartNewPolygon( V7ExtPolygonHandle       polyHandle,
                       SWChar const *           sDistrict,
                       SWChar const *           sMapSheet,
                       SWChar const *           sMapQuad,
                       SWChar const *           sMapSubQuad,
                       SWU32 const              iPolyNum,
                       V7ExtInventoryStandard   iInventoryStandard,
                       SWU32 const              iReferenceYear,
                       SWI32 const              iYearOfDeath,
                       SWChar const *           sFIZ,
                       SWChar const *           sBEC,
                       V7ExtCFSEcoZone          iCFSEcoZone,
                       SWF32 const              fPctStockableLand,
                       SWF32 const              fPctStockableDead,
                       SWChar const *           sNonProdDescriptor,
                       SWF32 const              fYieldFactor );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_SetReportingUtilLevel
 *	===========================
 *
 *		Set the reporting utilization level for all species to a particular
 *    utilization level.
 *
 *
 *	Parameters
 *	----------
 *
 *    polyHandle
 *       The polygon handle for which you wish to set the reporting utilization
 *       for a particular VDYP7 species.
 *
 *    fUtilLvl
 *       The reporting utilization level to set.  This value must be a
 *       recognized utilization such as: 4.0, 7.5, 12.5, 17.5, or 22.5
 *
 *       -9.0 indicates that projected volumes and other attributes for that
 *       species are to be ignored and treated as zero.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       The association of species to utilization level was made.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters were not supplied.
 *
 *    V7EXT_ERR_INVALIDUTILLEVEL
 *       The specified utilization level did not match up to one of the
 *       allowed utilization levels.
 *
 *
 *	Remarks
 *	-------
 *
 *		If the routine is not successful, no changes will be made.
 *
 *    Once an assignment is set, all subsequent runs of stand models or
 *    reloads of projection data will use the new assignment.
 *
 *    Any particular species may have its reporting level set any number of
 *    times.
 *
 *    When this library is initialized, all species will be set to a valid
 *    default utilization level.  Calls to this routine will override this
 *    default value.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_SetReportingUtilLevel( V7ExtPolygonHandle    polyHandle,
                             SWF32                 fUtilLvl );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_SetSpcsReportingUtilLevel
 *	===============================
 *
 *		Set the reporting utilization level for a particular VDYP7 species.
 *
 *
 *	Parameters
 *	----------
 *
 *    polyHandle
 *       The polygon handle for which you wish to set the reporting utilization
 *       for a particular VDYP7 species.
 *
 *		sSpcs
 *			The species for which you wish to set the reporting utilization
 *       level.  This may be any species recognized by the Site Tools library.
 *
 *    fUtilLvl
 *       The reporting utilization level to set.  This value must be a
 *       recognized utilization such as: 4.0, 7.5, 12.5, 17.5, or 22.5
 *
 *       -9.0 indicates that projected volumes and other attributes for that
 *       species are to be ignored and treated as zero.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       The association of species to utilization level was made.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters were not supplied.
 *
 *    V7EXT_ERR_INVALIDSPECIES
 *       The supplied species was not recognized as a valid commercial
 *       species.
 *
 *    V7EXT_ERR_INVALIDUTILLEVEL
 *       The specified utilization level did not match up to one of the
 *       allowed utilization levels.
 *
 *
 *	Remarks
 *	-------
 *
 *		If the routine is not successful, no changes will be made.
 *
 *    Once an assignment is set, all subsequent runs of stand models or
 *    reloads of projection data will use the new assignment.
 *
 *    Any particular species may have its reporting level set any number of
 *    times.
 *
 *    Setting the reporting level of a species will simulataneously set the
 *    reporting level for all species that are associated with the same VDYP7
 *    species.
 *
 *    When this library is initialized, all species will be set to a valid
 *    default utilization level.  Calls to this routine will override this
 *    default value.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_SetSpcsReportingUtilLevel( V7ExtPolygonHandle    polyHandle,
                                 SWChar const *        sSpcs,
                                 SWF32                 fUtilLvl );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetSpcsReportingUtilLevel
 *	===============================
 *
 *		Returns the current reporting utilization level for a particular species.
 *
 *
 *	Parameters
 *	----------
 *
 *    polyHandle
 *       The polygon handle for which you wish to request the reporting
 *       utilization for a particular species.
 *
 *		sSpcs
 *			The species for which you wish to query the reporting
 *       utilization level.  This species must be one of the species
 *       recognized by the SiteTools library.
 *
 *
 *	Return Value
 *	------------
 *
 *		The utilization level appropriate to that species.
 *    0.0 indicates the 'exclude' utilization level.
 *
 *    (SWF32)  V7EXT_ERR_INTERNALERROR
 *       The internal utilization level was not recognized.
 *       This should never happen and indicates an internal logic error.
 *
 *    (SWF32)  V7EXT_ERR_INVALIDPARAMETER
 *       Indicates one or more of the supplied parameters are invalid or
 *       missing.
 *
 *    (SWF32)  V7EXT_ERR_INVALIDSPECIES
 *       Indicates the species was not recognized
 *
 *
 *	Remarks
 *	-------
 *
 *		All SP0 species are set to a default utilization level when the
 *    library is initialized.
 *
 *    Utilization levels are set to new values with calls to:
 *       'V7Ext_SetSpcsReportingUtilLevel'
 *
 *    The assignment of a reporting utilization level to a particular
 *    species will simulataneously assign the same reporting level to
 *    any species with the same VDYP7 species.
 *
 */


SWF32    ENV_IMPORT_STDCALL
V7Ext_GetSpcsReportingUtilLevel( V7ExtPolygonHandle    polyHandle,
                                 SWChar const *        sSpcs );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetSpcsMoFBiomassUtilLevel
 *	================================
 *
 *		Return the Utilization Level a particular species should be projected at
 *    when requesting MoF Biomass values.
 *
 *
 *	Parameters
 *	----------
 *
 *		sSpcs
 *			The species name for which you wish to get the MoF Biomass utilization
 *       level to project that species at.
 *
 *
 *	Return Value
 *	------------
 *
 *		The specific Projection Utilization Levels that should be used when 
 *    projecting for a specific species.
 *
 *    -9.0 if the species was not recognized.
 *
 *
 *	Remarks
 *	-------
 *
 *		As per documentation for the MoF Biomass calculations, MoF Biomass
 *    should be calculated using the following utilization levels:
 *
 *       All Species:          4.0 cm+
 *
 *    The output of this routine can be used as an input to the routine:
 *    'V7Ext_SetSpcsReportingUtilLevel'
 *
 *    These utilization levels are only required when CFS Biomass output
 *    is desired.  The model for converting Projected Volumes to CFS Biomass
 *    relies on these Utilization Levels being used.
 *
 *    While this routine currently returns a constant value, it is included
 *    for future expansion when specific species utilization levels are
 *    required.
 *
 */

SWF32    ENV_IMPORT_STDCALL
V7Ext_GetSpcsMoFBiomassUtilLevel( SWChar const *     sSpcs );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetSpcsCFSBiomassUtilLevel
 *	================================
 *
 *		Return the Utilization Level a particular species should be projected at
 *    when requesting CFS Biomass values.
 *
 *
 *	Parameters
 *	----------
 *
 *		sSpcs
 *			The species name for which you wish to get the CFS Biomass utilization
 *       level to project that species at.
 *
 *
 *	Return Value
 *	------------
 *
 *		The specific Projection Utilization Levels that should be used when 
 *    projecting for a specific species.
 *
 *    -9.0 if the species was not recognized.
 *
 *
 *	Remarks
 *	-------
 *
 *		As per documentation for the CFS Biomass calculations, CFS Biomass
 *    should be calculated using the following utilization levels:
 *
 *       All Hardwoods:          12.5 cm+
 *       All Pine:               12.5 cm+
 *       All Other Conifers:     17.5 cm+
 *
 *    The output of this routine can be used as an input to the routine:
 *    'V7Ext_SetSpcsReportingUtilLevel'
 *
 *    These utilization levels are only required when CFS Biomass output
 *    is desired.  The model for converting Projected Volumes to CFS Biomass
 *    relies on these Utilization Levels being used.
 *
 */

SWF32    ENV_IMPORT_STDCALL
V7Ext_GetSpcsCFSBiomassUtilLevel( SWChar const *     sSpcs );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_AddNonVegetationInfo
 *	==========================
 *
 *		Add information regarding the non-vegetated areas of the polygon.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle into which to add the non-vegetation information.
 *
 *    iNonVegetationType
 *       The type of non-vegetation being added to the polygon.
 *
 *    fPolygonPercent
 *       The percent of the polygon being covered by this type of
 *       non-vegetation.
 *
 *       If not known, supply a value of -9.0 and it will be given a default
 *       value.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully added the non-vegetation information to the polygon.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters were missing or invalid.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon is no longer being defined.  Once some processing
 *       action has occurred, it is no longer valid to change the definition
 *       of the polygon.
 *
 *    V7EXT_ERR_PERCENTNOT100
 *       Indicates that the supplied percent would exceed 100 for the
 *       different types of other vegetation types.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_AddNonVegetationInfo( V7ExtPolygonHandle  polyHandle,
                            V7ExtNonVegType     iNonVegetationType,
                            SWF32               fPolygonPercent );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_AddOtherVegetationInfo
 *	============================
 *
 *		Supplies information regarding other forms of vegetative cover
 *    associated with the polygon.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle to which you wish to add the Vegetative Info
 *       too.
 *
 *    iOtherVegType
 *       The type of vegetative cover type to be added to the polygon.
 *
 *    fVegPercent
 *       The percent of the polygon area covered by this vegetation type.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully added the vegetation information to the polygon.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters were not supplied or are not valid
 *       or the supplied percent is not valid (< 0 or > 100).
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon definition has already been finalized and/or processed.
 *       Once we get to this point, we can no longer change the definition
 *       of the polygon.
 *
 *    V7EXT_ERR_PERCENTNOT100
 *       Indicates that the supplied percent would exceed 100 for the
 *       different types of other vegetation types.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_AddOtherVegetationInfo( V7ExtPolygonHandle   polyHandle,
                              V7ExtOtherVegType    iOtherVegType,
                              SWF32                fVegPercent );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_AddLayer
 *	==============
 *
 *		Add a layer containing stand information to the current polygon.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle to add the layer to.
 *
 *    sLayerID
 *       The layer identifier you wish to add.
 *       This code must be included.
 *
 *    sTargetVDYP7Layer
 *       The VDYP7 layer this layer should be targeted at.  This string
 *       must take on one of the following values:
 *
 *          "P"   - The layer will be processed as the VDYP7 Primary Layer
 *          "V"   - The layer will be processed as the VDYP7 Veteran Layer
 *          "D"   - The layer will be processed as the VDYP7 Dead Layer
 *          " "
 *          ""
 *          NULL  - The layer will not be targeted to a particular VDYP7
 *                  layer.  See the processing rules outlined below on the
 *                  final disposition of a layer with this code.
 *
 *    sRankCode
 *       The rank of this layer.  Only one layer can be labelled as rank "1"
 *       indicating the primary layer in a single polygon.  Other layers can
 *       be labelled (or not labelled) as desired.  It is also legal to not
 *       label any layer as being rank 1.
 *
 *       This parameter can be NULL or "" if the rank is not known.
 *
 *    sNonForestDescriptor
 *       Indicates any non-forest descriptor for the layer.  Individual
 *       layers may be considered non-forested while others remain forested.
 *       This may be because of recent logging and re-growth has not occurred
 *       yet.
 *
 *       If the layer is forested or if the non-forest code is not known,
 *       supply NULL or a zero length string.
 *
 *       The Non-Forest Descriptor is interpreted as per IPSCB206.
 *
 *    fMeasuredUtilLevel
 *       The utilization level the layer attributes were measured at.
 *       Currently, this parameter is ignored and always assumed to be 7.5cm.
 *       The caller should always supply 7.5 for this parameter.
 *
 *    fLayerPctStk
 *       The amount of the polygon stockability attributed to this layer
 *       expressed in terms of the entire polygon area (and not in terms of
 *       the polygon's stockability).  Therefore, this percentage, if supplied
 *       must never exceed the polygon's stockability (if it is known).
 *
 *       Ranges in value from 0 to 100.
 *       -9.0 if this value is not known.
 *
 *       IMPORTANT: This parameter is not currently used.  Always supply -9.0
 *                  for this parameter when creating a new layer.
 *
 *    fCC
 *       The crown closure of the layer.
 *       If not known, supply -9.0
 *
 *    fBA
 *       The basal area at the measured utilization level for this layer.
 *       If not known, supply -9.0
 *
 *    fTPH
 *       The Trees per Hectare at the measured utilization level for this
 *       layer.  If not known, supply -9.0
 *
 *    sEstimatedSISpcs
 *       The species code to which the Estimated SI is associated.  If the
 *       species is not known, this parameter should be NULL or "", in which
 *       case the the Estimated SI will assume to apply to the leading
 *       species for the layer (to be supplied later with a call to
 *       'V7Ext_AddSpeciesComponent').
 *
 *    fEstimatedSI
 *       The Estimated Site Index to use in case the leading species site
 *       index is not valid for some reason or not derivable due to other
 *       reasons.  If not known, supply -9.0
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully added the layer to the stand.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       Unable to add the layer to the stand because one or more of the
 *       parameters was not recognized.
 *
 *    V7EXT_ERR_LAYERALREADYEXISTS
 *       An attempt to add the layer to the polygon when another layer with
 *       the same layer id already exists.
 *
 *    V7EXT_ERR_RANK1ALREADYEXISTS
 *       A layer has already been recorded with a Rank 1 code.
 *
 *    V7EXT_ERR_TOOMANYLAYERS
 *       An attempt to add a layer to the polygon was made but the polygon
 *       already has the maximum number of layers assigned to it.  The
 *       constant V7EXT_MAX_NUM_LAYERS_PER_POLYGON defines the maximum number
 *       of layers.
 *
 *    V7EXT_ERR_INVALIDSPECIES
 *       The supplied estimated species code was not recognized.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon has already been defined.  No further changes to layers
 *       may be performed.
 *
 *
 *	Remarks
 *	-------
 *
 *		Once a layer has been added, species components can be added to the
 *    layer using the same layer id.
 *
 *    Targeting a specific layer rules:
 *       - If one or more layers are labelled as targeting the VDYP7 Primary
 *         layer, only those layers will be considered for the Primary Layer.
 *         Normal Primary Layer selection logic is suspended.
 *
 *         Any layers not specifically identified for the VDYP7 Primary Layer
 *         will be excluded from VDYP7 Primary Layer processing.
 *
 *       - If no layers are labelled as targeting the VDYP7 Primary layer,
 *         normal layer selection logic will be performed to determine what
 *         gets processed as the VDYP7 Primary Layer excluding layers that
 *         may have been targeted to the VDYP7 Veteran Layer.
 *
 *       - If one or more layers are labelled as targeting the VDYP7 Veteran
 *         layer, only those layers will be considered for the Veteran Layer.
 *         Normal Veteran Layer selection logic is suspended.
 *
 *         Any layers not specifically identified for the VDYP7 Veteran Layer
 *         will be excluded from VDYP7 Veteran Layer processing.
 *
 *       - If no layers are labelled as targeting the VDYP7 Veteran Layer,
 *         normal layer selection logic will be performed to determine what
 *         gets processed as the VDYP7 Veteran Layer, excluding layers that
 *         may have been targeted to the VDYP7 Primary Layer.
 *
 *    Layer Stockbility notes:
 *       - This percentage is in terms of the polygon stockability and would
 *         range from 1 to 100% of the polygon overall stocability.
 *       - As an example, if the Polygon has 80% stockability, and you want to
 *         attribute 75% (i.e. 60% of the entire polygon's stockability) of
 *         that stockability to the dead layer, you would supply 75% for the dead  
 *         layer stockability.
 *
 */

V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_AddLayer( V7ExtPolygonHandle     polyHandle,
                SWChar const *         sLayerID,
                SWChar const *         sTargetVDYP7Layer,
                SWChar const *         sRankCode,
                SWChar const *         sNonForestDescriptor,
                SWF32                  fMeasuredUtilLevel,
                SWF32                  fLayerPctStk,
                SWF32                  fCC,
                SWF32                  fBA,
                SWF32                  fTPH,
                SWChar const *         sEstimatedSISpcs,
                SWF32                  fEstimatedSI );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_AddLayerHistory
 *	=====================
 *
 *		Records information regarding the history of the layer.
 *
 *
 *	Parameters
 *	----------
 *
 *		polygonHandle
 *			The polygon handle to which you want to add layer information.
 *
 *    sLayerID
 *       The layer id to which you wish to add the layer information.
 *       If "" or NULL, the history will be added to the last referenced
 *       layer.
 *
 *    iSilviculturalBaseCode
 *       The silvicultural base code associated with the layer history
 *       record.
 *
 *    iStartYear
 *    iEndYear
 *       The years over which the historical activity occurred.
 *       Supply -9 for either if not known.
 *
 *    fLayerPercent
 *       The percent of the layer which was affected by the activity.
 *       Layer percent is an optional parameter and if not known, a
 *       value of -9.0 may be supplied.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully added the historical information to the layer.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the supplied parameters are invalid or missing.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       The layer to which the history information is to be applied could not
 *       be found in the current stand description.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon definition can not be changed once the polygon definition
 *       has been completed, or initial processing has occurred.
 *
 *
 *	Remarks
 *	-------
 *
 *		This routine is optional as far as supplying data is concerned.  Specific
 *    layers may or may not have history information associated with it.
 *
 *    2006/11/23
 *    Modified the input to allow -9 for an unknown Start Year.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_AddLayerHistory( V7ExtPolygonHandle       polygonHandle,
                       SWChar const *           sLayerID,
                       V7ExtSilviculturalBase   iSilviculturalBaseCode,
                       SWI32                    iStartYear,
                       SWI32                    iEndYear,
                       SWF32                    fLayerPercent );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_AddSpeciesComponent
 *	=========================
 *
 *		Adds a species component to the specified layer.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The handle to the polygon you wish to add a species to.
 *
 *    sLayerID
 *       The layer id you wish add a species to.
 *       If NULL or "", the layer used will be the last referenced or added
 *       layer from previous calls.
 *
 *    sSpcs
 *       The species code (as recognized by the SiteTools library) to be
 *       added a component of this layer.
 *
 *    fPcnt
 *       The percent of the layer this species component makes up this stand.
 *       Percent will be rounded to one decimal place of precision.
 *
 *    fTotalAge
 *       The total age of the species component.
 *       If not known, supply the value: -9.0
 *
 *    fDominantHeight
 *       The dominant height of the species component.
 *       If not known, supply the value: -9.0
 *
 *    fSI
 *       The BHA 50 Site Index for the species component.
 *       If not known, supply the value: -9.0
 *
 *    fYTBH
 *       The Years to Breast Height value for the species component.
 *       If not known, supply the value: -9.0
 *
 *    fBHAge
 *       The Breast Height Age for the species component.
 *       If not known, supply the value: -9.0
 *
 *    iSiteCurve
 *       The Site Curve to use for modelling tree height growth.  This site
 *       curve number must be one recognized by the Site Tools library.
 *       If not known, supply the value: -9
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully added the species to the layer.
 *
 *    V7EXT_ERR_INTERNALERROR
 *       An internal logic error occurred.  This should be considered a
 *       fatal error.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was missing or invalid.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       The specified layer to add the species to was not found.
 *
 *    V7EXT_ERR_INVALIDSPECIES
 *       The specified species was not recognized as a valid commercial
 *       species within the SiteTools library.
 *
 *    V7EXT_ERR_TOOMANYSPECIES
 *       An attempt was made to add too many species to the layer.
 *       The constant V7EXT_MAX_NUM_SPECIES_PER_LAYER defines the maximum
 *       number.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon has already been defined.  No further changes to species
 *       composition may be performed.
 *
 *
 *	Remarks
 *	-------
 *
 *		Each call to this routine would add a species to the layer.
 *
 *    It is an error to add duplicate species to a stand.
 *
 *    It is an error to add too many different species corresponding to
 *    a single VDYP7 species to the stand.
 *
 *    2003/11/21:
 *    Based on Cam's Nov. 21, 2003 e-mail, as species are added into a
 *    layer, the species percent for that species component is rounded
 *    to one decimal.
 *
 *    2003/11/30:
 *    Adjusted the logic for applying Estimated Site Index calculations
 *    according to Cam's IPSCB204 document.  The logic forces Estimated
 *    SI to occur after the stand has been defined.  These rules also imply
 *    that species components can not be filled in until after the stand
 *    has been fully defined.
 *
 *    2009/03/26:
 *    Updated the logic to allow for identical species to be supplied.
 *    See Sam Otukol's Mar. 25, 2009 e-mail on the subject.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_AddSpeciesComponent( V7ExtPolygonHandle   polyHandle,
                           SWChar const *       sLayerID,
                           SWChar const *       sSpcs,
                           SWF32                fPcnt,
                           SWF32                fTotalAge,
                           SWF32                fDominantHeight,
                           SWF32                fSI,
                           SWF32                fYTBH,
                           SWF32                fBHAge,
                           SWI32                iSiteCurve );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_DetermineVDYP7ProcessingLayer
 * V7Ext_VB_DetermineVDYP7ProcessingLayer
 *	======================================
 *
 *		Determine the VDYP7 Layer a particular layer within the stand will be
 *    or was processed as.
 *
 *
 *	Parameters
 *	----------
 *
 *    polyHandle
 *       The polygon handle containing the stand layers you wish to query.
 *
 *    sLayerID
 *       The particular layer within the stand you wish to query.
 *
 *
 *	Return Value
 *	------------
 *
 *		The name of the VDYP7 layer the specified layer was processed as.
 *    "" indicates the layer was not processed.
 *    "?" indicates an error was detected.
 *
 *
 *	Remarks
 *	-------
 *
 *		In order for this routine to work, the polygon must have been previously
 *    defined, have been initially processed, or projected.
 *
 *    Because layers may be aggregated (combined) into a single layer for
 *    processing within VDYP7, this mechanism allows us to view how a layer was
 *    processed within VDYP7.  This also allows us to figure out how to
 *    deaggregate the stand once processing has completed in order to apply
 *    volumes and other projected values appropriately to the different layers.
 *
 */


SWChar const *    ENV_IMPORT_STDCALL
V7Ext_DetermineVDYP7ProcessingLayer( V7ExtPolygonHandle  polyHandle,
                                     SWChar const *      sLayerID );




void              ENV_IMPORT_STDCALL
V7Ext_VB_DetermineVDYP7ProcessingLayer( SWChar *             buffer,
                                        SWI32 *              bufferLen,
                                        V7ExtPolygonHandle   polyHandle,
                                        SWChar const *       sLayerID );





/*-----------------------------------------------------------------------------
 *
 * V7Ext_InitialProcessingModeToBeUsed
 *	===================================
 *
 *		Determine the processing the stand will be initially subject to.
 *
 *
 *	Parameters
 *	----------
 *
 *    iGrowthModel
 *       On output, will specify the underlying growth model which will be
 *       used to perform initial processing based on the properties currently
 *       assigned to the polygon.
 *
 *    iProcessingMode
 *       On output, will specify the processing mode initially used to process
 *       the stand.  This selection may be overridden when the model is
 *       actually run.  This routine does, however, identify the initial values
 *       which will be used.
 *
 *       The parameter 'iGrowthMode' will identify how this parameter should
 *       be interpreted because of overlap in processing mode values between
 *       the different stand models.
 *
 *		polyHandle
 *			The handle to the polygon definition.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully determined the stand type.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       The processing mode could not be determined for some reason.  In this
 *       case, the output function parameters remain undefined.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Could not determine a primary layer.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       Could not find a primary species within the layer.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon has already been initially processed.
 *
 *    V7EXT_ERR_POLYGONNONPRODUCTIVE
 *       The polygon has been labeled as non-productive and therefore will
 *       not be processed.
 *
 *
 *	Remarks
 *	-------
 *
 *    The processing mode is specified according to how the stand is defined.
 *    The mode is completely defined by the stand attributes and is not
 *    explicitly chosen by the caller.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_InitialProcessingModeToBeUsed( V7ExtGrowthModel *     iGrowthModel,
                                     V7ExtProcessingMode *  iProcessingMode,
                                     V7ExtPolygonHandle     polyHandle );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_PerformInitialProcessing
 *	==============================
 *
 *		Runs the polygon through its initial processing making it capable of
 *    being projected to an arbitrary age or year.
 *
 *
 *	Parameters
 *	----------
 *
 *    iYearYieldsValid
 *       On output, holds the year on or after the supplied stand
 *       establishment year, for which stand yields can be reliably predicted.
 *
 *    iGrowthModel
 *       On output, the growth model actually used will be supplied through
 *       this parameter.
 *
 *       This value is actually of the data type 'enumGrowthModel' but because
 *       of data type size issues between platforms and compilers for enum
 *       data sizes, this value has been cast to the fixed size SWI32.
 *
 *    iProcessingMode
 *       On output, the processing mode for the growth model will be supplied
 *       through this parameter.
 *
 *       This value is actually of the data type 'enumProcessingMode' but
 *       because of data type size issues between platforms and compilers for
 *       enum data sizes, this value has been cast to the fixed size SWI32.
 *
 *    fPcntFrstdLandUsed
 *       Returns the Percent Forested Land that was actually used in
 *       processing the stand.
 *
 *       If a stand description was not possible, then this parameter returns
 *       the internally computed or supplied percent forested land value.
 *
 *    fYldFactorUsed
 *       Returns the Yield Factor applied to the stand.  If the yield factor
 *       was supplied when defining the polygon, then the same factor will
 *       be returned.  If the yield factor was not supplied (-9.0), an
 *       internally computed value will be returned.
 *
 *		polyHandle
 *			The handle to the polygon you wish to run through its initial
 *       processing.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully processed the polygon through either VRISTART or
 *       FIPSTART processing.
 *
 *    V7EXT_ERR_INTERNALERROR
 *       An internal logic error occurred.  This should be treated as a
 *       fatal error.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       Errors in the polygon data prevented successful processing of the
 *       polygon.  In this case, the output parameters 'iGrowthModel' and
 *       and 'iProcessingMode' will be undefined.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Could not determine a primary layer.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       Could not find a primary species within the layer.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon has already been initially processed or even projected.
 *
 *    V7EXT_ERR_POLYGONNONPRODUCTIVE
 *       The polygon has been labeled as non-productive and therefore will
 *       not be processed.
 *
 *
 *	Remarks
 *	-------
 *
 *		The polygon is processed through VRISTART or FIPSTART depending on the
 *    configuration of the polygon parameters.
 *
 *    The output parameters will inform you of the specific growth model
 *    and processing mode actually used.
 *
 *    Also see the routine: V7Ext_GetFirstYearYieldsValid which will also
 *    return the same result.
 *
 *    2004/10/08:
 *    Trap FIPSTART return codes of -4 in addition to -14 according to Cam's
 *    Oct. 8, 2004 e-mail.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_PerformInitialProcessing( SWI32 *               iYearYieldsValid,
                                SWI32 *               iGrowthModelUsed,
                                SWI32 *               iProcessingModeUsed,
                                SWF32 *               fPctFrstdLandUsed,
                                SWF32 *               fYldFactorUsed,
                                V7ExtPolygonHandle    polyHandle );






/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetPolygonInitialProcessingInfo
 *	=====================================
 *
 *		Returns the polygon level computed statistics as returned by the
 *    'V7Ext_PerformInitialProcessing' routine.
 *
 *
 *	Parameters
 *	----------
 *
 *    iYearYieldsValid
 *       On output, holds the year on or after the supplied stand
 *       establishment year, for which stand yields can be reliably predicted.
 *
 *       If not required, supply NULL for this parameter.
 *
 *    iGrowthModel
 *       On output, the growth model actually used will be supplied through
 *       this parameter.
 *
 *       This value is actually of the data type 'enumGrowthModel' but because
 *       of data type size issues between platforms and compilers for enum
 *       data sizes, this value has been cast to the fixed size SWI32.
 *
 *       If not required, supply NULL for this parameter.
 *
 *    iProcessingMode
 *       On output, the processing mode for the growth model will be supplied
 *       through this parameter.
 *
 *       This value is actually of the data type 'enumProcessingMode' but
 *       because of data type size issues between platforms and compilers for
 *       enum data sizes, this value has been cast to the fixed size SWI32.
 *
 *       If not required, supply NULL for this parameter.  If requested,
 *       'iGrowthModel' must also be requested.
 *
 *    fPcntFrstdLandUsed
 *       Returns the Percent Forested Land that was actually used in
 *       processing the stand.
 *
 *       If a stand description was not possible, then this parameter returns
 *       the internally computed or supplied percent forested land value.
 *
 *       If not required, supply NULL for this parameter.
 *
 *    fYldFactorUsed
 *       Returns the Yield Factor applied to the stand.  If the yield factor
 *       was supplied when defining the polygon, then the same factor will
 *       be returned.  If the yield factor was not supplied (-9.0), an
 *       internally computed value will be returned.
 *
 *       If not required, supply NULL for this parameter.
 *
 *		polyHandle
 *			The handle to the polygon you wish to run through its initial
 *       processing.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully obtained the projected values at the specified age.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied, or is inconsistent.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       The interaction with the underlying VDYP7CORE Library has failed.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must have been successfully processed through the
 *       'V7Ext_PerformInitialProcessing' routine before these values can
 *       be retrieved.
 *
 *
 *	Remarks
 *	-------
 *
 * 2011/02/06: 0000006
 * This routine was added to permit later retrieval of the initial processing
 * information without having to artifically carry this information forward
 * through other data structures.
 *
 * The values returned here should be identical to the values returned through
 * the 'V7Ext_PerformInitialProcessing' routine.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetPolygonInitialProcessingInfo( SWI32 *               iYearYieldsValid,
                                       SWI32 *               iGrowthModelUsed,
                                       SWI32 *               iProcessingModeUsed,
                                       SWF32 *               fPctFrstdLandUsed,
                                       SWF32 *               fYldFactorUsed,
                                       V7ExtPolygonHandle    polyHandle );






/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetFirstYearYieldsValid
 *	=============================
 *
 *		Returns the first year for which yields could be predicted for a
 *    polygon.
 *
 *
 *	Parameters
 *	----------
 *
 *		iYearYieldsValid
 *			Points to the buffer to store the first year yields are valid.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully returned the year the polygon generated its first
 *       valid yield.
 *
 *    V7EXT_ERR_INTERNALERROR
 *       An internal logic error occurred.  This should be treated as a
 *       fatal error.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the supplied parameters were missing or invalid.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Could not determine a primary layer.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       Could not find a primary species within the layer.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon has already been initially processed or even projected.
 *
 *
 *	Remarks
 *	-------
 *
 *		In the event of an error return code, the output parameter's value
 *    is undefined.
 *
 *    This routine will always return the same value as returned by the
 *    routine 'V7Ext_PerformInitialProcessing'.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetFirstYearYieldsValid( SWI32 *             iYearYieldsValid,
                               V7ExtPolygonHandle  polyHandle );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetStandAdjustmentSeeds
 *	=============================
 *
 *		Obtain the stand adjustment seeds useful for adjusting the stand
 *    using the VRIADJST process.
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
 *    polyHandle
 *       The polygon handle from which you wish to obtain the adjustment seeds
 *       from.
 *
 *    sLayerID
 *       Identifies the layer for which you wish to get the adjustment seeds.
 *       If NULL or "", refers to the last used layer.
 *       If "P", refers to the primary "combined" layer.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully obtained the adjustment seeds.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters is missing or invalid.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       An interaction with the VDYP7CORE library writing out some aspect
 *       of the layer information.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Unable to locate the specified layer.
 *
 *    V7EXT_ERR_LAYERNOTPROCESSED
 *       The requested layer was not processed and therefore adjustment seeds
 *       are not available.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon has not been initially processed OR it has already been
 *       projected.
 *
 *
 *	Remarks
 *	-------
 *
 *		These seeds are the initial values, some of which may be adjusted,
 *    to be supplied through the 'V7Ext_SetStandAdjustments' routine.
 *
 */

V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetStandAdjustmentSeeds( SWF32 *             fLH075,
                               SWF32 *             fWSV075,
                               SWF32 *             fBA125,
                               SWF32 *             fWSV125,
                               SWF32 *             fVCU125,
                               SWF32 *             fVD125,
                               SWF32 *             fVDW125,
                               SWF32 *             fRsrvd1,
                               SWF32 *             fRsrvd2,
                               SWF32 *             fRsrvd3,
                               V7ExtPolygonHandle  polyHandle,
                               SWChar const *      sLayerID );





/*-----------------------------------------------------------------------------
 *
 * V7Ext_SetStandAdjustments
 *	=========================
 *
 *		Optional step to set the stand adjustments prior to projection.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			Handle to the polygon descriptor to which we wish to apply the
 *       adjustments.
 *
 *    sLayerID
 *       The specific layer to which the adjustments are to be applied.
 *       "X" indicates the "spanning layer" and applies to all layers.
 *       "P" indicates the primary layer and would apply either to a combined
 *           layer or to layer "1".
 *       Otherwise the adjustments are applied to the specific layer specified.
 *
 *       If NULL, the last referenced layer will be used.
 *
 *    fLH075
 *       Lorey Height at the 7.5cm+ utilization level.
 *
 *    fWSV075
 *       Whole Stem Volume at the 7.5cm+ utilization level.
 *
 *    fBA125
 *       Basal Area at the 12.5cm+ utilization level.
 *
 *    fWSV125
 *       Whole Stem Volume at the 12.5cm+ utilization level.
 *
 *    fVCU125
 *       Close Utilization Volume at the 12.5cm+ utilization level.
 *
 *    fVD125
 *       Volume less Decay at the 12.5cm+ utilization level.
 *
 *    fVDW125
 *       Volume less Decay and Waste at the 12.5cm+ utilization level.
 *
 *    fRsrvd1
 *    fRsrvd2
 *    fRsrvd3
 *       Reserved for future use.
 *
 *
 *	Return Value
 *	------------
 *
 *    V7EXT_SUCCESS
 *       Successfully set the adjustments.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       Unable to apply the stand adjustments.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Unable to locate the specified layer.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must have been initially processed AND not have
 *       been projected.
 *
 *
 *	Remarks
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */

V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_SetStandAdjustments( V7ExtPolygonHandle   polyHandle,
                           SWChar const *       sLayerID,
                           SWF32                fLH075,
                           SWF32                fWSV075,
                           SWF32                fBA125,
                           SWF32                fWSV125,
                           SWF32                fVCU125,
                           SWF32                fVD125,
                           SWF32                fVDW125,
                           SWF32                fRsrvd1,
                           SWF32                fRsrvd2,
                           SWF32                fRsrvd3 );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_ProjectStandToYear
 *	========================
 *
 *		Projects the stand from its reference year to the year requested.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle to be projected.
 *
 *    yearToProjectTo
 *       The year to project the polygon to.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully projected the stand through the age range.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       An invalid parameter was supplied or is missing.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       An interaction with the VDYP7CORE library writing out some aspect
 *       of the layer information.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must have been initially processed but not already
 *       projected.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Indicates the the stand does not have a primary layer.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       Indicates that the stand does not have a leading species within the
 *       primary layer.
 *
 *
 *	Remarks
 *	-------
 *
 *		This routine is only project to the year requested.
 *
 */

V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_ProjectStandToYear( V7ExtPolygonHandle    polyHandle,
                          SWI32                 yearToProjectTo );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_ProjectStandByAge
 *	=======================
 *
 *		Projects the stand through an age range.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle to be projected.
 *
 *    fStartAge
 *       The start of the age range to project from.
 *
 *    fFinishAge
 *       The end of the age range to project to.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully projected the stand through the age range.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       An invalid parameter was supplied or is missing.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       An interaction with the VDYP7CORE library writing out some aspect
 *       of the layer information.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must have been initially processed but not already
 *       projected.
 *
 *
 *	Remarks
 *	-------
 *
 *		This routine is most useful when prjecting for a yield table.
 *
 */

V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_ProjectStandByAge( V7ExtPolygonHandle  polyHandle,
                         SWF32               fStartAge,
                         SWF32               fFinishAge );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedPolygonGrowthInfo
 *	===================================
 *
 *		Obtains the density, height, basal area and diameter information for
 *    the entire polygon at the age requested.
 *
 *
 *	Parameters
 *	----------
 *
 *    fSiteIndex
 *       On output, the Site Index for the entire polygon will be returned.
 *       Must not be NULL.
 *
 *		fDomHeight
 *			On output, the dominant height of the layer at the age specified.
 *       Must not be NULL.
 *
 *    fLoreyHeight
 *       On output, the Lorey height of the layer at the age specified.
 *       Must not be NULL.
 *
 *    fDiameter
 *       On output, contains the diameter of the layer at the age specified.
 *       Must not be NULL.
 *
 *    fTPH
 *       On output, contains the Trees Per Hectare at the age specified.
 *       Must not be NULL.
 *
 *    fBasalArea
 *       On output, contains the Basal Area of the layer at the age
 *       specified.
 *       Must not be NULL.
 *
 *    polyHandle
 *       The handle to the polygon for which you want the yields.
 *       Must not be: V7EXT_INVALID_POLYGON_DESCRIPTOR
 *
 *    fTotalAge
 *       The total age of the for which you want the growth information.
 *       Must be greater than or equal to 0.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully obtained the projected values at the specified age.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied, or is inconsistent.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       The interaction with the underlying VDYP7CORE Library has failed.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must be projected before projected values can be
 *       retrieved.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Unable to locate the primary layer for the polygon and/or there are
 *       zero layers in the polygon.
 *
 *    V7EXT_ERR_LAYERNOTPROCESSED
 *       The primary layer was either not processed or projected.
 *
 *
 *	Remarks
 *	-------
 *
 *    Note that certain layers may not have been projected.  As a result,
 *    those layers will not be included or considered in the returned
 *    polygon values.
 *
 *    When supplying a Total Age to return Growth Information, the Total Age
 *    for a polygon is considered to be the Total Age of the Primary Layer.
 *
 *    The returned values for this routine always reflect:
 *       - For Site Index, Dominant Height and Lorey Height:
 *             These values are the same as for the Primary Layer.
 *
 *       - For TPH, Basal Area and Diameter:
 *             These values are based on the aggregate of all projected 
 *             layers.
 *             
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetProjectedPolygonGrowthInfo( SWF32 *               fSiteIndex,
                                     SWF32 *               fDomHeight,
                                     SWF32 *               fLoreyHeight,
                                     SWF32 *               fDiameter,
                                     SWF32 *               fTPH,
                                     SWF32 *               fBasalArea,
                                     V7ExtPolygonHandle    polyHandle,
                                     SWF32                 fTotalAge );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedLayerStandGrowthInfo
 *	======================================
 *
 *		Obtains the density, height, basal area and diameter information for
 *    the entire stand at a specific layer at the age requested.
 *
 *
 *	Parameters
 *	----------
 *
 *    fSiteIndex
 *       On output, the Site Index for the entire layer will be returned.
 *       Must not be NULL.
 *
 *		fDomHeight
 *			On output, the dominant height of the layer at the age specified.
 *       Must not be NULL.
 *
 *    fLoreyHeight
 *       On output, the Lorey height of the layer at the age specified.
 *       Must not be NULL.
 *
 *    fDiameter
 *       On output, contains the diameter of the layer at the age specified.
 *       Must not be NULL.
 *
 *    fTPH
 *       On output, contains the Trees Per Hectare at the age specified.
 *       Must not be NULL.
 *
 *    fBasalArea
 *       On output, contains the Basal Area of the layer at the age
 *       specified.
 *       Must not be NULL.
 *
 *    polyHandle
 *       The handle to the polygon for which you want the yields.
 *
 *    sLayerID
 *       The particular layer for which you want the layer information.
 *       If NULL or "", the last referenced layer will be used.
 *
 *    fTotalAge
 *       The total age of the layer for which you want the growth information.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully obtained the projected values at the specified age.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied, or is inconsistent.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Unable to locate the requested layer.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       The interaction with the underlying VDYP7CORE Library has failed.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must be projected before projected values can be
 *       retrieved.
 *
 *
 *	Remarks
 *	-------
 *
 *    Note that certain layers may not have been processed.  As a result,
 *    those layers may result in no growth info despite the presence of
 *    growth info on other layers.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetProjectedLayerStandGrowthInfo( SWF32 *               fSiteIndex,
                                        SWF32 *               fDomHeight,
                                        SWF32 *               fLoreyHeight,
                                        SWF32 *               fDiameter,
                                        SWF32 *               fTPH,
                                        SWF32 *               fBasalArea,
                                        V7ExtPolygonHandle    polyHandle,
                                        SWChar const *        sLayerID,
                                        SWF32                 fTotalAge );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedLayerGroupGrowthInfo
 *	======================================
 *
 *		Obtains the density, height, basal area and diameter information for
 *    a specific species group at a specific layer at the age requested.
 *
 *
 *	Parameters
 *	----------
 *
 *    bDomSiteSpcs
 *       On output, indicates whether or not the requested species is flagged
 *       as the dominant site species for the year in question.  The dominant
 *       species flag comes from column 98 of the VDYP7 Species file.
 *
 *       non-zero    indicates the SP0 is dominant
 *       zero        indicates the SP0 is not dominant
 *
 *    iSiteCurve
 *       On output, the Site Index curve used for the species group will
 *       be returned (if available).  If not available, -9 will be returned.
 *
 *    fSiteIndex
 *       On output, the Site Index used for the species group will be
 *       returned (if available).
 *
 *		fDomHeight
 *			On output, the dominant height of the layer at the age specified.
 *
 *    fLoreyHeight
 *       On output, the Lorey height of the layer at the age specified.
 *
 *    fDiameter
 *       On output, contains the diameter of the layer at the age specified.
 *
 *    fTPH
 *       On output, contains the Trees Per Hectare at the age specified.
 *
 *    fBasalArea
 *       On output, contains the Basal Area of the layer at the age
 *       specified.
 *
 *    polyHandle
 *       The handle to the polygon for which you want the yields.
 *
 *    sLayerID
 *       The particular layer for which you want the layer information.
 *       If NULL or "", the last referenced layer will be used.
 *
 *    sSP0Name
 *       The name of the SP0 species for which you want the growth
 *       information.  If an SP64 is supplied, it will be converted into an
 *       appropriate SP0 code for look up.
 *
 *    fTotalAge
 *       The total age of the stand for which you want the growth information.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully obtained the projected values at the specified age.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied, or is inconsistent.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Unable to locate the requested layer.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       The requested species group does not exist in the layer.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       The interaction with the underlying VDYP7CORE Library has failed.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must be projected before projected values can be
 *       retrieved.
 *
 *
 *	Remarks
 *	-------
 *
 *    Note that certain layers may not have been processed.  As a result,
 *    those layers may result in no growth info despite the presence of
 *    info on other layers.
 *
 *    Note that different species may become the dominant species over the
 *    entire range of a projection.
 *
 *    2005/09/23:
 *    Now allow the retrieval of growth information for layers that were
 *    not processed.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetProjectedLayerGroupGrowthInfo( SWI16 *               bDomSiteSpcs,
                                        SWI32 *               iSiteCurve,
                                        SWF32 *               fSiteIndex,
                                        SWF32 *               fDomHeight,
                                        SWF32 *               fLoreyHeight,
                                        SWF32 *               fDiameter,
                                        SWF32 *               fTPH,
                                        SWF32 *               fBasalArea,
                                        V7ExtPolygonHandle    polyHandle,
                                        SWChar const *        sLayerID,
                                        SWChar const *        sSP0Name,
                                        SWF32                 fTotalAge );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedLayerSpeciesGrowthInfo
 *	========================================
 *
 *		Obtains the density, height, basal area and diameter information for
 *    a specific species at a specific layer at the age requested.
 *
 *
 *	Parameters
 *	----------
 *
 *    bDomSiteSpcs
 *       On output, indicates whether or not the requested species is flagged
 *       as the dominant site species for the year in question.  The dominant
 *       SP0 flag comes from column 98 of the VDYP7 Species file.  A particular
 *       species is dominant within that SP0 if it was the first supplied SP64
 *       of that SP0 group.
 *
 *       non-zero    indicates the SP0 is dominant
 *       zero        indicates the SP0 is not dominant
 *
 *    fSpeciesTotalAge
 *       On output, the total age of the requested species when the stand is
 *       at the requested age.
 *
 *    fSiteIndex
 *       On output, the Site Index used for the species group will be
 *       returned (if available).
 *
 *		fDomHeight
 *			On output, the dominant height of the layer at the age specified.
 *
 *    fLoreyHeight
 *       On output, the Lorey height of the layer at the age specified.
 *
 *    fDiameter
 *       On output, contains the diameter of the layer at the age specified.
 *
 *    fTPH
 *       On output, contains the Trees Per Hectare at the age specified.
 *
 *    fBasalArea
 *       On output, contains the Basal Area of the layer at the age
 *       specified.
 *
 *    polyHandle
 *       The handle to the polygon for which you want the yields.
 *
 *    sLayerID
 *       The particular layer for which you want the layer information.
 *       If NULL or "", the last referenced layer will be used.
 *
 *    sSpeciesCode
 *       The species code for which you wish the growth information.
 *
 *    fStandTotalAge
 *       The total age of the stand for which you want the growth information.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully obtained the projected values at the specified age.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied, or is inconsistent.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Unable to locate the requested layer.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       The requested species group does not exist in the layer.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       The interaction with the underlying VDYP7CORE Library has failed.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must be projected before projected values can be
 *       retrieved.
 *
 *
 *	Remarks
 *	-------
 *
 *    Note that certain layers may not have been processed.  As a result,
 *    those layers may result in no growth info despite the presence of
 *    growth info on other layers.
 *
 *    2004/02/15:
 *    When processing stands which have secondary species which match the
 *    primary species at the SP0 and have different site information supplied,
 *    we need to add special case processing which will generate an age and
 *    height based on the original supplied age and height.
 *    See Cam's Feb 6, 2004 e-mail for details.
 *
 *    2004/11/30:
 *    Now return a Dominant Site Species flag for the projected data if the
 *    VDYP7 calculations determined that the requested species was the
 *    first supplied SP64 of its corresponding SP0 group and that SP0 group
 *    was flagged as dominant in the output calculations.
 *
 *    2005/09/23:
 *    Now allow the retrieval of growth information for layers that were
 *    not processed.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetProjectedLayerSpeciesGrowthInfo( SWI16 *               bDomSiteSpcs,
                                          SWF32 *               fSpeciesTotalAge,
                                          SWF32 *               fSiteIndex,
                                          SWF32 *               fDomHeight,
                                          SWF32 *               fLoreyHeight,
                                          SWF32 *               fDiameter,
                                          SWF32 *               fTPH,
                                          SWF32 *               fBasalArea,
                                          V7ExtPolygonHandle    polyHandle,
                                          SWChar const *        sLayerID,
                                          SWChar const *        sSpeciesCode,
                                          SWF32                 fStandTotalAge );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedPolygonVolumes
 *	================================
 *
 *		Obtains the yields summarized at the polygon level for a specific
 *    stand total age.
 *
 *
 *	Parameters
 *	----------
 *
 *    fVolumeWS
 *       On output, contains the Whole Stem Volume at the age specified.
 *       Must not be NULL.
 *
 *    fVolumeCU
 *       On output, contains the Close Utilization Volume at the age
 *       specified.
 *       Must not be NULL.
 *
 *    fVolumeD
 *       On output, contains the Volume less Decay at the age specified.
 *       Must not be NULL.
 *
 *    fVolumeDW
 *       On output, contains the Volume less Decay, Waste at the age
 *       specified.
 *       Must not be NULL.
 *
 *    fVolumeDWB
 *       On output, contains the Volume less Decay, Waste and Breakage at
 *       the age specified.
 *       Must not be NULL.
 *
 *    polyHandle
 *       The handle to the polygon for which you want the yields.
 *       Must not be NULL.
 *
 *    fTotalAge
 *       The total age of the stand for which you want the growth information.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully obtained the projected values at the specified age.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied, or is inconsistent.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Unable to locate the requested layer.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       The interaction with the underlying VDYP7CORE Library has failed.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must be projected before projected values can be
 *       retrieved.
 *
 *    V7EXT_ERR_LAYERNOTPROCESSED
 *       The requested layer was not projected and therefore projected volume
 *       information is not available.
 *
 *
 *	Remarks
 *	-------
 *
 *    Note that certain layers may not have been processed.  As a result,
 *    those layers may result in no volumes despite the presence of
 *    volumes on other layers.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetProjectedPolygonVolumes( SWF32 *               fVolumeWS,
                                  SWF32 *               fVolumeCU,
                                  SWF32 *               fVolumeD,
                                  SWF32 *               fVolumeDW,
                                  SWF32 *               fVolumeDWB,
                                  V7ExtPolygonHandle    polyHandle,
                                  SWF32                 fTotalAge );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedLayerStandVolumes
 *	===================================
 *
 *		Obtains the yields summarized at the layer level for a specific
 *    stand total age.
 *
 *
 *	Parameters
 *	----------
 *
 *    fVolumeWS
 *       On output, contains the Whole Stem Volume at the age specified.
 *       Must not be NULL.
 *
 *    fVolumeCU
 *       On output, contains the Close Utilization Volume at the age
 *       specified.
 *       Must not be NULL.
 *
 *    fVolumeD
 *       On output, contains the Volume less Decay at the age specified.
 *       Must not be NULL.
 *
 *    fVolumeDW
 *       On output, contains the Volume less Decay, Waste at the age
 *       specified.
 *       Must not be NULL.
 *
 *    fVolumeDWB
 *       On output, contains the Volume less Decay, Waste and Breakage at
 *       the age specified.
 *       Must not be NULL.
 *
 *    polyHandle
 *       The handle to the polygon for which you want the yields.
 *       Must not be NULL.
 *
 *    sLayerID
 *       The particular layer for which you want the layer information.
 *       If NULL or "", the last referenced layer will be used.
 *
 *    fTotalAge
 *       The total age of the stand for which you want the growth information.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully obtained the projected values at the specified age.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied, or is inconsistent.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Unable to locate the requested layer.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       The interaction with the underlying VDYP7CORE Library has failed.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must be projected before projected values can be
 *       retrieved.
 *
 *    V7EXT_ERR_LAYERNOTPROCESSED
 *       The requested layer was not projected and therefore projected volume
 *       information is not available.
 *
 *
 *	Remarks
 *	-------
 *
 *    Note that certain layers may not have been processed.  As a result,
 *    those layers may result in no volumes despite the presence of
 *    volumes on other layers.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetProjectedLayerStandVolumes( SWF32 *               fVolumeWS,
                                     SWF32 *               fVolumeCU,
                                     SWF32 *               fVolumeD,
                                     SWF32 *               fVolumeDW,
                                     SWF32 *               fVolumeDWB,
                                     V7ExtPolygonHandle    polyHandle,
                                     SWChar const *        sLayerID,
                                     SWF32                 fTotalAge );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedLayerGroupVolumes
 *	===================================
 *
 *		Obtains the yields summarized at the layer species group level for a
 *    specific stand total age.
 *
 *
 *	Parameters
 *	----------
 *
 *    fVolumeWS
 *       On output, contains the Whole Stem Volume at the age specified.
 *
 *    fVolumeCU
 *       On output, contains the Close Utilization Volume at the age
 *       specified.
 *
 *    fVolumeD
 *       On output, contains the Volume less Decay at the age specified.
 *
 *    fVolumeDW
 *       On output, contains the Volume less Decay, Waste at the age
 *       specified.
 *
 *    fVolumeDWB
 *       On output, contains the Volume less Decay, Waste and Breakage at
 *       the age specified.
 *
 *    polyHandle
 *       The handle to the polygon for which you want the yields.
 *
 *    sLayerID
 *       The particular layer for which you want the layer information.
 *       If NULL or "", the last referenced layer will be used.
 *
 *    iSP0Index
 *       The VDYP7 Species Index for which you wish the volumes.
 *       This value must range from 0 to (vdyp7core_numspecies - 1)
 *
 *    fTotalAge
 *       The total age of the stand for which you want the volume information.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully obtained the projected values at the specified age.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied, or is inconsistent.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Unable to locate the requested layer.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       The requested species could not be located in the stand.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       The interaction with the underlying VDYP7CORE Library has failed.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must be projected before projected values can be
 *       retrieved.
 *
 *    V7EXT_ERR_LAYERNOTPROCESSED
 *       The requested layer was not projected and therefore projected volume
 *       information is not available.
 *
 *
 *	Remarks
 *	-------
 *
 *    Note that certain layers may not have been processed.  As a result,
 *    those layers may result in no volumes despite the presence of
 *    volumes on other layers.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetProjectedLayerGroupVolumes( SWF32 *               fVolumeWS,
                                     SWF32 *               fVolumeCU,
                                     SWF32 *               fVolumeD,
                                     SWF32 *               fVolumeDW,
                                     SWF32 *               fVolumeDWB,
                                     V7ExtPolygonHandle    polyHandle,
                                     SWChar const *        sLayerID,
                                     SWI32                 iSP0Index,
                                     SWF32                 fTotalAge );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedLayerSpeciesVolumes
 *	=====================================
 *
 *		Obtains the yields summarized at the layer species for a
 *    specific stand total age.
 *
 *
 *	Parameters
 *	----------
 *
 *    fVolumeWS
 *       On output, contains the Whole Stem Volume at the age specified.
 *
 *    fVolumeCU
 *       On output, contains the Close Utilization Volume at the age
 *       specified.
 *
 *    fVolumeD
 *       On output, contains the Volume less Decay at the age specified.
 *
 *    fVolumeDW
 *       On output, contains the Volume less Decay, Waste at the age
 *       specified.
 *
 *    fVolumeDWB
 *       On output, contains the Volume less Decay, Waste and Breakage at
 *       the age specified.
 *
 *    polyHandle
 *       The handle to the polygon for which you want the yields.
 *
 *    sLayerID
 *       The particular layer for which you want the layer information.
 *       If NULL or "", the last referenced layer will be used.
 *
 *    sSpeciesCode
 *       The species code for which you wish the volumes.
 *
 *    fTotalAge
 *       The total age of the stand for which you want the volume information.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully obtained the projected values at the specified age.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied, or is inconsistent.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Unable to locate the requested layer.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       The requested species could not be located in the stand.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       The interaction with the underlying VDYP7CORE Library has failed.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must be projected before projected values can be
 *       retrieved.
 *
 *    V7EXT_ERR_LAYERNOTPROCESSED
 *       The requested layer was not projected and therefore projected volume
 *       information is not available.
 *
 *
 *	Remarks
 *	-------
 *
 *    Note that certain layers may not have been processed.  As a result,
 *    those layers may result in no volumes despite the presence of
 *    volumes on other layers.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetProjectedLayerSpeciesVolumes( SWF32 *               fVolumeWS,
                                       SWF32 *               fVolumeCU,
                                       SWF32 *               fVolumeD,
                                       SWF32 *               fVolumeDW,
                                       SWF32 *               fVolumeDWB,
                                       V7ExtPolygonHandle    polyHandle,
                                       SWChar const *        sLayerID,
                                       SWChar const *        sSpeciesCode,
                                       SWF32                 fTotalAge );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedLayerStandMoFBiomass
 *	======================================
 *
 *		Obtains the MoF biomass summarized at the layer level for a specific
 *    stand total age.
 *
 *
 *	Parameters
 *	----------
 *
 *    fMoFBiomassWS
 *       On output, contains the Whole Stem MoF Biomass at the age specified.
 *
 *    fMoFBiomassCU
 *       On output, contains the Close Utilization MoF Biomass at the age
 *       specified.
 *
 *    fMoFBiomassD
 *       On output, contains the MoF Biomass less Decay at the age specified.
 *
 *    fMoFBiomassDW
 *       On output, contains the MoF Biomass less Decay, Waste at the age
 *       specified.
 *
 *    fMoFBiomassDWB
 *       On output, contains the MoF Biomass less Decay, Waste and Breakage at
 *       the age specified.
 *
 *    polyHandle
 *       The handle to the polygon for which you want the MoF biomass.
 *
 *    sLayerID
 *       The particular layer for which you want the layer information.
 *       If NULL or "", the last referenced layer will be used.
 *
 *    fTotalAge
 *       The total age of the stand for which you want the MoF biomass
 *       information.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully obtained the projected values at the specified age.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied, or is inconsistent.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Unable to locate the requested layer.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       The interaction with the underlying VDYP7CORE Library has failed.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must be projected before projected values can be
 *       retrieved.
 *
 *    V7EXT_ERR_LAYERNOTPROCESSED
 *       The requested layer was not projected and therefore projected MoF
 *       biomass information is not available.
 *
 *
 *	Remarks
 *	-------
 *
 *    Note that certain layers may not have been processed.  As a result,
 *    those layers may result in no MoF biomass despite the presence of
 *    MoF biomass on other layers.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetProjectedLayerStandMoFBiomass( SWF32 *               fMoFBiomassWS,
                                        SWF32 *               fMoFBiomassCU,
                                        SWF32 *               fMoFBiomassD,
                                        SWF32 *               fMoFBiomassDW,
                                        SWF32 *               fMoFBiomassDWB,
                                        V7ExtPolygonHandle    polyHandle,
                                        SWChar const *        sLayerID,
                                        SWF32                 fTotalAge );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedPolygonCFSBiomass
 *	===================================
 *
 *		Obtains the CFS Biomass summarized at the polygon level for a specific
 *    stand total age.
 *
 *
 *	Parameters
 *	----------
 *
 *    fCFSBiomassMerch
 *       On output, contains the total stem wood biomass of 
 *       merchantable-sized live trees (biomass includes stumps and tops), in
 *       metric tonnes per ha (T/ha).
 *       Must not be NULL.
 *
 *    fCFSBiomassNonMerch
 *       On output, contains the stem wood biomass of live,
 *       nonmerchantable-sized trees (T/ha).
 *       Must not be NULL.
 *
 *    fCFSBiomassSapling
 *       On output, contains the stem wood biomass of live, sapling-sized
 *       trees (T/ha).
 *       Must not be NULL.
 *
 *    fPropStemwood
 *       On output, proportion of total tree biomass in stemwood.
 *       Must not be NULL.
 *
 *    fPropBark
 *       On output, proportion of total tree biomass in stem bark.
 *       Must not be NULL.
 *
 *    fPropBranches
 *       On output, proportion of total tree biomass in branches.
 *       Must not be NULL.
 *
 *    fPropFoliage
 *       On output, proportion of total tree biomass in foliage.
 *       Must not be NULL.
 *       
 *    fPropDead
 *       On output, above ground dead tree biomass expressed as a fraction of
 *       the merchantable stemwood biomass.
 *
 *       Must not be NULL.
 *
 *    fBioStemwood
 *       On output, total tree stem biomass.
 *       Must not be NULL.
 *
 *    fBioBark
 *       On output, total tree biomass in stem bark.
 *       Must not be NULL.
 *
 *    fBioBranches
 *       On output, total tree biomass in branches.
 *       Must not be NULL.
 *
 *    fBioFoliage
 *       On output, total tree biomass in foliage.
 *       Must not be NULL.
 *       
 *    fBioDead
 *       On output, above ground dead tree biomass.
 *       Must not be NULL.
 *
 *    polyHandle
 *       The handle to the polygon for which you want the projected MoF 
 *       Biomass.
 *
 *       Must not be NULL.
 *
 *    fPolyVolumeCU
 *       The polygon level Close Utilization volume from which Biomass will
 *       be calculated.
 *
 *       Must be greater than or equal to 0.0.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully obtained the projected values at the specified age.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied, or is inconsistent.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Unable to locate a projected layer.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       The interaction with the underlying VDYP7CORE Library has failed.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must be projected before projected values can be
 *       retrieved.
 *
 *    V7EXT_ERR_LAYERNOTPROCESSED
 *       The requested layer was not projected and therefore projected value
 *       information is not available.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       No leading species could be located on the polygon primary layer.
 *
 *    V7EXT_ERR_INVALIDBEC
 *       Unable to convert the polygon BEC Zone into a CFS Eco Zone equivalent.
 *
 *
 *	Remarks
 *	-------
 *
 *    Note that certain layers may not have been processed.  As a result,
 *    those layers may result in no biomass despite the presence of
 *    biomass on other layers.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetProjectedPolygonCFSBiomass( SWF32 *               fCFSBiomassMerch,
                                     SWF32 *               fCFSBiomassNonMerch,
                                     SWF32 *               fCFSBiomassSapling,
                                     SWF32 *               fPropStemwood,
                                     SWF32 *               fPropBark,
                                     SWF32 *               fPropBranches,
                                     SWF32 *               fPropFoliage,
                                     SWF32 *               fPropDead,
                                     SWF32 *               fBioStemwood,
                                     SWF32 *               fBioBark,
                                     SWF32 *               fBioBranches,
                                     SWF32 *               fBioFoliage,
                                     SWF32 *               fBioDead,
                                     V7ExtPolygonHandle    polyHandle,
                                     SWF32                 fPolyVolumeCU );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedLayerCFSBiomass
 *	=================================
 *
 *		Obtains the CFS Biomass summarized at the layer level for a specific
 *    stand total age.
 *
 *
 *	Parameters
 *	----------
 *
 *    fCFSBiomassMerch
 *       On output, contains the total stem wood biomass of 
 *       merchantable-sized live trees (biomass includes stumps and tops), in
 *       metric tonnes per ha (T/ha).
 *       Must not be NULL.
 *
 *    fCFSBiomassNonMerch
 *       On output, contains the stem wood biomass of live,
 *       nonmerchantable-sized trees (T/ha).
 *       Must not be NULL.
 *
 *    fCFSBiomassSapling
 *       On output, contains the stem wood biomass of live, sapling-sized
 *       trees (T/ha).
 *       Must not be NULL.
 *
 *    fPropStemwood
 *       On output, proportion of total tree biomass in stemwood.
 *       Must not be NULL.
 *
 *    fPropBark
 *       On output, proportion of total tree biomass in stem bark.
 *       Must not be NULL.
 *
 *    fPropBranches
 *       On output, proportion of total tree biomass in branches.
 *       Must not be NULL.
 *
 *    fPropFoliage
 *       On output, proportion of total tree biomass in foliage.
 *       Must not be NULL.
 *       
 *    fPropDead
 *       On output, above ground dead tree biomass expressed as a fraction of
 *       the merchantable stemwood biomass.
 *
 *       Must not be NULL.
 *
 *    fBioStemwood
 *       On output, total tree stem biomass.
 *       Must not be NULL.
 *
 *    fBioBark
 *       On output, total tree biomass in stem bark.
 *       Must not be NULL.
 *
 *    fBioBranches
 *       On output, total tree biomass in branches.
 *       Must not be NULL.
 *
 *    fBioFoliage
 *       On output, total tree biomass in foliage.
 *       Must not be NULL.
 *       
 *    fBioDead
 *       On output, above ground dead tree biomass.
 *       Must not be NULL.
 *
 *    polyHandle
 *       The handle to the polygon for which you want the projected MoF 
 *       Biomass.
 *
 *       Must not be NULL.
 *
 *    sLayerID
 *       The specific layer for which the CFS Biomass is to be calculated.
 *
 *       Must name a valid layer within the polygon definition.
 *
 *    fLayerVolumeCU
 *       The layer level Close Utilization volume from which Biomass will
 *       be calculated.
 *
 *       Must be greater than or equal to 0.0.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully obtained the projected values at the specified age.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied, or is inconsistent.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Unable to locate a projected layer.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       The interaction with the underlying VDYP7CORE Library has failed.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must be projected before projected values can be
 *       retrieved.
 *
 *    V7EXT_ERR_LAYERNOTPROCESSED
 *       The requested layer was not projected and therefore projected value
 *       information is not available.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       No leading species could be located on the identified layer.
 *
 *    V7EXT_ERR_INVALIDBEC
 *       Unable to convert the polygon BEC Zone into a CFS Eco Zone equivalent.
 *
 *
 *	Remarks
 *	-------
 *
 *    Note that certain layers may not have been processed.  As a result,
 *    those layers may result in no biomass despite the presence of
 *    biomass on other layers.
 *
 *    2017-07-24:
 *    As per conversation with Wenli, suppress computed values for dead layers.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetProjectedLayerCFSBiomass( SWF32 *               fCFSBiomassMerch,
                                   SWF32 *               fCFSBiomassNonMerch,
                                   SWF32 *               fCFSBiomassSapling,
                                   SWF32 *               fPropStemwood,
                                   SWF32 *               fPropBark,
                                   SWF32 *               fPropBranches,
                                   SWF32 *               fPropFoliage,
                                   SWF32 *               fPropDead,
                                   SWF32 *               fBioStemwood,
                                   SWF32 *               fBioBark,
                                   SWF32 *               fBioBranches,
                                   SWF32 *               fBioFoliage,
                                   SWF32 *               fBioDead,
                                   V7ExtPolygonHandle    polyHandle,
                                   SWChar const *        sLayerID,
                                   SWF32                 fLayerVolumeCU );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedPolygonMoFBiomass
 *	===================================
 *
 *		Obtains the MoF Biomass summarized at the polygon level for a specific
 *    stand total age.
 *
 *
 *	Parameters
 *	----------
 *
 *    fMoFBiomassWS
 *       On output, contains the Whole Stem Biomass at the age specified.
 *       Must not be NULL.
 *
 *    fMoFBiomassCU
 *       On output, contains the Close Utilization Biomass at the age
 *       specified.
 *       Must not be NULL.
 *
 *    fMoFBiomassD
 *       On output, contains the Biomass less Decay at the age specified.
 *       Must not be NULL.
 *
 *    fMoFBiomassDW
 *       On output, contains the Biomass less Decay, Waste at the age
 *       specified.
 *       Must not be NULL.
 *
 *    fMoFBiomassDWB
 *       On output, contains the Biomass less Decay, Waste and Breakage at
 *       the age specified.
 *       Must not be NULL.
 *
 *    polyHandle
 *       The handle to the polygon for which you want the projected MoF 
 *       Biomass.
 *
 *       Must not be NULL.
 *
 *    fTotalAge
 *       The total age of the stand for which you want the projected Biomass.
 *       Must be a valid age value (greater than or equal to 0.0)
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully obtained the projected values at the specified age.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied, or is inconsistent.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Unable to locate the requested layer.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       The interaction with the underlying VDYP7CORE Library has failed.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must be projected before projected values can be
 *       retrieved.
 *
 *    V7EXT_ERR_LAYERNOTPROCESSED
 *       The requested layer was not projected and therefore projected value
 *       information is not available.
 *
 *
 *	Remarks
 *	-------
 *
 *    Note that certain layers may not have been processed.  As a result,
 *    those layers may result in no biomass despite the presence of
 *    biomass on other layers.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetProjectedPolygonMoFBiomass( SWF32 *               fMoFBiomassWS,
                                     SWF32 *               fMoFBiomassCU,
                                     SWF32 *               fMoFBiomassD,
                                     SWF32 *               fMoFBiomassDW,
                                     SWF32 *               fMoFBiomassDWB,
                                     V7ExtPolygonHandle    polyHandle,
                                     SWF32                 fTotalAge );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedLayerGroupMoFBiomass
 *	======================================
 *
 *		Obtains the MoF biomass summarized at the layer species group level for a
 *    specific stand total age.
 *
 *
 *	Parameters
 *	----------
 *
 *    fMoFBiomassWS
 *       On output, contains the Whole Stem MoF Biomass at the age specified.
 *
 *    fMoFBiomassCU
 *       On output, contains the Close Utilization MoF Biomass at the age
 *       specified.
 *
 *    fMoFBiomassD
 *       On output, contains the MoF Biomass less Decay at the age specified.
 *
 *    fMoFBiomassDW
 *       On output, contains the MoF Biomass less Decay, Waste at the age
 *       specified.
 *
 *    fMoFBiomassDWB
 *       On output, contains the MoF Biomass less Decay, Waste and Breakage at
 *       the age specified.
 *
 *    polyHandle
 *       The handle to the polygon for which you want the MoF biomass.
 *
 *    sLayerID
 *       The particular layer for which you want the layer information.
 *       If NULL or "", the last referenced layer will be used.
 *
 *    iSP0Index
 *       The VDYP7 Species Index for which you wish the volumes.
 *       This value must range from 0 to (vdyp7core_numspecies - 1)
 *
 *    fTotalAge
 *       The total age of the stand for which you want the MoF biomass 
 *       information.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully obtained the projected values at the specified age.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied, or is inconsistent.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Unable to locate the requested layer.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       The requested species could not be located in the stand.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       The interaction with the underlying VDYP7CORE Library has failed.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must be projected before projected values can be
 *       retrieved.
 *
 *    V7EXT_ERR_LAYERNOTPROCESSED
 *       The requested layer was not projected and therefore projected MoF
 *       biomass information is not available.
 *
 *
 *	Remarks
 *	-------
 *
 *    Note that certain layers may not have been processed.  As a result,
 *    those layers may result in no MoF biomass despite the presence of
 *    MoF biomass on other layers.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetProjectedLayerGroupMoFBiomass( SWF32 *               fMoFBiomassWS,
                                        SWF32 *               fMoFBiomassCU,
                                        SWF32 *               fMoFBiomassD,
                                        SWF32 *               fMoFBiomassDW,
                                        SWF32 *               fMoFBiomassDWB,
                                        V7ExtPolygonHandle    polyHandle,
                                        SWChar const *        sLayerID,
                                        SWI32                 iSP0Index,
                                        SWF32                 fTotalAge );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedLayerSpeciesMoFBiomass
 *	========================================
 *
 *		Obtains the MoF biomass summarized at the layer species for a
 *    specific stand total age.
 *
 *
 *	Parameters
 *	----------
 *
 *    fMoFBiomassWS
 *       On output, contains the Whole Stem MoF Biomass at the age specified.
 *
 *    fMoFBiomassCU
 *       On output, contains the Close Utilization MoF Biomass at the age
 *       specified.
 *
 *    fMoFBiomassD
 *       On output, contains the MoF Biomass less Decay at the age specified.
 *
 *    fMoFBiomassDW
 *       On output, contains the MoF Biomass less Decay, Waste at the age
 *       specified.
 *
 *    fMoFBiomassDWB
 *       On output, contains the MoF Biomass less Decay, Waste and Breakage at
 *       the age specified.
 *
 *    polyHandle
 *       The handle to the polygon for which you want the MoF biomass.
 *
 *    sLayerID
 *       The particular layer for which you want the layer information.
 *       If NULL or "", the last referenced layer will be used.
 *
 *    sSpeciesCode
 *       The species code for which you wish the MoF biomass.
 *
 *    fTotalAge
 *       The total age of the stand for which you want the MoF biomass 
 *       information.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully obtained the projected values at the specified age.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied, or is inconsistent.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       Unable to locate the requested layer.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       The requested species could not be located in the stand.
 *
 *    V7EXT_ERR_CORELIBRARYERROR
 *       The interaction with the underlying VDYP7CORE Library has failed.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon must be projected before projected values can be
 *       retrieved.
 *
 *    V7EXT_ERR_LAYERNOTPROCESSED
 *       The requested layer was not projected and therefore projected 
 *       MoF biomass information is not available.
 *
 *
 *	Remarks
 *	-------
 *
 *    Note that certain layers may not have been processed.  As a result,
 *    those layers may result in no MoF biomass despite the presence of
 *    MoF biomass on other layers.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetProjectedLayerSpeciesMoFBiomass( SWF32 *               fMoFBiomassWS,
                                          SWF32 *               fMoFBiomassCU,
                                          SWF32 *               fMoFBiomassD,
                                          SWF32 *               fMoFBiomassDW,
                                          SWF32 *               fMoFBiomassDWB,
                                          V7ExtPolygonHandle    polyHandle,
                                          SWChar const *        sLayerID,
                                          SWChar const *        sSpeciesCode,
                                          SWF32                 fTotalAge );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetNumLayers
 *	==================
 *
 *		Returns the count of the currently defined layers.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle you want a layer count from.
 *
 *
 *	Return Value
 *	------------
 *
 *		The count of currently defined layers.
 *    -1 indicates an error.
 *
 */


SWI32    ENV_IMPORT_STDCALL
V7Ext_GetNumLayers( V7ExtPolygonHandle     polyHandle );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetNumSpecies
 *	===================
 *
 *		Gets the number of species currently a part of the layer.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle for which you wish to query.
 *
 *    sLayerID
 *       The specific layer for which we want the species count.
 *       If NULL or "", the last referenced layer will be used.
 *
 *
 *	Return Value
 *	------------
 *
 *		A count of the species added to the layer.
 *
 *    (SWI32) V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters are invalid.
 *
 *    (SWI32) V7EXT_ERR_LAYERNOTFOUND
 *       Could not locate the requested layer.
 *
 *
 *	Remarks
 *	-------
 *
 *		Counts the number of species added to the specific layer.
 *
 */


SWI32    ENV_IMPORT_STDCALL
V7Ext_GetNumSpecies( V7ExtPolygonHandle   polyHandle,
                     SWChar const *       sLayerID );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetNumSpeciesGroups
 *	=========================
 *
 *		Gets the number of species groups currently a part of the layer.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle for which you wish to query.
 *
 *    sLayerID
 *       The specific layer for which we want the species count.
 *       If NULL or "", the last referenced layer will be used.
 *
 *
 *	Return Value
 *	------------
 *
 *		A count of the species groups added to the layer.
 *
 *    (SWI32) V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters are invalid.
 *
 *    (SWI32) V7EXT_ERR_LAYERNOTFOUND
 *       Could not locate the requested layer.
 *
 *
 *	Remarks
 *	-------
 *
 *		Counts the number of species groups added to the specific layer.
 *
 */


SWI32    ENV_IMPORT_STDCALL
V7Ext_GetNumSpeciesGroups( V7ExtPolygonHandle   polyHandle,
                           SWChar const *       sLayerID );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetSpeciesGroupName
 * V7Ext_VB_GetSpeciesGroupName
 *	============================
 *
 *		Returns the requested species group name.
 *
 *
 *	Parameters
 *	----------
 *
 *		buffer     (VB Version only)
 *			The buffer into which the string is to be placed.
 *       Must not be NULL
 *
 *    bufferLen  (VB Version only)
 *       Input:  The maximum length of the 'buffer' to store data.
 *       Output: The actual amount of version string data stored in 'buffer'.
 *
 *		polyHandle
 *			The polygon handle for which you want the species group name.
 *
 *    sLayerID
 *       The layer from which you want the species group name.
 *       If NULL or "", the last referenced layer will be used.
 *
 *    iSpeciesGroupNum
 *       The species group number for which you want the species group
 *       name.
 *
 *       This number must range from 0 to (V7Ext_GetNumSpeciesGroups - 1)
 *
 *    iSpeciesSorting
 *       The species ordering to request species from.
 *
 *
 *	Return Value
 *	------------
 *
 *		The name of the species group corresponding to the requested data.
 *    NULL if the group could not be determined.
 *
 *
 *	Remarks
 *	-------
 *
 *		Species groups are returned in increasing alphabetical order.
 *
 */


SWChar const *    ENV_IMPORT_STDCALL
V7Ext_GetSpeciesGroupName( V7ExtPolygonHandle   polyHandle,
                           SWChar const *       sLayerID,
                           V7ExtSpeciesIndex    iSpeciesGroupNum,
                           V7ExtSpeciesSorting  iSpeciesSorting );


void     ENV_IMPORT_STDCALL
V7Ext_VB_GetSpeciesGroupName( SWChar *             buffer,
                              SWI32 *              bufferLen,
                              V7ExtPolygonHandle   polyHandle,
                              SWChar const *       sLayerID,
                              SWI32                iSpeciesGroupNum,
                              SWI32                iSpeciesSorting );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedSpeciesPercent
 *	================================
 *
 *		Returns the projected percent for a particular species in the stand.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle for which you want the species group name.
 *
 *    sLayerID
 *       The layer from which you want the species group name.
 *       If NULL or "", the last referenced layer will be used.
 *
 *    fTotalAge
 *       The projected age at which you want the species percent for.
 *
 *    sSpeciesName
 *       The species name for which you want the projected stand percent.
 *       This name must correspond to a species in the stand.
 *
 *
 *	Return Value
 *	------------
 *
 *		The percent composition of the species at the specified age.
 *    On success, this will range from 0.0 to 100.0 percent.
 *
 *    (SWF32) V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters caused problems.
 *
 *    (SWF32) V7EXT_ERR_INCORRECTSTATE
 *       The polygon must be projected before projected values can be
 *       retrieved.
 *
 *    (SWF32) V7EXT_ERR_LAYERNOTFOUND
 *       The requested layer is not a part of the stand.
 *
 *    (SWF32) V7EXT_ERR_SPECIESNOTFOUND
 *       The requested species is not a member of the stand.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */

SWF32    ENV_IMPORT_STDCALL
V7Ext_GetProjectedSpeciesPercent( V7ExtPolygonHandle    polyHandle,
                                  SWChar const *        sLayerID,
                                  SWF32                 fTotalAge,
                                  SWChar const *        sSpeciesName );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedSpeciesGroupPercent
 *	=====================================
 *
 *		Returns the projected species group percent for the stand.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle for which you want the species group name.
 *
 *    sLayerID
 *       The layer from which you want the species group name.
 *       If NULL or "", the last referenced layer will be used.
 *
 *    fTotalAge
 *       The projected age at which you want the species percent for.
 *
 *    iSP0Index
 *       The VDYP7 Species Number for which you want the species group
 *       name.
 *
 *       This number must range from 0 to (vdyp7core_getnumspecies() - 1)
 *
 *
 *	Return Value
 *	------------
 *
 *		The percent composition of the species group at the specified age.
 *
 *    (SWF32) V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters caused problems.
 *
 *    (SWF32) V7EXT_ERR_INCORRECTSTATE
 *       The polygon must be projected before projected values can be
 *       retrieved.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */

SWF32    ENV_IMPORT_STDCALL
V7Ext_GetProjectedSpeciesGroupPercent( V7ExtPolygonHandle    polyHandle,
                                       SWChar const *        sLayerID,
                                       SWF32                 fTotalAge,
                                       SWI32                 iSP0Index );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_InitialProcessingReturnCode
 *	=================================
 *
 *		Obtains the internal return code from the VDYP7CORE library resulting
 *    from initial processing.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle to obtain the return code for.
 *
 *
 *	Return Value
 *	------------
 *
 *		The return code from VDYP7CORE initial processing.
 *    -9999 indicates the return code could not be determined.
 *
 *
 *	Remarks
 *	-------
 *
 *		These results originate from processing from either FIPSTART or
 *    VRISTART.
 *
 */


SWI32    ENV_IMPORT_STDCALL
V7Ext_InitialProcessingReturnCode( V7ExtPolygonHandle    polyHandle );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_AdjustmentProcessingReturnCode
 *	====================================
 *
 *		Obtains the internal return code from the VDYP7CORE library resulting
 *    from the adjustment processing.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle to obtain the return code for.
 *
 *
 *	Return Value
 *	------------
 *
 *		The return code from VDYP7CORE initial processing.
 *    -9999 indicates the return code could not be determined.
 *
 *
 *	Remarks
 *	-------
 *
 *		These results originate from processing from VRIADJST.
 *
 */


SWI32    ENV_IMPORT_STDCALL
V7Ext_AdjustmentProcessingReturnCode( V7ExtPolygonHandle    polyHandle );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_PolygonProjectionReturnCode
 *	=================================
 *
 *		Obtains the internal return code from the VDYP7CORE library resulting
 *    from projecting the polygon.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle to obtain the return code for.
 *
 *
 *	Return Value
 *	------------
 *
 *		The internal return code from VDYP7CORE projection processing.
 *    -9999 indicates the return code could not be determined.
 *
 *
 *	Remarks
 *	-------
 *
 *		These results originate from processing from either VRIADJST,
 *    VDYP7, or VDYPBACK.
 *
 */


SWI32    ENV_IMPORT_STDCALL
V7Ext_PolygonProjectionReturnCode( V7ExtPolygonHandle    polyHandle );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetSpeciesName
 * V7Ext_VB_GetSpeciesName
 *	=======================
 *
 *		Returns the requested species name.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle for which you want the species group name.
 *
 *    sLayerID
 *       The layer from which you want the species group name.
 *       If NULL or "", the last referenced layer will be used.
 *
 *    iSpeciesNum
 *       The species number for which you want the species name.
 *
 *       This number must range from V7EXT_SpcsNdx_FIRST to
 *       (V7Ext_GetNumSpecies - 1)
 *
 *    iSpeciesSorting
 *       The species ordering to request species from.
 *
 *
 *	Return Value
 *	------------
 *
 *		The name of the species corresponding to the requested data.
 *    NULL if the group could not be determined.
 *
 *
 *	Remarks
 *	-------
 *
 *		Species are returned in decreasing species percent.
 *
 */


SWChar const *    ENV_IMPORT_STDCALL
V7Ext_GetSpeciesName( V7ExtPolygonHandle   polyHandle,
                      SWChar const *       sLayerID,
                      V7ExtSpeciesIndex    iSpeciesNum,
                      V7ExtSpeciesSorting  iSpeciesSorting );




void              ENV_IMPORT_STDCALL
V7Ext_VB_GetSpeciesName( SWChar *             buffer,
                         SWI32 *              bufferLen,
                         V7ExtPolygonHandle   polyHandle,
                         SWChar const *       sLayerID,
                         SWI32                iSpeciesNum,
                         SWI32                iSpeciesSorting );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetSpeciesComponent
 *	=========================
 *
 *		Returns all supplied and derived information about the species
 *    component.
 *
 *
 *	Parameters
 *	----------
 *
 *    iSpcsCode
 *       On output, holds the species code corresponding to the returned
 *       species.  This species code is compatible with the SiteTools library.
 *
 *    fSpcsPcnt
 *       On output, holds the species percent of the species component when
 *       it was added to the layer.
 *
 *    fTotalAge
 *       On output, holds the total age of the species as it was supplied or
 *       derived from other parameters.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    fBreastHeightAge
 *       On output, holds the breast height age of the species as it was
 *       supplied or derived from other parameters.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    fDominantHeight
 *       On output, holds the dominant height of the species as it was
 *       supplied or derived from other parameters.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    fSI
 *       On output, holds the BHA50 Site Index of the species as it was
 *       supplied or derived from other parameters.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    fYTBH
 *       On output, holds the BHA50 Years to Breast Height of the species
 *       as it was supplied or derived from other parameters.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    iSiteCurveNum
 *       On output, holds the SiteTools library Site Curve number as it
 *       was supplied or derived from other species and layer parameters.
 *
 *       Will hold -9 if this value is not known.
 *
 *		polyHandle
 *			The the polygon handle for which you are querying species
 *       information.
 *
 *    sLayerID
 *       The specific layer within the polygon for which you wish to query
 *       species information.
 *
 *       "P" indicates the primary layer.
 *       NULL or "" indicates the last referenced layer.
 *
 *    speciesNum
 *       The species number for which you wish the information sorted by
 *       decreasing species percent.
 *
 *       Ranges from V7EXT_SpcsNdx_FIRST to (V7Ext_GetNumSpecies - 1)
 *
 *    speciesSorting
 *       The species ordering to request species from.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully located the species information.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters were not supplied or are invalid.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       The requested layer was not found.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       Unable to locate the species you requested.
 *
 *
 *	Remarks
 *	-------
 *
 *		Species are sorted by decreasing species percent as supplied when
 *    the species was added to the layer.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetSpeciesComponent( SWI16 *              iSpcsCode,
                           SWF32 *              fSpcsPcnt,
                           SWF32 *              fTotalAge,
                           SWF32 *              fBreastHeightAge,
                           SWF32 *              fDominantHeight,
                           SWF32 *              fSI,
                           SWF32 *              fYTBH,
                           SWI32 *              iSiteCurveNum,
                           V7ExtPolygonHandle   polyHandle,
                           SWChar const *       sLayerID,
                           V7ExtSpeciesIndex    speciesNum,
                           V7ExtSpeciesSorting  speciesSorting );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetSpeciesGroupComponent
 *	==============================
 *
 *		Returns all supplied and derived information about the species
 *    group component.
 *
 *
 *	Parameters
 *	----------
 *
 *    iSpcsCode
 *       On output, holds the species code corresponding to the returned
 *       species group.  This species code is compatible with the SiteTools
 *       library.
 *
 *    fSpcsPcnt
 *       On output, holds the species group percent of the species group
 *       component after all species have been added to the layer.
 *
 *    fTotalAge
 *       On output, holds the total age of the species group after combining
 *       all species into this species group.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    fBreastHeightAge
 *       On output, holds the breast height age of the species group after
 *       combining all species into this species group.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    fDominantHeight
 *       On output, holds the dominant height of the species group after
 *       combining all species into this species group.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    fSI
 *       On output, holds the BHA50 Site Index of the species group after
 *       combining all species into this species group.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    fYTBH
 *       On output, holds the BHA50 Years to Breast Heightdominant height
 *       of the species group after  combining all species into this species
 *       group.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    iSiteCurveNum
 *       On output, holds the SiteTools library Site Curve of the species
 *       group after combining all species into this species group.
 *
 *       Will hold -9 if this value is not known.
 *
 *		polyHandle
 *			The the polygon handle for which you are querying species
 *       information.
 *
 *    sLayerID
 *       The specific layer within the polygon for which you wish to query
 *       species information.
 *
 *       "P" indicates the primary layer.
 *       NULL or "" indicates the last referenced layer.
 *
 *    speciesGrpNum
 *       The species group number for which you wish the information.
 *       Ranges from 0 to (V7Ext_GetNumSpeciesGroups - 1).
 *
 *    iSpeciesSorting
 *       The species ordering to request species from.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully located the species group information.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters were not supplied or are invalid.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       The requested layer was not found.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       Unable to locate the species you requested.
 *
 *
 *	Remarks
 *	-------
 *
 *		Species groups are sorted by decreasing species percent or by
 *    increasing alphabetical after combining all species into species
 *    groups.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetSpeciesGroupComponent( SWI16 *              iSpcsCode,
                                SWF32 *              fSpcsPcnt,
                                SWF32 *              fTotalAge,
                                SWF32 *              fBreastHeightAge,
                                SWF32 *              fDominantHeight,
                                SWF32 *              fSI,
                                SWF32 *              fYTBH,
                                SWI32 *              iSiteCurveNum,
                                V7ExtPolygonHandle   polyHandle,
                                SWChar const *       sLayerID,
                                V7ExtSpeciesIndex    speciesNum,
                                V7ExtSpeciesSorting  iSpeciesSorting );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetNumSiteSpecies
 *	=======================
 *
 *		Returns the number of site species currently defined in the stand.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle for which you wish to query.
 *
 *    sLayerID
 *       The specific layer for which we want the species count.
 *       If NULL or "", the last referenced layer will be used.
 *
 *
 *	Return Value
 *	------------
 *
 *		A count of the site species in the requested layer.
 *
 *    (SWI32) V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters are invalid.
 *
 *    (SWI32) V7EXT_ERR_LAYERNOTFOUND
 *       Could not locate the requested layer.
 *
 *
 *	Remarks
 *	-------
 *
 *		Counts the number of site species currently a part of the
 *    requested layer.
 *
 *    Site Species result as a consequence of the normal process of adding
 *    species into the stand; you do not have to add or identify species
 *    as being site species.
 *
 *    Typically, the number of site species is always the same as the number
 *    of species groups in the layer.  However, there are circumstances when
 *    this count may be lower depending on the individual components of
 *    the stand.
 *
 */


SWI32    ENV_IMPORT_STDCALL
V7Ext_GetNumSiteSpecies( V7ExtPolygonHandle   polyHandle,
                         SWChar const *       sLayerID );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetNumSiteSpeciesGroups
 *	=============================
 *
 *		Returns the number of site species groups currently defined in the stand.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle for which you wish to query.
 *
 *    sLayerID
 *       The specific layer for which we want the species count.
 *       If NULL or "", the last referenced layer will be used.
 *
 *
 *	Return Value
 *	------------
 *
 *		A count of the site species groups in the requested layer.
 *
 *    (SWI32) V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters are invalid.
 *
 *    (SWI32) V7EXT_ERR_LAYERNOTFOUND
 *       Could not locate the requested layer.
 *
 *
 *	Remarks
 *	-------
 *
 *		Counts the number of site species groups currently a part of the
 *    requested layer.
 *
 *    Site Species result as a consequence of the normal process of adding
 *    species into the stand; you do not have to add or identify species
 *    as being site species.
 *
 *    Typically, the number of site species is always the same as the number
 *    of species groups in the layer.  However, there are circumstances when
 *    this count may be lower depending on the individual components of
 *    the stand.
 *
 */


SWI32    ENV_IMPORT_STDCALL
V7Ext_GetNumSiteSpeciesGroups( V7ExtPolygonHandle   polyHandle,
                               SWChar const *       sLayerID );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetSiteSpeciesComponent
 *	=============================
 *
 *		Returns all supplied and derived information about the requested site
 *    species component.
 *
 *
 *	Parameters
 *	----------
 *
 *    iSpcsCode
 *       On output, holds the species code corresponding to the returned
 *       site species.  This species code is compatible with the SiteTools
 *       library.
 *
 *    fSpcsPcnt
 *       On output, holds the species percent of the site species component
 *       when it was added to the layer.
 *
 *    fTotalAge
 *       On output, holds the total age of the species as it was supplied or
 *       derived from other parameters.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    fBreastHeightAge
 *       On output, holds the breast height age of the species as it was
 *       supplied or derived from other parameters.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    fDominantHeight
 *       On output, holds the dominant height of the species as it was
 *       supplied or derived from other parameters.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    fSI
 *       On output, holds the BHA50 Site Index of the species as it was
 *       supplied or derived from other parameters.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    fYTBH
 *       On output, holds the BHA50 Years to Breast Height of the species
 *       as it was supplied or derived from other parameters.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    iSiteCurveNum
 *       On output, holds the SiteTools library Site Curve number as it
 *       was supplied or derived from other species and layer parameters.
 *
 *       Will hold -9 if this value is not known.
 *
 *		polyHandle
 *			The the polygon handle for which you are querying species
 *       information.
 *
 *    sLayerID
 *       The specific layer within the polygon for which you wish to query
 *       species information.
 *
 *       "P" indicates the primary layer.
 *       NULL or "" indicates the last referenced layer.
 *
 *    siteSpeciesNum
 *       The site species number for which you wish the information.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully located the species information.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters were not supplied or are invalid.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       The requested layer was not found.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       Unable to locate the species you requested.
 *
 *
 *	Remarks
 *	-------
 *
 *    The site species is defined to be the leading species within the
 *    site species group.  Refer to the routine
 *    'V7Ext_GetSiteSpeciesGroupComponent' for details on how this value is
 *    determined.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetSiteSpeciesComponent( SWI16 *              iSpcsCode,
                               SWF32 *              fSpcsPcnt,
                               SWF32 *              fTotalAge,
                               SWF32 *              fBreastHeightAge,
                               SWF32 *              fDominantHeight,
                               SWF32 *              fSI,
                               SWF32 *              fYTBH,
                               SWI32 *              iSiteCurveNum,
                               V7ExtPolygonHandle   polyHandle,
                               SWChar const *       sLayerID,
                               V7ExtSpeciesIndex    siteSpeciesNum );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetSiteSpeciesGroupComponent
 *	==================================
 *
 *		Returns all supplied and derived information about the requested site
 *    species component.
 *
 *
 *	Parameters
 *	----------
 *
 *    iSpcsCode
 *       On output, holds the species code corresponding to the returned
 *       site species.  This species code is compatible with the SiteTools
 *       library.
 *
 *    iIsAnAggregate
 *       On output, indicates whether or not the species group is an aggregate
 *       or not.
 *
 *       TRUE     indicates the site species group is an aggregate of one
 *                or more other species groups.
 *
 *       FALSE    indicates the site species group is not an aggregate.
 *                This species group stands alone.
 *
 *    fSpcsPcnt
 *       On output, holds the species percent of the site species component
 *       when it was added to the layer.
 *
 *       If the site species group is an aggregate, this routine returns the
 *       percent total for the aggregate.  Otherwise it returns the percent
 *       for the specific SP0.
 *
 *    fTotalAge
 *       On output, holds the total age of the species as it was supplied or
 *       derived from other parameters.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    fBreastHeightAge
 *       On output, holds the breast height age of the species as it was
 *       supplied or derived from other parameters.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    fDominantHeight
 *       On output, holds the dominant height of the species as it was
 *       supplied or derived from other parameters.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    fSI
 *       On output, holds the BHA50 Site Index of the species as it was
 *       supplied or derived from other parameters.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    fYTBH
 *       On output, holds the BHA50 Years to Breast Height of the species
 *       as it was supplied or derived from other parameters.
 *
 *       Will hold -9.0 if this value is not known.
 *
 *    iSiteCurveNum
 *       On output, holds the SiteTools library Site Curve number as it
 *       was supplied or derived from other species and layer parameters.
 *
 *       Will hold -9 if this value is not known.
 *
 *		polyHandle
 *			The the polygon handle for which you are querying species
 *       information.
 *
 *    sLayerID
 *       The specific layer within the polygon for which you wish to query
 *       species information.
 *
 *       "P" indicates the primary layer.
 *       NULL or "" indicates the last referenced layer.
 *
 *    siteSpeciesNum
 *       The site species number for which you wish the information.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully located the species information.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters were not supplied or are invalid.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       The requested layer was not found.
 *
 *    V7EXT_ERR_SPECIESNOTFOUND
 *       Unable to locate the species you requested.
 *
 *
 *	Remarks
 *	-------
 *
 *    Site Species Group is similar in concept to Species Group except
 *    that the rules for ranking Species Groups is slightly different
 *    that for Site Species Groups.
 *
 *    Site Species Groups are ranked by Species Group Percent, but also
 *    have the added constraint of certain groups being combined together
 *    for the purposes of Site Species.
 *
 *    When two species groups are combined, their respective percents
 *    combine.
 *
 *    When querying the site species group, the first encountered species
 *    group is returned, not secondary groups.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetSiteSpeciesGroupComponent( SWI16 *              iSpcsCode,
                                    SWI16 *              iIsAnAggregate,
                                    SWF32 *              fSpcsPcnt,
                                    SWF32 *              fTotalAge,
                                    SWF32 *              fBreastHeightAge,
                                    SWF32 *              fDominantHeight,
                                    SWF32 *              fSI,
                                    SWF32 *              fYTBH,
                                    SWI32 *              iSiteCurveNum,
                                    V7ExtPolygonHandle   polyHandle,
                                    SWChar const *       sLayerID,
                                    V7ExtSpeciesIndex    siteSpeciesNum );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_NumProcessingMessages
 *	===========================
 *
 *		Determines the number of processing messages generated since the last
 *    time a new polygon has started.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle to which there may be messages associated with it.
 *
 *
 *	Return Value
 *	------------
 *
 *		The number of messages available to be processed.
 *    -1 indicates an error.
 *
 *
 *	Remarks
 *	-------
 *
 *		These messages are reset each time the routine 'V7Ext_StartNewPolygon'
 *    is called.
 *
 */


SWI32    ENV_IMPORT_STDCALL
V7Ext_NumProcessingMessages( V7ExtPolygonHandle    polyHandle );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProcessingMessage
 *	==========================
 *
 *		Returns an individual message associated with the polygon.
 *
 *
 *	Parameters
 *	----------
 *
 *    sMessageLayerID
 *			On output, this parameter will point to the layer identifier
 *       associated with this message.
 *
 *       If "", this message is associated with the polygon as a whole.
 *
 *    iMessageErrorCode
 *       On output, returns the error code associated with the operation
 *       which generated the message.
 *
 *    iMessageSeverity
 *       On output, will contain the severity of the identified message.
 *
 *    iMessageCode
 *       On output, indicates the numeric code for the message text.
 *
 *    sMessageText
 *       On output, this parameter will point to the actual text of the
 *       message.
 *
 *    polyHandle
 *       Identifies the polygon from which w=you wish a specific message.
 *
 *    iMsgNum
 *       The actual message number which you wish to retrieve.
 *       This value must range from 0 to 'V7Ext_NumProcessingMessages - 1'.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully retrieved the message requested.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied or they are out
 *       of range.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


V7ExtReturnCode      ENV_IMPORT_STDCALL
V7Ext_GetProcessingMessage( SWChar const **        sMessageLayerID,
                            V7ExtReturnCode *      iMessageErrorCode,
                            V7ExtMessageSeverity * iMessageSeverity,
                            V7ExtMessageCode *     iMessageCode,
                            SWChar const **        sMessageText,
                            V7ExtPolygonHandle     polyHandle,
                            SWI32                  iMsgNum );





/*-----------------------------------------------------------------------------
 *
 * V7Ext_VB_GetProcessingMessage
 *	=============================
 *
 *		Returns an individual message associated with the polygon using the
 *    Visual Basic interface.
 *
 *
 *	Parameters
 *	----------
 *
 *    sLayerIDBuffer
 *			On output, the buffer pointed to by this parameter will hold
 *       the layer id associated with the message.
 *
 *       A zero length string will be returned if the message is associated
 *       with the polygon as a whole rather than a specific layer within
 *       the polygon.
 *
 *    iLayerIDBufLen
 *       On input, specifies the maximum length of the Layer ID buffer to
 *       hold text.
 *
 *       On output, specifies the actual length of the layer identifier that
 *       was placed into the buffer.  If 0, this message is not associated
 *       with a specific layer.
 *
 *    iMessageErrorCode
 *       On output, returns the error code associated with the operation
 *       which generated the message.
 *
 *    iMessageSeverity
 *       On output, will contain the severity of the identified message.
 *
 *    iMessageCode
 *       On output, the buffer pointed to by this parameter will hold
 *       the numeric equivalent of the text also returned.
 *
 *    sMessageTextBuffer
 *       On output, the buffer pointed to by this parameter will hold
 *       the actual text of this message.
 *
 *    iMessageTextBufLen
 *       On input, specifies the maximum length of the Message Text buffer
 *       to hold text.
 *
 *       On output, specifies the actual length of the message text that
 *       was placed into the buffer.
 *
 *    polyHandle
 *       Identifies the polygon from which you wish a specific message.
 *
 *    iMsgNum
 *       The actual message number which you wish to retrieve.
 *       This value must range from 0 to 'V7Ext_NumProcessingMessages - 1'.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully retrieved the message requested.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied or they are out
 *       of range.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


V7ExtReturnCode      ENV_IMPORT_STDCALL
V7Ext_VB_GetProcessingMessage( SWChar *               sLayerIDBuffer,
                               SWI32 *                iLayerIDBufLen,
                               V7ExtReturnCode *      iMessageErrorCode,
                               V7ExtMessageSeverity * iMessageSeverity,
                               V7ExtMessageCode *     iMessageCode,
                               SWChar *               sMessageTextBuffer,
                               SWI32 *                iMessageTextBufLen,
                               V7ExtPolygonHandle     polyHandle,
                               SWI32                  iMsgNum );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_CompletedPolygonDefinition
 *	================================
 *
 *		Marks the end of the polygon definition modifications.
 *
 *
 *	Parameters
 *	----------
 *
 *    iLayerSummarizationMode
 *       On output, returns the Layer Summarization Mode used in processing
 *       the layers in the stand.
 *
 *		polyHandle
 *			The polygon handle you wish to mark as being completed as far
 *       as defining layers and species composition.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully marked the polygon as being defined.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the supplied parameters were missing or otherwise
 *       invalid.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon is in a state which would not allow the polygon to be
 *       defined or to be marked as having its definition finalized.
 *
 *
 *	Remarks
 *	-------
 *
 *		Once the polygon has been completely defined, internal actions which
 *    logically take place prior to initial processing such as combining
 *    layers or computing stockability takes place.
 *
 *    This routine is implicitly called if not already done when calling
 *    'V7Ext_PerformInitialProcessing'.
 *
 *    2003/11/21:
 *    Added code to pro-rate species percents to ensure they sum up to 100%
 *    as per Cam Bartam's Nov. 21, 2003 e-mail.
 *
 */

V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_CompletedPolygonDefinition( SWI32 *             iLayerSummarizationMode,
                                  V7ExtPolygonHandle  polyHandle );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_PolygonIsCoastal
 *	======================
 *
 *		Determines if the polygon is coastal or interior.
 *
 *
 *	Parameters
 *	----------
 *
 *    bIsCoastal
 *       The buffer into which to place the interior/coastal flag.
 *       On output:
 *          TRUE     Indicates the polygon is a coastal polygon.
 *          FALSE    Indicates the polygon is an interior polygon.
 *
 *       If the return code is not V7EXT_SUCCESS, the value of this parameter
 *       is undefined.
 *
 *		polygonHandle
 *			The polygon handle to be tested for interior or coastal residence.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully determined whether or not the polygon is interior or
 *       coastal.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters are invalid.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */


V7ExtReturnCode      ENV_IMPORT_STDCALL
V7Ext_PolygonIsCoastal( SWI16 *              bIsCoastal,
                        V7ExtPolygonHandle   polygonHandle );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_DetermineStandAgeAtYear
 *	=============================
 *
 *		Compute the total age of stand at the supplied year.
 *
 *
 *	Parameters
 *	----------
 *
 *		polygonHandle
 *			The polygon handle to be used.
 *
 *    year
 *       The year to compute the stand age at.
 *
 *
 *	Return Value
 *	------------
 *
 *		The total age of the stand at the specified year.
 *    or a value less than 0 indicating an error.
 *
 *    Possible errors are:
 *
 *    (SWF32) V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters were not supplied
 *
 *    (SWF32) V7EXT_ERR_LAYERNOTFOUND
 *       No primary layer could be found.
 *
 *    (SWF32) V7EXT_ERR_SPECIESNOTFOUND
 *       The leading species could not be found.
 *
 *    (SWF32) V7EXT_ERR_INVALIDSITEINFORMATION
 *       Either no reference age was associated with the species or
 *       no reference year was associated with the polygon.
 *
 *
 *	Remarks
 *	-------
 *
 *		The age of the leading species in the primary layer is computed
 *    and returned as the age of the stand.
 *
 */


SWF32    ENV_IMPORT_STDCALL
V7Ext_DetermineStandAgeAtYear( V7ExtPolygonHandle  polygonHandle,
                               SWI32               year );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_DetermineLayerAgeAtYear
 *	=============================
 *
 *		Compute the total age of layer at the supplied year.
 *
 *
 *	Parameters
 *	----------
 *
 *		polygonHandle
 *			The polygon handle to be used.
 *
 *    sLayerID
 *       The particular layer you wish to determine the calendar year for.
 *
 *    year
 *       The year to compute the stand age at.
 *
 *
 *	Return Value
 *	------------
 *
 *		The total age of the layer at the specified year.
 *    or a value less than 0 indicating an error.
 *
 *    Possible errors are:
 *
 *    (SWF32) V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters were not supplied
 *
 *    (SWF32) V7EXT_ERR_LAYERNOTFOUND
 *       The requested layer could be found.
 *
 *    (SWF32) V7EXT_ERR_SPECIESNOTFOUND
 *       The leading species could not be found.
 *
 *    (SWF32) V7EXT_ERR_INVALIDSITEINFORMATION
 *       Either no reference age was associated with the species or
 *       no reference year was associated with the polygon.
 *
 *
 *	Remarks
 *	-------
 *
 *		The age of the leading species in the requested layer is computed
 *    and returned as the age of the layer.
 *
 */


SWF32    ENV_IMPORT_STDCALL
V7Ext_DetermineLayerAgeAtYear( V7ExtPolygonHandle  polygonHandle,
                               SWChar const *      sLayerID,
                               SWI32               year );




/*-----------------------------------------------------------------------------
 *
 * V7Ext_PolygonReferenceYear
 *	==========================
 *
 *		Determine the year in which the polygon attributes were measured.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyInfo
 *			The polygon from which the Measurement Year is desired.
 *
 *
 *	Return Value
 *	------------
 *
 *		The year in which the polygon data was measured.
 *    -9 if the year could not be determined.
 *
 *
 *	Remarks
 *	-------
 *
 *		The measurement year is determined to be the later of:
 *       Polygon Reference Year
 *       Year of Death (if supplied)
 *
 */

SWI32       ENV_EXPORT_STDCALL
V7Ext_PolygonReferenceYear( V7ExtPolygonHandle   polyInfo );




/*-----------------------------------------------------------------------------
 *
 * V7Ext_GetPolygonInfo
 *	====================
 *
 *		Returns information about the current polygon.
 *
 *
 *	Parameters
 *	----------
 *
 *    sDistrict
 *       On output, contains the map district responsible for the polygon.
 *       Maximum length defined by: V7EXT_MAX_LEN_DISTRICT
 *
 *    sMapSheet
 *       On output, contains the map sheet of the polygon.
 *       Maximum length defined by: V7EXT_MAX_LEN_MAPSHEET
 *
 *    sMapQuad
 *       On output, contains the map quad of the polygon.
 *       Maximum length defined by: V7EXT_MAX_LEN_MAP_QUAD
 *
 *    sMapSubQuad
 *       On output, contains the map sub-quad of the polygon.
 *       Maximum length defined by: V7EXT_MAX_LEN_MAP_SUBQUAD
 *
 *    iPolyNum
 *       On output, contains the polygon number within the map sheet.
 *
 *    iMeasurementYear
 *       On output, contains the year the polygon information was measured.
 *
 *    sFIZ
 *       On output, contains the Forest Inventory Zone of the polygon.
 *       Maximum length defined by: V7EXT_MAX_LEN_FIZ
 *
 *    sBEC
 *       On output, contains the BEC Zone of the polygon.
 *       Maximum length defined by: V7EXT_MAX_LEN_BEC
 *
 *    fPctStockableLand
 *       On output, contains the precent stockable land of the polygon.
 *
 *    sNonProdDescriptor
 *       On output, contains the non productive descriptor of the polygon.
 *       Maximum length defined by: V7EXT_MAX_LEN_NON_PROD_DESC
 *
 *    fYieldFactor
 *       On output, contains the multiplier for the volumes to adjust by.
 *
 *		polyHandle
 *			The polygon handle to retrieve information from.
 *       This handle must have previously been allocated with a call
 *       to 'V7Ext_AllocatePolygonDescriptor'.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully retrieved the polygon information.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       The polyHandle parameter was not supplied.
 *
 *
 *	Remarks
 *	-------
 *
 *		Some of the information returned may not match exactly that which
 *    was originally supplied if the data was modified or filled in to
 *    support processing.
 *
 *    Output parameters for which you supply NULL for the output parameter
 *    will be ignored.
 *
 *    All output buffers are assumed to be large enough to accomodate the
 *    data being stored in them.  Further, string parameters must be 1 character
 *    larger than the stated buffer size to hold the string terminator.
 *
 */


V7ExtReturnCode    ENV_IMPORT_STDCALL
V7Ext_GetPolygonInfo( SWChar *             sDistrict,
                      SWChar *             sMapSheet,
                      SWChar *             sMapQuad,
                      SWChar *             sMapSubQuad,
                      SWU32 *              iPolyNum,
                      SWI32 *              iMeasurementYear,
                      SWChar *             sFIZ,
                      SWChar *             sBEC,
                      SWF32 *              fPctStockableLand,
                      SWChar *             sNonProdDescriptor,
                      SWF32 *              fYieldFactor ,
                      V7ExtPolygonHandle   polyHandle );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetLayerInfo
 *	==================
 *
 *		Retrieves information regarding a specific layer.
 *
 *
 *	Parameters
 *	----------
 *
 *    fMeasuredUtilLevel
 *       The utilization level the layer attributes were measured at.
 *
 *    fCC
 *       The crown closure of the layer.
 *
 *    fBA
 *       The basal area at the measured utilization level for this layer.
 *
 *    fTPH
 *       The Trees per Hectare at the measured utilization level for this
 *
 *    iEstimatedSISpcs
 *       The species associated with the estimated site index.  If no E_SI
 *       was supplied or the associated species is not known, then this
 *       parameter will hold -1.  This integer is can be converted into a
 *       species name using the SiteTools library.
 *
 *    fEstimatedSI
 *       The Estimated Site Index to use in case the leading species site
 *       index is not valid for some reason or not derivable due to other
 *       reasons.
 *
 *		polyHandle
 *			The polygon handle to retrieve layer information from.
 *
 *    sLayerID
 *       The specific layer identifier you are requesting information from.
 *       If NULL or "", the last requested layer will be retrieved.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully retrieved the layer information.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       The polygon handle was invalid.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       The requested layer could not be found.
 *
 *
 *	Remarks
 *	-------
 *
 *		Some of the information returned may not match exactly that which
 *    was originally supplied if the data was modified or filled in to
 *    support processing.
 *
 *    Output parameters for which you supply NULL for the output parameter
 *    will be ignored.
 *
 *    All output buffers are assumed to be large enough to accomodate the
 *    data being stored in them.  Further, string parameters must be 1 character
 *    larger than the stated buffer size to hold the string terminator.
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_GetLayerInfo( SWF32 *               fMeasuredUtilLevel,
                    SWF32 *               fCC,
                    SWF32 *               fBA,
                    SWF32 *               fTPH,
                    SWI32 *               iEstimatedSISpcs,
                    SWF32 *               fEstimatedSI,
                    V7ExtPolygonHandle    polyHandle,
                    SWChar const *        sLayerID );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_WasLayerProcessed
 *	=======================
 *
 *		This routine checks to see if this layer will be or has been processed.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The handle to the polygon definition.
 *
 *    sLayerID
 *       Identifies the layer for which you wish to test.
 *       If NULL or "", refers to the last used layer.
 *       If "P", refers to the primary "combined" layer.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Indicates the layer will be or has been processed or projected.
 *
 *    V7EXT_ERR_LAYERNOTPROCESSED
 *       Indicates the layer was not and will not be processed for one
 *       reason or another.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       One or more of the parameters was not supplied.
 *
 *    V7EXT_ERR_LAYERNOTFOUND
 *       The layer could not be located.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The polygon definition must have been completed, initial processing
 *       must have occurred, or the polygon must have been projected before
 *       this routine can be called.
 *
 *
 *	Remarks
 *	-------
 *
 *		This routine provides a quick check to see if a polygon layer has been
 *    processed (whether or not it was successfully processed is another
 *    question).
 *
 */


V7ExtReturnCode   ENV_IMPORT_STDCALL
V7Ext_WasLayerProcessed( V7ExtPolygonHandle  polyHandle,
                         SWChar const *      sLayerID );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetProjectedDomSpcsAgeAtYear
 *	==================================
 *
 *		For the supplied calendar year, returns the age of the species
 *    determined by VDYP7 to be the dominant species while projecting.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			parameter description
 *
 *    sLayerID
 *       The specific layer we wish to query.
 *       If NULL or "", the most recently requested layer will be used.
 *
 *    iYear
 *       The year to determine the age at.
 *       This year must be at least as great as the first year yields were
 *       projected after the call to 'V7Ext_V7Ext_PerformInitialProcessing'.
 *
 *       If this year is less than zero, the first year at which valid yields
 *       were produced will be used.
 *
 *
 *	Return Value
 *	------------
 *
 *		The age of the projected dominant species of the layer at the requested
 *    year.
 *
 *    -9.0 if the age could not be determined for any reason.
 *
 *
 *	Remarks
 *	-------
 *
 *		The projected dominant species is the species determined by the
 *    VDYP7 routines to be dominant at a particular year.  As a result,
 *    the dominant species could change from year to year and so the
 *    projected age returned may jump forwards and backwards as the
 *    dominant species changes.
 *
 */


SWF32    ENV_IMPORT_STDCALL
V7Ext_GetProjectedDomSpcsAgeAtYear( V7ExtPolygonHandle   polyHandle,
                                    SWChar const *       sLayerID,
                                    SWI32                iYear );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_SetInterfaceOptionInt
 *	===========================
 *
 *		Sets a particular interface option to a supplied integer.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle to which this option is to be applied.
 *
 *    interfaceOption
 *       The particular interface option to be set.
 *       While supplied as a 32 bit integer, the value of this parameter
 *       must correspond to one of the 'V7IntInterfaceOption' values.
 *
 *    newSetting
 *       The integer to set the parameter to.
 *
 *       For Enable/Disable options:
 *          0        Disables the option in question.
 *          non-0    Enables the option in question.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Indicates the layer will be or has been processed or projected.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       Indicates the inteface option was not recognized or there was
 *       no conversion from the supplied integral value to the actual
 *       data type for the Interface Option.
 *
 *
 *	Remarks
 *	-------
 *
 *		The option value being set applies only to the particular polygon
 *    handle specified.  Any other polygon handle will not be affected.
 *
 *    If the Interface Option requested is in fact not an integer, this
 *    routine will attempt to convert the supplied value to the appropriate
 *    type.  If no conversion is possible, an Invalid Parameter return code
 *    is returned.
 *
 */


V7ExtReturnCode     ENV_IMPORT_STDCALL
V7Ext_SetInterfaceOptionInt( V7ExtPolygonHandle    polyHandle,
                             V7ExtInterfaceOption  interfaceOption,
                             SWI32                 newSetting );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetInterfaceOptionInt
 *	===========================
 *
 *		Returns the current setting for a particular interface option.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle to which this option is to be applied.
 *
 *    interfaceOption
 *       The particular interface option to be set.
 *       While supplied as a 32 bit integer, the value of this parameter
 *       must correspond to one of the 'V7IntInterfaceOption' values.
 *
 *
 *	Return Value
 *	------------
 *
 *		The current setting for the specified Interface Option.
 *
 *    Return Value is undefined if:
 *       - the Interface Option is not recognized, or
 *       - there is no data type conversion from the stored value to
 *         an integer.
 *
 *
 *	Remarks
 *	-------
 *
 *		The option value being set applies only to the particular polygon
 *    handle specified.  Any other polygon handle will not be affected.
 *
 *    If the specified Interface Option is not an integer, this routine will
 *    attempt to convert the value for that option to an integer.
 *
 */


SWI32     ENV_IMPORT_STDCALL
V7Ext_GetInterfaceOptionInt( V7ExtPolygonHandle    polyHandle,
                             V7ExtInterfaceOption  interfaceOption );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_SetInterfaceOptionString
 *	==============================
 *
 *		Sets a particular interface option to a supplied string value.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle to which this option is to be applied.
 *
 *    interfaceOption
 *       The particular interface option to be set.
 *       While supplied as a 32 bit integer, the value of this parameter
 *       must correspond to one of the 'V7IntInterfaceOption' values.
 *
 *    newSetting
 *       The string to set the parameter to.  A copy of the supplied string
 *       is made and stored internally.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Indicates the layer will be or has been processed or projected.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       Indicates the inteface option was not recognized or there was
 *       no conversion from the supplied string value to the actual
 *       data type for the Interface Option.
 *
 *
 *	Remarks
 *	-------
 *
 *		The option value being set applies only to the particular polygon
 *    handle specified.  Any other polygon handle will not be affected.
 *
 *    If the Interface Option requested is in fact not a string, this
 *    routine will attempt to convert the supplied value to the appropriate
 *    type.  If no conversion is possible, an Invalid Parameter return code
 *    is returned.
 *
 */


V7ExtReturnCode     ENV_IMPORT_STDCALL
V7Ext_SetInterfaceOptionString( V7ExtPolygonHandle    polyHandle,
                                V7ExtInterfaceOption  interfaceOption,
                                SWChar const *        newSetting );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_GetInterfaceOptionString
 *	==============================
 *
 *		Returns the current setting for a particular interface option.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle to which this option is to be applied.
 *
 *    interfaceOption
 *       The particular interface option to be set.
 *       While supplied as a 32 bit integer, the value of this parameter
 *       must correspond to one of the 'V7IntInterfaceOption' values.
 *
 *
 *	Return Value
 *	------------
 *
 *		The current setting for the specified Interface Option.
 *    Care should be taken regarding the use of this return value as it will
 *    represent an internal buffer and should not be modified, free'd or
 *    otherwise manipulated.
 *
 *    Return Value is NULL if:
 *       - the Interface Option is not recognized, or
 *       - there is no data type conversion from the stored value to
 *         a string.
 *
 *
 *	Remarks
 *	-------
 *
 *		The option value being set applies only to the particular polygon
 *    handle specified.  Any other polygon handle will not be affected.
 *
 *    If the specified Interface Option is not an integer, this routine will
 *    attempt to convert the value for that option to an integer.
 *
 */


SWChar const *     ENV_IMPORT_STDCALL
V7Ext_GetInterfaceOptionString( V7ExtPolygonHandle    polyHandle,
                                V7ExtInterfaceOption  interfaceOption );




/*-----------------------------------------------------------------------------
 *
 *	V7Ext_ReloadProjectedData
 *	=========================
 *
 *		Causes the projected data to be reloaded.
 *
 *
 *	Parameters
 *	----------
 *
 *		polygonHandle
 *			The polygon handle with projected results to be reloaded and
 *       interpreted.
 *
 *
 *	Return Value
 *	------------
 *
 *		V7EXT_SUCCESS
 *       Successfully reloaded and interpreted the projected data from VDYP7.
 *
 *    V7EXT_ERR_INVALIDPARAMETER
 *       The polygon handle parameter was not supplied or is invalid.
 *
 *    V7EXT_ERR_INCORRECTSTATE
 *       The requested operation is not possible in the current polygon
 *       state.  The polygon must have been successfully projected before
 *       this routine may be called.
 *
 *
 *	Remarks
 *	-------
 *
 *		This routine would typically be called after:
 *       - projecting a stand,
 *       - taking the desired projected values from the projection,
 *
 *    Often it is desirable to change the reporting utilization level without
 *    having to reproject the entire stand.  After performing the above two
 *    steps, the caller could:
 *       - reset species utilization levels
 *       - call this routine to reload the projected results at the new
 *         utilization level.
 *
 */



V7ExtReturnCode     ENV_IMPORT_STDCALL
V7Ext_ReloadProjectedData( V7ExtPolygonHandle    polyHandle );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_DetermineLayerYearOfDeath
 *	===============================
 *
 *		Retrieve the Calendar Year the layer was killed.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The polygon handle to query for a year of death.
 *
 *    sLayerID
 *       The particular layer within the polygon to request the year of death.
 *
 *
 *	Return Value
 *	------------
 *
 *		The calendar year representing the year of death for that layer.
 *
 *    -9 if the layer is still alive, the layer was not found or one or more
 *       of the parameters were illegal or missing.
 *
 *
 *	Remarks
 *	-------
 *
 *		The Dead Layer will also be marked with the VDYP7 Processing Layer Type
 *    of "VDYP7_sDEADLAYER"
 *
 */


SWI32    ENV_IMPORT_STDCALL
V7Ext_DetermineLayerYearOfDeath( V7ExtPolygonHandle   polyHandle,
                                 SWChar const *       sLayerID );





/*-----------------------------------------------------------------------------
 *
 *	V7Ext_DetermineLayerStockability
 *	================================
 *
 *		For layers processed by VDYP7, determines the Polygon Percent
 *    Stockability attributed to that layer for the projection.
 *
 *
 *	Parameters
 *	----------
 *
 *		polyHandle
 *			The Polygon Handle to query for Layer Stockability.
 *
 *    sLayerID
 *       The Layer ID for the specific layer to get projected
 *       stockability for.
 *
 *
 *	Return Value
 *	------------
 *
 *		The Percent Stockabilkity used for the projection of the
 *    requested layer.
 *
 *    -9.0 if the Percent Stockability could not be determined
 *         or the layer was not projected for any reason.
 *
 *
 *	Remarks	(Optional Heading)
 *	-------
 *
 *		Remarks, warnings, special conditions to be aware of, etc.
 *
 */

SWF32    ENV_IMPORT_STDCALL
V7Ext_DetermineLayerStockability( V7ExtPolygonHandle     polyHandle,
                                  SWChar const *         sLayerID );




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

