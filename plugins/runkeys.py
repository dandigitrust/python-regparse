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

        self.processKeys(self.hive, self.format, self.format_file, run_entries)
    
    def processKeys(self, hive=None, format=None, format_file=None, run_entries=None):
        self.format = format
        self.format_file = format_file
        self.run_entries = run_entries
    
        env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))
    
        key_hive = self.hive
        runkey_list = []
    
        for k in run_entries:
            try:
                key = Registry.Registry(hive).open(k)
    
                for v in key.values():
                    last_write = key.timestamp()
                    if k:
                        key_name = k
                    else:
                        key_name = "None"
                    if v.name():
                        name = v.name()
                    else:
                        name = v.name()
                    if v.value():
                        value = v.value()
                    else:
                        value = v.value()
    
                    runkey_list.append([last_write, key_name, name, value])
    
            except Registry.RegistryKeyNotFoundException as e:
                pass
    
        if self.format is not None:
            for entry in runkey_list:
                last_write = entry[0]
                key_name = entry[1]
                name = entry[2]
                value = entry[3]
                template = Environment().from_string(format[0])
                sys.stdout.write(template.render(k=k, \
                                                 key_hive=key_hive, \
                                                 last_write=last_write, \
                                                 key_name=key_name, \
                                                 name=name, \
                                                 value=value) + "\n")
        elif self.format_file is not None:
            with open(self.format_file[0], "rb") as f:
                template = env.from_string(f.read())            
                sys.stdout.write(template.render(k=k, \
                                                 key_hive=key_hive, \
                                                 runkey_list=runkey_list) + "\n")