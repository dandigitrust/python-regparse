import sys
from modules.HelperFunctions import HelperFunction
from Registry import Registry
from yapsy.IPlugin import IPlugin
from jinja2 import Template, Environment, PackageLoader
#import logging
#logging.basicConfig(level=logging.DEBUG)

class RunMRU(IPlugin):

    def __init__(self, hive=None, format=None, format_file=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file

    def ProcessPlugin(self, hive=None, format=None, format_file=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file
        env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))
        
        try: 
            runmru_entries = []
            runmru = Registry.Registry(self.hive).open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU")
            runmru_list = runmru.value("MRUList").value()
            last_write = runmru.timestamp()        
            s = ",".join(["{:02x}".format(ord(c)) for c in runmru_list])
            
            for entry in s.split(','):
                for vals in runmru.values():
                    if vals.name() == str(entry.decode("hex")):
                        key_name = vals.name()
                        value = vals.value()
                    else:
                        continue
                    
                    if self.format is not None:
                        template = Environment().from_string(format[0])
                        sys.stdout.write(template.render(last_write=last_write, \
                                                         runmru_list=runmru_list, \
                                                         key_name=key_name, \
                                                         value=value) + "\n")
                    elif self.format_file is not None:
                        with open(self.format_file[0], "rb") as f:
                            template = env.from_string(f.read())            
                            sys.stdout.write(template.render(last_write=last_write, \
                                                         runmru_list=runmru_list, \
                                                         key_name=key_name, \
                                                         value=value) + "\n")                       
                
        except (Registry.RegistryKeyNotFoundException, Registry.RegistryParse.RegistryStructureDoesNotExist) as e:
            print "No RunMRU found."
            exit(0)