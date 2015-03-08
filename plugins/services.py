import sys
from modules.HelperFunctions import HelperFunction
from Registry import Registry
from yapsy.IPlugin import IPlugin
from jinja2 import Template, Environment, PackageLoader
#import logging
#logging.basicConfig(level=logging.DEBUG)

class Services(IPlugin):
    
    def __init__(self, hive=None, format=None, format_file=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file
    
    def ProcessPlugin(self, hive=None, format=None, format_file=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file
        
        if "system" in self.hive.lower():
            current = HelperFunction(self.hive).CurrentControlSet()
            services = Registry.Registry(self.hive).open('%s\\Services' % (current))
            
            service_list = []
            objects_list = []     
            
            for service in services.subkeys():
                service_list.append(service.name().lower())
    
            for service_name in service_list:
                k = Registry.Registry(self.hive).open('ControlSet001\\Services\\' + service_name)
                key_name = k.name()
                last_write = str(k.timestamp())
                try:
                    type_name = k.value("Type").value()
                except:
                    type_name = "None"
                try:
                    image_path = k.value("ImagePath").value().lower()
                except:
                    image_path = "None"
                try:
                    display_name = k.value("DisplayName").value()
                except:
                    display_name = "None"
                try:
                    start_type = k.value("Start").value()
                except:
                    start_type = "None"
                try:
                    service_dll = k.subkey("Parameters").value("ServiceDll").value()
                except:
                    service_dll = "None"
                
                env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))
                
                
                if self.format_file is not None:
                    with open(self.format_file[0], "rb") as f:
                        template = env.from_string(f.read())
                        sys.stdout.write(template.render(last_write=last_write, key_name=key_name, \
                                                         image_path=image_path, type_name=type_name, \
                                                         display_name=display_name, start_type=start_type, \
                                                         service_dll=service_dll) + "\n")
                    
                elif self.format is not None:
                    template = Environment().from_string(format[0])
                    sys.stdout.write(template.render(last_write=last_write, key_name=key_name, \
                                                     image_path=image_path, type_name=type_name, \
                                                     display_name=display_name, start_type=start_type, \
                                                     service_dll=service_dll) + "\n")                    