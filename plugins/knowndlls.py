import sys
from modules.HelperFunctions import HelperFunction
from Registry import Registry
from yapsy.IPlugin import IPlugin
from jinja2 import Template, Environment, PackageLoader

class KnownDLLs(IPlugin):

    def __init__(self, hive=None, format=None):
        self.hive = hive
        self.format = format
        
    def ProcessPlugin(self, hive=None, format=None, format_file=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file
        env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))
        
        try:
            current = HelperFunction(self.hive).CurrentControlSet()
            knowndlls = Registry.Registry(self.hive).open('%s\\Control\\Session Manager\\KnownDLLs' % (current))
            last_write = knowndlls.timestamp()
            try:
                for v in knowndlls.values():
                    name = v.name()
                    value = v.value()
                    
                    if self.format_file is not None:
                        with open(self.format_file[0], "rb") as f:
                            template = env.from_string(f.read())
                            sys.stdout.write(template.render(last_write=last_write, name=name, value=value) + "\n")
                
                    elif self.format is not None:              
                        template = Environment().from_string(format[0])
                        sys.stdout.write(template.render(last_write=last_write, name=name, value=value) + "\n")
                    
            except Registry.RegistryKeyNotFoundException as e:
                pass
            
        except Registry.RegistryKeyNotFoundException as e:
            pass