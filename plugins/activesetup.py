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
        
        env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))

        active_setup = ["Microsoft\\Active Setup\\Installed Components",
                        "Wow6432Node\\Microsoft\\Active Setup\\Installed Components"]
    
        active_setup_list = []
        
        try:
            for m in active_setup:
                for v in Registry.Registry(self.hive).open(m).subkeys():
                    active_setup_list.append(v.name())
        
            for keys in active_setup_list:
                k = Registry.Registry(self.hive).open(m + "\\%s" % (keys))
                for activesets in k.values():
                    if activesets.name() == "StubPath":
                        if activesets.value() is not '':
                            last_write = k.timestamp()
                            key_name = k.name().encode('ascii', 'ignore')
                            stub_path = activesets.value().encode('ascii', 'ignore')                            

                            if self.format is not None:
                                    template = Environment().from_string(format[0])
                                    sys.stdout.write(template.render(last_write=last_write, key_name=key_name, stub_path=stub_path) + "\n")
                            
                            elif self.format_file is not None:
                                with open(self.format_file[0], "rb") as f:
                                    template = env.from_string(f.read())            
                                    sys.stdout.write(template.render(last_write=last_write, key_name=key_name, stub_path=stub_path) + "\n")

        except Registry.RegistryKeyNotFoundException as e:
            pass