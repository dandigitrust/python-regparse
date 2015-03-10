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
        
        
    def processMRU(self, hive=None):
        key = "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ComDlg32\\OpenSaveMRU"
        opensavemru_list_entries = []
        mru_list = []
        try:
            opensavemru = Registry.Registry(self.hive).open(key)
        
            for sK in opensavemru.subkeys():
                mru_named_order = sK.value("MRUList").value()
                mru = ",".join(["{:02x}".format(ord(c)) for c in sK.value("MRUList").value()])
                opensavemru_list_entries.append([sK.timestamp(), sK.name(), mru, mru_named_order])
        
        except Registry.RegistryKeyNotFoundException as e:
            pass
        
        return opensavemru_list_entries

                
    
    def ProcessPlugin(self, hive=None, format=None, format_file=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file
        
        env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))
        key = 'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\ComDlg32\\OpenSaveMRU\\%s'
        
        for entry in self.processMRU(self.hive):
            split_mru = [thing.decode("hex") for thing in entry[2].split(',')]
            for split_mru_value in split_mru:
                
                for vals in Registry.Registry(self.hive).open(key % (entry[1])).values():
                    if split_mru_value == vals.name():
                        last_write = entry[1]
                        mru_order = entry[3]
                        key_name = vals.name()
                        value = vals.value()
                    else:
                        continue
                    
                    if self.format is not None:
                        template = Environment().from_string(format[0])
                        sys.stdout.write(template.render(last_write=last_write, \
                                                         mru_order=mru_order, \
                                                         key_name=key_name, \
                                                         value=value) + "\n")
                    elif self.format_file is not None:
                        with open(self.format_file[0], "rb") as f:
                            template = env.from_string(f.read())            
                            sys.stdout.write(template.render(last_write=last_write, \
                                                             mru_order=mru_order, \
                                                             key_name=key_name, \
                                                             value=value) + "\n")                     
