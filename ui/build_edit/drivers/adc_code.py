ADC_H_TEMPLATE = '''#ifndef ADC_H_
#define ADC_H_

/**
 * Developer: Aruvi B & Auroshaa A from CreamCollar
 * @file Adc.h
 * @brief ADC Configuration Header File
 * @details Generated ADC Configuration Header from ARXML
 * Generated from ARXML: adc_config.arxml
 */

#include "Std_Types.h"

/* ============================ */
/*      AUTOSAR Version Info    */
/* ============================ */
#define ADC_AR_RELEASE_MAJOR_VERSION   (4U)
#define ADC_AR_RELEASE_MINOR_VERSION   (4U)
#define ADC_AR_RELEASE_REVISION_VERSION (0U)

#define ADC_SW_MAJOR_VERSION           (1U)
#define ADC_SW_MINOR_VERSION           (0U)
#define ADC_SW_PATCH_VERSION           (0U)



/* ============================ */
/*          DEFINES             */
/* ============================ */
#define ADC_VENDOR_ID                  (1234U)
#define ADC_MODULE_ID                  (123U)
#define ADC_INSTANCE_ID                (0U)

/* Development error codes */
#define ADC_E_UNINIT                   (0x01U)
#define ADC_E_PARAM_GROUP              (0x02U)
#define ADC_E_ALREADY_INITIALIZED      (0x03U)
#define ADC_E_PARAM_CONFIG             (0x04U)

/* API Service IDs */
#define ADC_INIT_ID                    (0x00U)
#define ADC_DEINIT_ID                  (0x01U)
#define ADC_START_GROUP_CONVERSION_ID  (0x02U)
#define ADC_STOP_GROUP_CONVERSION_ID   (0x03U)
#define ADC_READ_GROUP_ID              (0x04U)
#define ADC_ENABLE_HARDWARE_TRIGGER_ID (0x05U)
#define ADC_DISABLE_HARDWARE_TRIGGER_ID (0x06U)
#define ADC_ENABLE_NOTIFICATION_ID     (0x07U)
#define ADC_DISABLE_NOTIFICATION_ID    (0x08U)
#define ADC_GET_GROUP_STATUS_ID        (0x09U)
#define ADC_GET_VERSION_INFO_ID        (0x0AU)
#define ADC_SETUP_RESULT_BUFFER_ID     (0x0BU)
#define ADC_GET_STREAM_LAST_POINTER_ID (0x0CU)

/* ============================ */
/*          TYPES               */
/* ============================ */

/* AUTOSAR-defined types */
typedef uint8 Adc_GroupType;
typedef uint16 Adc_ValueGroupType;
typedef uint8 Adc_PrescaleType;
typedef uint16 Adc_ConversionTimeType;
typedef uint16 Adc_SamplingTimeType;
typedef uint8 Adc_ResolutionType;
typedef uint8 Adc_StatusType;
typedef uint8 Adc_GroupPriorityType;
typedef uint16* Adc_GroupDefType;
typedef uint16 Adc_StreamNumSampleType;
typedef uint8 Adc_HwTriggerSignalType;
typedef uint32 Adc_HwTriggerTimerType;
typedef uint8 Adc_PowerStateRequestResultType;


/* Priority Implementation */
typedef enum {
    ADC_PRIORITY_HW,
    ADC_PRIORITY_HW_SW,
    ADC_PRIORITY_NONE
} Adc_PriorityImplementationType;

/* Result Alignment */
typedef enum {
    ADC_ALIGN_LEFT,
    ADC_ALIGN_RIGHT
} AdcResultAlignmentType;

/* Channel Range */
typedef enum {
    ADC_RANGE_DEFAULT,
    ADC_RANGE_EXTENDED
} AdcChannelRangeSelectType;

/* Access Mode */
typedef enum {
    ADC_ACCESS_MODE_SINGLE,
    ADC_ACCESS_MODE_STREAMING
} AdcGroupAccessModeType;

/* Conversion Mode */
typedef enum {
    ADC_CONV_MODE_ONESHOT,
    ADC_CONV_MODE_CONTINUOUS
} Adc_GroupConvModeType;

/* Replacement Mode */
typedef enum {
    ADC_REPLACE_MODE_DISCARD_OLD,
    ADC_REPLACE_MODE_OVERWRITE
} AdcGroupReplacementType;

/* Trigger Source */
typedef enum {
    ADC_TRIGG_SRC_SW,
    ADC_TRIGG_SRC_HW
} Adc_TriggerSourceType;

/* Streaming Buffer Mode */
typedef enum {
    ADC_STREAM_BUFFER_LINEAR,
    ADC_STREAM_BUFFER_CIRCULAR
} Adc_StreamBufferModeType;

/* Adc Channel Configuration */
typedef struct {
    uint16 AdcChannelId;
    uint16 AdcChannelConvTime;
    uint16 AdcChannelHighLimit;
    uint16 AdcChannelLowLimit;
    boolean AdcChannelLimitCheck;
    AdcChannelRangeSelectType AdcChannelRangeSelect;
    boolean AdcChannelRefVoltsrcHigh;
    boolean AdcChannelRefVoltsrcLow;
    uint8 AdcChannelResolution;
    uint16 AdcChannelSampTime;
} Adc_ChannelType;

/* Adc Group Configuration */
typedef struct {
    uint16 AdcGroupId;
    AdcGroupAccessModeType AdcGroupAccessMode;
    Adc_GroupConvModeType AdcGroupConversionMode;
    uint8 AdcGroupPriority;
    AdcGroupReplacementType AdcGroupReplacement;
    Adc_TriggerSourceType AdcGroupTriggSrc;
    uint8 AdcHwTrigSignal;
    uint16 AdcHwTrigTimer;
    boolean AdcNotification;
    Adc_StreamBufferModeType AdcStreamingBufferMode;
    uint16 AdcStreamingNumSamples;
    uint16 AdcGroupDefinition; /* links to channel IDs */
} AdcGroupConfigType;

/* Adc Power State Config */
typedef struct {
    uint8 AdcPowerState;
    const char* AdcPowerStateReadyCbkRef;
} Adc_PowerStateType;

/* Main Adc Config */
typedef struct {
    Adc_PriorityImplementationType AdcPriorityImplementation;
    AdcResultAlignmentType AdcResultAlignment;
    uint8 AdcHwUnit;
    const Adc_ChannelType* AdcChannels;
    uint16 NumChannels;
    const AdcGroupConfigType* AdcGroups;
    uint16 NumGroups;
    const Adc_PowerStateType* AdcPowerStates;
    uint16 NumPowerStates;
} Adc_ConfigType;

/* ============================ */
/*        API PROTOTYPES        */
/* ============================ */
void Adc_Init(const Adc_ConfigType* ConfigPtr);

#if (ADC_DEINIT_API == STD_ON)
void Adc_DeInit(void);
#endif

Std_ReturnType Adc_SetupResultBuffer(uint16 Group, uint16* BufferPtr);

#if (ADC_ENABLE_START_STOP_GROUP_API == STD_ON)
Std_ReturnType Adc_StartGroupConversion(uint16 Group);
Std_ReturnType Adc_StopGroupConversion(uint16 Group);
#endif

#if (ADC_READ_GROUP_API == STD_ON)
Std_ReturnType Adc_ReadGroup(uint16 Group, uint16* DataBufferPtr);
#endif

#if (ADC_HW_TRIGGER_API == STD_ON)
void Adc_EnableHardwareTrigger(uint16 Group);
void Adc_DisableHardwareTrigger(uint16 Group);
#endif

#if (ADC_GRP_NOTIF_CAPABILITY == STD_ON)
void Adc_EnableGroupNotification(uint16 Group);
void Adc_DisableGroupNotification(uint16 Group);
#endif

Std_ReturnType Adc_GetGroupStatus(uint16 Group);
Std_ReturnType Adc_GetStreamLastPointer(uint16 Group, uint16** PtrToSamplePtr);

#if (ADC_VERSION_INFO_API == STD_ON)
void Adc_GetVersionInfo(Std_VersionInfoType* versioninfo);
#endif

#if (ADC_LOW_POWER_STATES_SUPPORT == STD_ON)
/* Power States */
Std_ReturnType Adc_SetPowerState(uint8 PowerState);
Std_ReturnType Adc_GetCurrentPowerState(uint8* CurrentState);
Std_ReturnType Adc_GetTargetPowerState(uint8* TargetState);
Std_ReturnType Adc_PreparePowerState(uint8 PowerState, uint8 TransitionMode);
void Adc_Main_PowerTransitionManager(void);
#endif

#endif /* ADC_H_ */

'''

ADC_C_TEMPLATE = '''#include "Adc.h"
#include "Adc_Cfg.h"
#include "stm32_regs.h"

/**
 * Developer: Aruvi B & Auroshaa A from CreamCollar
 * @file Adc.c
 * @brief ADC Implementation File
 * @details Generated ADC Implementation from ARXML
 * Generated from ARXML: adc_config.arxml
 */


/* Global state */
static const Adc_ConfigType* Adc_ConfigPtr = NULL_PTR;
static boolean Adc_Initialized = FALSE;
static uint8 Adc_CurrentPowerState = 0U;

/* ============================ */
/*        API DEFINITIONS       */
/* ============================ */


/* Initialize ADC */
void Adc_Init(const Adc_ConfigType* ConfigPtr)
{
    /* Enable ADC1 clock */
    RCC_APB2ENR |= RCC_APB2ENR_ADC1EN;

    /* Enable ADC1 */
    ADC1_CR2 |= ADC_CR2_ADON;

    /* Example: Set sample time for channel 0 */
    ADC1_SMPR2 |= (0x7 << 0);  // 480 cycles for channel 0
}

/* Start conversion on a group (simulate group as channel 0) */
Std_ReturnType Adc_StartGroupConversion(Adc_GroupType Group)
{
    /* Select channel 0 */
    ADC1_SQR3 = 0;

    /* Start conversion */
    ADC1_CR2 |= ADC_CR2_SWSTART;

    return E_OK;
}

/* Read conversion result */
Std_ReturnType Adc_ReadGroup(Adc_GroupType Group, Adc_ValueGroupType* DataBufferPtr)
{
    while (!(ADC1_SR & ADC_SR_EOC)) ;  // Wait for conversion
    DataBufferPtr[0] = (uint16)ADC1_DR;
    return E_OK;
}


#if (ADC_DEINIT_API == STD_ON)
void Adc_DeInit(void)
{
    Adc_ConfigPtr = NULL_PTR;
    Adc_Initialized = FALSE;
}
#endif

/* Setup buffer for group results */
Std_ReturnType Adc_SetupResultBuffer(uint16 Group, uint16* BufferPtr)
{
    if (!Adc_Initialized) {
#if (ADC_DEV_ERROR_DETECT == STD_ON)
        Det_ReportError(ADC_MODULE_ID, ADC_INSTANCE_ID, ADC_SETUP_RESULT_BUFFER_ID, ADC_E_UNINIT);
#endif
        return E_NOT_OK;
    }
    /* TODO: assign buffer for group */
    return E_OK;
}

#if (ADC_ENABLE_START_STOP_GROUP_API == STD_ON)
/* Start group conversion */


/* Stop group conversion */
Std_ReturnType Adc_StopGroupConversion(uint16 Group)
{
    if (!Adc_Initialized) {
#if (ADC_DEV_ERROR_DETECT == STD_ON)
        Det_ReportError(ADC_MODULE_ID, ADC_INSTANCE_ID, ADC_STOP_GROUP_CONVERSION_ID, ADC_E_UNINIT);
#endif
        return E_NOT_OK;
    }
    /* TODO: stop hardware conversion */
    return E_OK;
}
#endif

#if (ADC_HW_TRIGGER_API == STD_ON)
void Adc_EnableHardwareTrigger(uint16 Group)
{
    if (!Adc_Initialized) {
#if (ADC_DEV_ERROR_DETECT == STD_ON)
        Det_ReportError(ADC_MODULE_ID, ADC_INSTANCE_ID, ADC_ENABLE_HARDWARE_TRIGGER_ID, ADC_E_UNINIT);
#endif
        return;
    }
    /* TODO: enable hardware trigger for group */
}

void Adc_DisableHardwareTrigger(uint16 Group)
{
    if (!Adc_Initialized) {
#if (ADC_DEV_ERROR_DETECT == STD_ON)
        Det_ReportError(ADC_MODULE_ID, ADC_INSTANCE_ID, ADC_DISABLE_HARDWARE_TRIGGER_ID, ADC_E_UNINIT);
#endif
        return;
    }
    /* TODO: disable hardware trigger for group */
}
#endif

#if (ADC_GRP_NOTIF_CAPABILITY == STD_ON)
/* Notifications */
void Adc_EnableGroupNotification(uint16 Group)
{
    /* TODO: enable interrupts for group */
}

void Adc_DisableGroupNotification(uint16 Group)
{
    /* TODO: disable interrupts for group */
}
#endif

Std_ReturnType Adc_GetGroupStatus(uint16 Group)
{
    if (!Adc_Initialized) {
#if (ADC_DEV_ERROR_DETECT == STD_ON)
        Det_ReportError(ADC_MODULE_ID, ADC_INSTANCE_ID, ADC_GET_GROUP_STATUS_ID, ADC_E_UNINIT);
#endif
        return E_NOT_OK;
    }
    /* TODO: get group status */
    return E_OK;
}

Std_ReturnType Adc_GetStreamLastPointer(uint16 Group, uint16** PtrToSamplePtr)
{
    if (!Adc_Initialized) {
#if (ADC_DEV_ERROR_DETECT == STD_ON)
        Det_ReportError(ADC_MODULE_ID, ADC_INSTANCE_ID, ADC_GET_STREAM_LAST_POINTER_ID, ADC_E_UNINIT);
#endif
        return E_NOT_OK;
    }
    /* TODO: get stream last pointer */
    return E_OK;
}

#if (ADC_VERSION_INFO_API == STD_ON)
/* Version Info */
void Adc_GetVersionInfo(Std_VersionInfoType* versioninfo)
{
    if (versioninfo != NULL_PTR) {
        versioninfo->vendorID = ADC_VENDOR_ID;
        versioninfo->moduleID = ADC_MODULE_ID;
        versioninfo->sw_major_version = ADC_SW_MAJOR_VERSION;
        versioninfo->sw_minor_version = ADC_SW_MINOR_VERSION;
        versioninfo->sw_patch_version = ADC_SW_PATCH_VERSION;
    }
}
#endif

#if (ADC_LOW_POWER_STATES_SUPPORT == STD_ON)
/* Power States */
Std_ReturnType Adc_SetPowerState(uint8 PowerState)
{
    Adc_CurrentPowerState = PowerState;
    return E_OK;
}

Std_ReturnType Adc_GetCurrentPowerState(uint8* CurrentState)
{
    if (CurrentState != NULL_PTR) {
        *CurrentState = Adc_CurrentPowerState;
        return E_OK;
    }
    return E_NOT_OK;
}

Std_ReturnType Adc_GetTargetPowerState(uint8* TargetState)
{
    /* Stub */
    return E_OK;
}

Std_ReturnType Adc_PreparePowerState(uint8 PowerState, uint8 TransitionMode)
{
    /* Stub */
    return E_OK;
}

void Adc_Main_PowerTransitionManager(void)
{
    /* Stub */
    return E_OK;
}
#endif

'''


STD_TYPES = '''
#ifndef STD_TYPES_H
#define STD_TYPES_H

#include <stdint.h>

/* Standard AUTOSAR types */
typedef uint8_t  uint8;
typedef uint16_t uint16;
typedef uint32_t uint32;
typedef int8_t   sint8;
typedef int16_t  sint16;
typedef int32_t  sint32;

typedef unsigned char boolean;

#ifndef TRUE
#define TRUE 1
#endif

#ifndef FALSE
#define FALSE 0
#endif

typedef uint8 Std_ReturnType;

#define E_OK 0x00u
#define E_NOT_OK 0x01u

#define STD_HIGH 0x01u
#define STD_LOW 0x00u

#define STD_ACTIVE 0x01u
#define STD_IDLE 0x00u

#define STD_ON 0x01u
#define STD_OFF 0x00u

#define NULL_PTR ((void *)0)

typedef struct
{
  uint16  vendorID;
  uint16  moduleID;
  uint8   sw_major_version;
  uint8   sw_minor_version;
  uint8   sw_patch_version;
} Std_VersionInfoType;

#endif /* STD_TYPES_H */
'''

ADC_PB_CFG = '''#include "Adc.h"
#include "Adc_Cfg.h"

/* Define Channels */
static const Adc_ChannelType AdcChannelConfig[ADC_MAX_CHANNELS] = {
    { .AdcChannelId = 0, .AdcChannelConvTime = 5, .AdcChannelHighLimit = 1023,
      .AdcChannelLowLimit = 0, .AdcChannelLimitCheck = FALSE,
      .AdcChannelRangeSelect = ADC_RANGE_DEFAULT,
      .AdcChannelRefVoltsrcHigh = TRUE, .AdcChannelRefVoltsrcLow = FALSE,
      .AdcChannelResolution = 10, .AdcChannelSampTime = 2 },

    { .AdcChannelId = 1, .AdcChannelConvTime = 5, .AdcChannelHighLimit = 1023,
      .AdcChannelLowLimit = 0, .AdcChannelLimitCheck = TRUE,
      .AdcChannelRangeSelect = ADC_RANGE_EXTENDED,
      .AdcChannelRefVoltsrcHigh = TRUE, .AdcChannelRefVoltsrcLow = TRUE,
      .AdcChannelResolution = 12, .AdcChannelSampTime = 3 },

    { .AdcChannelId = 2, .AdcChannelConvTime = 10, .AdcChannelHighLimit = 500,
      .AdcChannelLowLimit = 100, .AdcChannelLimitCheck = FALSE,
      .AdcChannelRangeSelect = ADC_RANGE_DEFAULT,
      .AdcChannelRefVoltsrcHigh = FALSE, .AdcChannelRefVoltsrcLow = FALSE,
      .AdcChannelResolution = 8, .AdcChannelSampTime = 1 },

    { .AdcChannelId = 3, .AdcChannelConvTime = 12, .AdcChannelHighLimit = 4095,
      .AdcChannelLowLimit = 0, .AdcChannelLimitCheck = TRUE,
      .AdcChannelRangeSelect = ADC_RANGE_EXTENDED,
      .AdcChannelRefVoltsrcHigh = TRUE, .AdcChannelRefVoltsrcLow = FALSE,
      .AdcChannelResolution = 12, .AdcChannelSampTime = 4 }
};

/* Define Groups */
static const AdcGroupConfigType AdcGroupConfig[ADC_MAX_GROUPS] = {
    { .AdcGroupId = 0,
      .AdcGroupAccessMode = ADC_ACCESS_MODE_SINGLE,
      .AdcGroupConversionMode = ADC_CONV_MODE_ONESHOT,
      .AdcGroupPriority = 1,
      .AdcGroupReplacement = ADC_REPLACE_MODE_OVERWRITE,
      .AdcGroupTriggSrc = ADC_TRIGG_SRC_SW,
      .AdcHwTrigSignal = 0,
      .AdcHwTrigTimer = 0,
      .AdcNotification = TRUE,
      .AdcStreamingBufferMode = ADC_STREAM_BUFFER_LINEAR,
      .AdcStreamingNumSamples = 1,
      .AdcGroupDefinition = 0 },

    { .AdcGroupId = 1,
      .AdcGroupAccessMode = ADC_ACCESS_MODE_STREAMING,
      .AdcGroupConversionMode = ADC_CONV_MODE_CONTINUOUS,
      .AdcGroupPriority = 2,
      .AdcGroupReplacement = ADC_REPLACE_MODE_DISCARD_OLD,
      .AdcGroupTriggSrc = ADC_TRIGG_SRC_HW,
      .AdcHwTrigSignal = 1,
      .AdcHwTrigTimer = 100,
      .AdcNotification = FALSE,
      .AdcStreamingBufferMode = ADC_STREAM_BUFFER_CIRCULAR,
      .AdcStreamingNumSamples = 8,
      .AdcGroupDefinition = 1 }
};

/* Define Power States */
static const Adc_PowerStateType AdcPowerStates[ADC_MAX_POWER_STATES] = {
    { .AdcPowerState = 0, .AdcPowerStateReadyCbkRef = "PowerState0Ready" },
    { .AdcPowerState = 1, .AdcPowerStateReadyCbkRef = "PowerState1Ready" }
};

/* Exported Config Structure */
const Adc_ConfigType Adc_Config = {
    .AdcPriorityImplementation = ADC_PRIORITY_HW_SW,
    .AdcResultAlignment = ADC_ALIGN_RIGHT,
    .AdcHwUnit = 1,
    .AdcChannels = AdcChannelConfig,
    .NumChannels = ADC_MAX_CHANNELS,
    .AdcGroups = AdcGroupConfig,
    .NumGroups = ADC_MAX_GROUPS,
    .AdcPowerStates = AdcPowerStates,
    .NumPowerStates = ADC_MAX_POWER_STATES
};
'''
