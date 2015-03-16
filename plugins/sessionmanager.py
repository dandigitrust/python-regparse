import sys
from modules.HelperFunctions import HelperFunction
from Registry import Registry
from yapsy.IPlugin import IPlugin
from jinja2 import Template, Environment, PackageLoader
#import logging
#logging.basicConfig(level=logging.DEBUG)

class Services(IPlugin):

    def __init__(self, hive=None, format=None, format_file=None, search=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file

    def ProcessPlugin(self, hive=None, format=None, format_file=None, search=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file
        env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))

        #dict = {}
        for hive in self.hive:
            #dict.update(self.processSessionManager(hive))
            self.processSessionManager(hive)

    def processSessionManager(self, hive=None):            
        try:
            current = HelperFunction(hive).CurrentControlSet()
            session_manager = Registry.Registry(hive).open('%s\\Control\\Session Manager' % (current))
            last_write = session_manager.timestamp()
            for value in session_manager.value("PendingFileRenameOperations").value():
                if value != '':
                    print str(value).encode('ascii', 'ignore')
        except Registry.RegistryKeyNotFoundException as e:
            pass
        
        try:
            for value in session_manager.value("BootExecute").value():
                if value != '':
                    boot_execute = str(value).encode('ascii', 'ignore')
                    print boot_execute
        except Registry.RegistryKeyNotFoundException as e:
            pass
                    
        