import sys
from modules.HelperFunctions import HelperFunction
from Registry import Registry
from yapsy.IPlugin import IPlugin
from jinja2 import Template, Environment, PackageLoader
import struct
#import logging
#logging.basicConfig(level=logging.DEBUG)

class RecentDocs(IPlugin):

    def __init__(self, hive=None, format=None, format_file=None, search=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file

    def ProcessPlugin(self, hive=None, format=None, format_file=None, search=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file

        env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))
        
        recentdocs_root = []
        
        for hive in self.hive:
            
            recentdocs = Registry.Registry(hive).open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RecentDocs")

            key = recentdocs.name()
            last_write = recentdocs.timestamp()
            mruorder = recentdocs.value("MRUListEx").value()
            for entry in struct.unpack("%dI" % (len(mruorder)/4), mruorder):
                for docs in recentdocs.values():
                    if docs.name() == str(entry):
                        recentdocs_root.append((recentdocs.timestamp(), key, "RootMRU", entry, docs.value().split('\x00\x00')[0]))
                    else:
                        continue
                        
            for subkeys in Registry.Registry(hive).open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RecentDocs").subkeys():
                mruorder = subkeys.value("MRUListEx").value()
                
                for values in subkeys.values():
                    for entry in  struct.unpack("%dI" % (len(mruorder)/4), mruorder):
                        if str(values.name()) == str(entry):
                            recentdocs_root.append((subkeys.timestamp(), key, subkeys.name(), values.name(), values.value().split('\x00\x00')[0]))
                        else:
                            continue
                        
        for entry in recentdocs_root:
            last_write = entry[0]
            key_name = entry[1]
            key = entry[2]
            value = entry[3]
            data = entry[4]
            
            if self.format_file is not None:
                with open(self.format_file[0], "rb") as f:
                    template = env.from_string(f.read())
                    sys.stdout.write(template.render(last_write=last_write, \
                                                     key_name=key_name, \
                                                     key=key, \
                                                     value=value, \
                                                     data=data) + "\n")
        
            elif self.format is not None:              
                template = Environment().from_string(format[0])
                sys.stdout.write(template.render(last_write=last_write, \
                                                 key_name=key_name, \
                                                 key=key, \
                                                 value=value, \
                                                 data=data) + "\n")