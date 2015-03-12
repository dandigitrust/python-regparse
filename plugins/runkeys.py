import sys
from modules.HelperFunctions import HelperFunction
from Registry import Registry
from yapsy.IPlugin import IPlugin
from jinja2 import Template, Environment, PackageLoader
#import logging
#logging.basicConfig(level=logging.DEBUG)

class RunKeys(IPlugin):

    def __init__(self, hive=None, format=None, format_file=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file
         
    def ProcessPlugin(self, hive=None, format=None, format_file=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file
        env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))
        
        dict = {}
        
        for hive in self.hive:
            dict.update(self.processKeys(hive))
            
        for key, val in dict.iteritems():
            last_write = val[0]
            sub_key = key
            key_name = val[1]
            value = val[2]
            
            
            if self.format is not None:              
                template = Environment().from_string(format[0])
                sys.stdout.write(template.render(last_write=last_write, \
                                                     key_name=key_name, \
                                                     sub_key=sub_key, \
                                                     value=value) + "\n")
            elif self.format_file is not None:
                with open(self.format_file[0], "rb") as f:
                    template = env.from_string(f.read())
                    sys.stdout.write(template.render(last_write=last_write, \
                                                     key_name=key_name, \
                                                     sub_key=sub_key, \
                                                     value=value) + "\n")        
    
    def processKeys(self, hive=None):
        self.hive = hive
        run_key_list = []
        run_entries =   ["Microsoft\\Windows\\CurrentVersion\\Run",
                         "Microsoft\\Windows\\CurrentVersion\\RunOnce",
                         "Microsoft\\Windows\\CurrentVersion\\RunOnceEx",
                         "Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run",
                         "Microsoft\\Windows\\CurrentVersion\\RunServicesOnce"
                         "Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Run",
                         "Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
                         "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                         "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
                         "Software\\Microsoft\\Windows\\CurrentVersion\\RunServices",
                         "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run"]
        
        for k in run_entries:
            try:
                for v in  Registry.Registry(self.hive).open(k).values():
                    last_write = Registry.Registry(self.hive).open(k).timestamp()
                    if k:
                        key_name = k
                    else:
                        key_name = "None"
                    if v.name():
                        name = v.name()
                    else:
                        name = "None"
                    if v.value():
                        value = v.value()
                    else:
                        value = "None"
                    run_key_list.append([last_write, key_name, name, value])
                    
            except Registry.RegistryKeyNotFoundException:
                continue
        
        dict = {}
        for entry in run_key_list:
            dict[entry[2]] = entry[0], entry[1], entry[3]            

        return(dict)