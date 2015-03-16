import sys
from modules.HelperFunctions import HelperFunction
from Registry import Registry
from yapsy.IPlugin import IPlugin
from jinja2 import Template, Environment, PackageLoader
#import logging
#logging.basicConfig(level=logging.DEBUG)

class ActiveSetup(IPlugin):

    def __init__(self, hive=None, format=None, format_file=None, search=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file

    def ProcessPlugin(self, hive=None, format=None, format_file=None, search=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file
        
        env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))
        dict = {}
        
        for hive in self.hive:
            dict.update(self.processKeys(hive))
            
        for key, val in dict.iteritems():
            last_write = val[0]
            key_name = key
            stub_path = val[1]
        

            if self.format is not None:
                template = Environment().from_string(format[0])
                sys.stdout.write(template.render(last_write=last_write, \
                                                 key_name=key_name, \
                                                 stub_path=stub_path) + "\n")
            
            elif self.format_file is not None:
                with open(self.format_file[0], "rb") as f:
                    template = env.from_string(f.read())            
                    sys.stdout.write(template.render(last_write=last_write, \
                                                     key_name=key_name, \
                                                     stub_path=stub_path) + "\n")
        
    def processKeys(self, hive):
        active_setup_list = []
        active_setup_list_entries = []
        active_setup = ["Microsoft\\Active Setup\\Installed Components",
                        "Wow6432Node\\Microsoft\\Active Setup\\Installed Components"]

        try:
            for m in active_setup:
                for v in Registry.Registry(hive).open(m).subkeys():
                    active_setup_list.append(v.name())
        
            for keys in active_setup_list:
                k = Registry.Registry(hive).open(m + "\\%s" % (keys))
                for activesets in k.values():
                    if activesets.name() == "StubPath":
                        if activesets.value() is not '':
                            last_write = k.timestamp()
                            key_name = k.name().encode('ascii', 'ignore')
                            stub_path = activesets.value().encode('ascii', 'ignore')

                            active_setup_list_entries.append([last_write, key_name, stub_path])
                            
        except Registry.RegistryKeyNotFoundException as e:
            pass
            
        dict = {}
        for entry in active_setup_list_entries:
            dict[entry[1]] = entry[0], entry[2]
    
        return(dict)