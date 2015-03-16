import sys
from Registry import Registry
from yapsy.IPlugin import IPlugin
from jinja2 import Template, Environment, PackageLoader

class Mounts(IPlugin):

    def __init__(self, hive=None, format=None, format_file=None, search=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file

    def ProcessPlugin(self, hive=None, format=None, format_file=None, search=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file
        dict = {}
        env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))
        
        for hive in self.hive:
            dict.update(self.processKeys(hive))
            
            
        for key, val in dict.iteritems():
            last_write = val[0]
            name = key
            value = val[1]
            
            if self.format_file is not None:                
                with open(self.format_file[0], "rb") as f:
                    template = env.from_string(f.read())
                    sys.stdout.write(template.render(last_write=last_write, \
                                                     name=name, \
                                                     value=value) + "\n")
            elif self.format is not None:           
                template = Environment().from_string(format[0])
                sys.stdout.write(template.render(last_write=last_write, \
                                                 name=name, \
                                                 value=value) + "\n")
    
    def processKeys(self, hive):
        
        mounteddevices_list = []
        
        try:
            mountpoints = Registry.Registry(hive).open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\MountPoints2")
            for mps in mountpoints.subkeys():
                last_write = mps.timestamp()
                name = mps.name()
                value = "None"
            
                mounteddevices_list.append([last_write, name, value])

        except Registry.RegistryKeyNotFoundException as e:
            pass
        
        try:
            networkmru = Registry.Registry(hive).open("Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Map Network Drive MRU")
            for mrus in networkmru.values():
                last_write = networkmru.timestamp()
                name = mrus.name()
                value = mrus.value()
        
                mounteddevices_list.append([last_write, name, value])            
        except Registry.RegistryKeyNotFoundException as e:
            pass
        
        try:
            mounteddevices = Registry.Registry(hive).open("MountedDevices")
            for mount in mounteddevices.values():
                last_write = mounteddevices.timestamp()
                name = mount.name()
                value = "None"
            
                mounteddevices_list.append([last_write, name, value])
        except Registry.RegistryKeyNotFoundException as e:
            pass

        
        dict = {}
        for entry in mounteddevices_list:
            dict[entry[1]] = entry[0], entry[2]
    
        return(dict)        
                  