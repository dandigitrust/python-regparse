import sys
from Registry import Registry
from yapsy.IPlugin import IPlugin
from jinja2 import Template, Environment, PackageLoader

class Mounts(IPlugin):

    def __init__(self, hive=None, format=None, format_file=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file          
        
    def ProcessPlugin(self, hive=None, format=None, format_file=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file
        
        mounteddevices_list = []
        
        try:
            mountpoints = Registry.Registry(self.hive).open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\MountPoints2")
            for mps in mountpoints.subkeys():
                last_write = mps.timestamp()
                name = mps.name()
                value = "None"
            
                mounteddevices_list.append([last_write, name, value])

        except Registry.RegistryKeyNotFoundException as e:
            pass
        
        try:
            networkmru = Registry.Registry(self.hive).open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Map Network Drive MRU")
            for mrus in networkmru.values():
                last_write = networkmru.timestamp()
                name = mrus.name()
                value = mrus.value()
        
                mounteddevices_list.append([last_write, name, value])            
        except Registry.RegistryKeyNotFoundException as e:
            pass
        
        try:
            mounteddevices = Registry.Registry(self.hive).open("MountedDevices")
            for mount in mounteddevices.values():
                last_write = mounteddevices.timestamp()
                name = mount.name()
                value = "None"
            
                mounteddevices_list.append([last_write, name, value])
        except Registry.RegistryKeyNotFoundException as e:
            pass

        self.processMounted(mounteddevices_list, self.format, self.format_file)
        
        
    def processMounted(self, mounteddevices_list=None, format=None, format_file=None):
        self.format = format
        self.format_file = format_file
        self.mounteddevices_list = mounteddevices_list
        env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))
        
        if self.format_file is not None:
            for entry in self.mounteddevices_list:
                last_write = entry[0]
                name = entry[1]
                value = entry[2]                
                with open(self.format_file[0], "rb") as f:
                    template = env.from_string(f.read())
                    sys.stdout.write(template.render(last_write=last_write, name=name, value=value) + "\n")

        elif self.format is not None:
            for entry in self.mounteddevices_list:
                last_write = entry[0]
                name = entry[1]
                value = entry[2]               
                template = Environment().from_string(format[0])
                sys.stdout.write(template.render(last_write=last_write, name=name, value=value) + "\n")          