import logging
import re
import json
import importlib.resources
from .. import templates
from jinja2 import Environment, PackageLoader, select_autoescape
from ..model.uphy import *

_logger = logging.getLogger(__name__)


def c_type(value):
    map = {
        DataType.UINT32: 'uint32_t',
        DataType.UINT16: 'uint16_t',
        DataType.UINT8: 'uint8_t',
        DataType.INT32: 'int32_t',
        DataType.INT16: 'int16_t',
        DataType.INT8: 'int8_t',
        DataType.REAL32: 'float',
    }
    return map[value.datatype]


def c_name(value):
    name = value.name
    if re.search("^[0-9].*", name):           # Escape leading numeral
        name = f"_{name}"

    name = re.sub("[^0-9A-Za-z_]", "_", name) # Replace special chars
    name = re.sub("[_+]", "_", name)          # Contract repeating underscore
    name = re.sub("_$", "", name)             # Strip trailing underscore
    return name


def c_name_upper(value):
    """Filter for uppercase C names. For example defines."""
    return c_name(value).upper()


def c_hex(value):
    return value.replace('#', '0')

def c_array(signal):
    if not signal.is_array:
        return ""
    else:
        return f"[{signal.array_length}]"

def c_flags(signal):
    if not signal.is_array:
        return "0"
    else:
        return "UP_SIG_FLAG_IS_ARRAY"

def c_bool(value):
    if value:
        return "true"
    else:
        return "false"

def enip_major_rev(rev_str):
    return rev_str.split('.')[0]

def enip_minor_rev(rev_str):
    return rev_str.split('.')[1]

class CCodeGenerator:
    def __init__(self, model):
        self.model = model
        self.device = None

        self.env = Environment(
            loader=PackageLoader("upgen"),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.env.filters['c_type'] = c_type
        self.env.filters['c_name'] = c_name
        self.env.filters['c_hex'] = c_hex
        self.env.filters['c_name_upper'] = c_name_upper
        self.env.filters['c_array'] = c_array
        self.env.filters['c_flags'] = c_flags
        self.env.filters['c_bool'] = c_bool
        self.env.filters['enip_major_rev'] = enip_major_rev
        self.env.filters['enip_minor_rev'] = enip_minor_rev

    def select_device(self, device_name):
        if device_name == None:
            self.device = self.model.devices[0]
        else:
            self.device = self.model.get_device(device_name)

        if self.device == None:
            raise Exception(f'{device_name} not found in model')

    def export_file(self):
        _logger.info('Generate model.h')
        header = self.generate_header_file()
        _logger.info('Generate model.c')
        source = self.generate_source_file()

        with open('model.h', 'w') as file:
            file.write(header)

        with open('model.c', 'w') as file:
            file.write(source)

    def generate_header_file(self):
        template = self.env.get_template("model_template.h")
        code = template.render(model=self.model, device=self.device)
        _logger.debug(code)
        return code

    def generate_source_file(self):
        template = self.env.get_template("model_template.c")
        code = template.render(model=self.model, device=self.device)
        _logger.debug(code)
        return code
