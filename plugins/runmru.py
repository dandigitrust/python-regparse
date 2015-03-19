import sys
from modules.HelperFunctions import HelperFunction
from Registry import Registry
from yapsy.IPlugin import IPlugin
from jinja2 import Template, Environment, PackageLoader
#import logging
#logging.basicConfig(level=logging.DEBUG)

class RunMRU(IPlugin):

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
            try:
                runmru = Registry.Registry(hive).open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU")
            except Registry.RegistryKeyNotFoundException as e:
                pass
            key = runmru.name()
            last_write = runmru.timestamp()
            mruorder = runmru.value("MRUList").value()
            for entry in list(mruorder):
                for vals in runmru.values():
                    if entry == vals.name():
                        value = vals.name()
                        data = vals.value()
                    else:
                        continue
                    
                    if self.format_file is not None:                
                        with open(self.format_file[0], "rb") as f:
                            template = env.from_string(f.read())
                            sys.stdout.write(template.render(last_write=last_write, \
                                                             key=key, \
                                                             mruorder=mruorder, \
                                                             value=value, \
                                                             data=data) + "\n")
                    elif self.format is not None:           
                        template = Environment().from_string(format[0])
                        sys.stdout.write(template.render(last_write=last_write, \
                                                             key=key, \
                                                             mruorder=mruorder, \
                                                             value=value, \
                                                             data=data) + "\n")            