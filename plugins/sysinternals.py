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

        sysinternal = ["Software\\Sysinternals"]
        
        try:
            for k in sysinternal:
                for sysKeys in Registry.Registry(self.hive).open(k).subkeys():
                    for v in sysKeys.values():
                        if "EulaAccepted" in v.name():
                            if v.value() == 1:
                                last_write = sysKeys.timestamp()
                                key_name = sysKeys.name()
                                
                                if self.format is not None:
                                    template = Environment().from_string(format[0])
                                    sys.stdout.write(template.render(last_write=last_write, \
                                                                     key_name=key_name) + "\n")
                                elif self.format_file is not None:
                                    with open(self.format_file[0], "rb") as f:
                                        template = env.from_string(f.read())            
                                        sys.stdout.write(template.render(last_write=last_write, \
                                                                     key_name=key_name) + "\n")                                
                                
        except Registry.RegistryKeyNotFoundException as e:
            pass