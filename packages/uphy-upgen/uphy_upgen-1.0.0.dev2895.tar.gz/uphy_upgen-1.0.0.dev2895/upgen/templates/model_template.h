/*********************************************************************
 *        _       _         _
 *  _ __ | |_  _ | |  __ _ | |__   ___
 * | '__|| __|(_)| | / _` || '_ \ / __|
 * | |   | |_  _ | || (_| || |_) |\__ \
 * |_|    \__|(_)|_| \__,_||_.__/ |___/
 *
 * http://www.rt-labs.com
 * Copyright 2022 rt-labs AB, Sweden.
 * See LICENSE file in the project root for full license information.
 ********************************************************************/

#ifndef MODEL_H
#define MODEL_H

#ifdef __cplusplus
extern "C" {
#endif

#include "up_types.h"

{% if model.profinet %}
#define UP_DEVICE_PROFINET_SUPPORTED 1
{% endif %}
{% if model.ethercat %}
#define UP_DEVICE_ETHERCAT_SUPPORTED 1
{% endif %}
{% if model.ethernetip %}
#define UP_DEVICE_ETHERNETIP_SUPPORTED 1
{% endif %}
{% if device.modbus %}
#define UP_DEVICE_MODBUS_SUPPORTED 1
{% endif %}

{% if device.has_alarms(model) %}
/* Alarm error codes */
{% for module in device.get_used_modules(model) %}
   {% for a in module.alarms %}
#define UP_ERROR_CODE_{{module | c_name_upper}}_{{a | c_name_upper}} {{a.error_code}}
   {% endfor %}
{% endfor %}

{% endif %}
typedef struct up_data
{
{% for slot in device.slots %}
{% set module = model.get_module(slot.module) %}
   struct
   {
   {% for signal in module.inputs %}
      struct
      {
         {{signal | c_type}} value{{signal | c_array}};
         up_signal_status_t status;
      } {{signal | c_name}};
   {% endfor %}
   {% for signal in module.outputs %}
      struct
      {
         {{signal | c_type}} value{{signal | c_array}};
         up_signal_status_t status;
      } {{signal | c_name}};
   {% endfor %}
   {% for signal in module.parameters %}
      {{signal | c_type}} {{signal | c_name}};
   {% endfor %}
   } {{slot | c_name}};
{% endfor %}
} up_data_t;

extern up_data_t up_data;
extern up_signal_info_t up_vars[];
extern up_device_t up_device;
{% if model.profinet %}
extern up_profinet_config_t up_profinet_config;
{% endif %}
{% if model.ethercat %}
extern up_ecat_device_t up_ethercat_config;
{% endif %}
{% if model.ethernetip %}
extern up_ethernetip_config_t up_ethernetip_config;
{% endif %}
{% if device.modbus %}
extern up_modbus_config_t up_modbus_config;
{% endif %}
extern up_mockadapter_config_t up_mock_config;

#ifdef __cplusplus
}
#endif

#endif /* MODEL_H */
