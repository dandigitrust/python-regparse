import sys
from modules.HelperFunctions import HelperFunction
from Registry import Registry
from yapsy.IPlugin import IPlugin
from jinja2 import Template, Environment, PackageLoader

class KnownDLLs(IPlugin):

    def __init__(self, hive=None, format=None, format_file=None, search=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file

    def ProcessPlugin(self, hive=None, format=None, format_file=None, search=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file
        env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))
        
        for hive in self.hive:
            for entry in self.processKeys(hive):
                last_write = entry[0]
                name = entry[1]
                value = entry[2]
                
                if self.format_file is not None:
                    with open(self.format_file[0], "rb") as f:
                        template = env.from_string(f.read())
                        sys.stdout.write(template.render(last_write=last_write, name=name, value=value) + "\n")

                elif self.format is not None:              
                    template = Environment().from_string(format[0])
                    sys.stdout.write(template.render(last_write=last_write, name=name, value=value) + "\n")
            
    def processKeys(self, hive):
        
        knowndlls_list = []
        
        try:
            current = HelperFunction(hive).CurrentControlSet()
            last_write = Registry.Registry(hive).open('%s\\Control\\Session Manager\\KnownDLLs' % (current)).timestamp()
            
            for v in Registry.Registry(hive).open('%s\\Control\\Session Manager\\KnownDLLs' % (current)).values():
                name = v.name()
                value = v.value()
                knowndlls_list.append([last_write, name, value])
            
        except Registry.RegistryKeyNotFoundException as e:
            pass
        
        return(knowndlls_list)