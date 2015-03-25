import sys
from Registry import Registry
from jinja2 import Template, Environment, PackageLoader

class PluginClass(object):

    def __init__(self, hives=None, search=None, format=None, format_file=None):
        self.hives = hives
        self.search = search
        self.format = format
        self.format_file = format_file

    def ProcessPlugin(self):

        env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))

        bho_keys = ["Microsoft\\Windows\\CurrentVersion\\Explorer\\Browser Helper Objects",
                    "WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Browser Helper Objects"]
        
        bhos = []
        
        for hive in self.hives:
            for k in bho_keys:
                try:
                    for sks in Registry.Registry(hive).open(k).subkeys():
                        bhos.append(sks.name())
                
                except Registry.RegistryKeyNotFoundException:
                    continue
                    
        for clsids in bhos:
            try:
                clsids_lastwrite = Registry.Registry(hive).open("Classes\\CLSID\\%s" % (clsids)).timestamp()
                value = Registry.Registry(hive).open("Classes\\CLSID\\%s" % (clsids)).name()
                inproc_lastwrite = Registry.Registry(hive).open("Classes\\CLSID\\%s" % (clsids)).subkey("InProcServer32").timestamp()
                data = Registry.Registry(hive).open("Classes\\CLSID\\%s" % (clsids)).subkey("InProcServer32").value('').value()
            except Registry.RegistryKeyNotFoundException:
                continue
            
            if self.format_file is not None:                
                with open(self.format_file[0], "rb") as f:
                    template = env.from_string(f.read())
                    sys.stdout.write(template.render(clsids_lastwrite=clsids_lastwrite, \
                                                     value=value, \
                                                     inproc_lastwrite=inproc_lastwrite, \
                                                     data=data) + "\n")
            elif self.format is not None:           
                template = Environment().from_string(self.format[0])
                sys.stdout.write(template.render(clsids_lastwrite=clsids_lastwrite, \
                                                     value=value, \
                                                     inproc_lastwrite=inproc_lastwrite, \
                                                     data=data) + "\n")
