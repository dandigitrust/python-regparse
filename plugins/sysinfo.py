import sys
from modules.HelperFunctions import HelperFunction
from Registry import Registry
from yapsy.IPlugin import IPlugin
from jinja2 import Template, Environment, PackageLoader
import time
#import logging
#logging.basicConfig(level=logging.DEBUG)

class SystemInformation(IPlugin):

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
            master = Registry.Registry(self.hive).open("Microsoft\\Windows NT\\CurrentVersion")

            last_write = master.timestamp()
            
            try:
                product_name = master.value("ProductName").value()
            except Registry.RegistryValueNotFoundException as e:
                product_name = "None Listed"
            
            try:
                csd_version = master.value("CSDVersion").value()
            except Registry.RegistryValueNotFoundException as e:
                csd_version = "None Listed"
            try:
                current_version = master.value("CurrentVersion").value()    
            except Registry.RegistryValueNotFoundException as e:
                current_version = "None Listed"
            try:
                current_build_number = master.value("CurrentBuildNumber").value()
            except Registry.RegistryValueNotFoundException as e:
                current_build_number = "None Listed"    
            try:
                registered_owner = master.value("RegisteredOwner").value()
            except Registry.RegistryValueNotFoundException as e:
                registered_owner = "None Listed"
            #2013-10-25T02:53:08Z
            try:
                installed_date = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(master.value("InstallDate").value()))
            except Registry.RegistryValueNotFoundException as e:
                installed_date = "None Listed"
                
            os_info = product_name +" "+ current_version +" "+ current_build_number +" "+ csd_version 
                
                
            if self.format_file is not None:
                with open(self.format_file[0], "rb") as f:
                    template = env.from_string(f.read())
                    sys.stdout.write(template.render(last_write=last_write, \
                                                     os_info=os_info, \
                                                     installed_date=installed_date, \
                                                     registered_owner=registered_owner) + "\n")
        
            elif self.format is not None:              
                template = Environment().from_string(format[0])
                sys.stdout.write(template.render(last_write=last_write, \
                                                     os_info=os_info, \
                                                     installed_date=installed_date, \
                                                     registered_owner=registered_owner) + "\n")                
                
        except Registry.RegistryValueNotFoundException as e:
            exit(0)
        

        
        