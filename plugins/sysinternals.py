import sys
from modules.HelperFunctions import HelperFunction
from Registry import Registry
from yapsy.IPlugin import IPlugin
from jinja2 import Template, Environment, PackageLoader
#import logging
#logging.basicConfig(level=logging.DEBUG)

class Sysinternals(IPlugin):

    def __init__(self, hive=None, format=None, format_file=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file

    def ProcessPlugin(self, hive=None, format=None, format_file=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file
        env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))
        
        for hive in self.hive:
            for entry in self.processSysinternals(hive):
                last_write = entry[0]
                key_name = entry[1]
                
                if self.format is not None:
                    template = Environment().from_string(format[0])
                    sys.stdout.write(template.render(last_write=last_write, \
                                                     key_name=key_name) + "\n")
                elif self.format_file is not None:
                    with open(self.format_file[0], "rb") as f:
                        template = env.from_string(f.read())            
                        sys.stdout.write(template.render(last_write=last_write, \
                                                         key_name=key_name) + "\n")
                
    def processSysinternals(self, hive=None):
        
        sysinternals_list = []
        
        try:
            for sks in Registry.Registry(hive).open("Software\\Sysinternals").subkeys():
                for v in sks.values():
                    if "EulaAccepted" in v.name():
                        if v.value() == 1:
                            last_write = sks.timestamp()
                            key_name = sks.name()
                            
                            sysinternals_list.append([last_write, key_name])
                                 
        except Registry.RegistryKeyNotFoundException as e:
            pass
        
        return(sysinternals_list)