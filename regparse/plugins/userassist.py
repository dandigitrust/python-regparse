import sys
import struct
from Registry import Registry
from jinja2 import Environment, PackageLoader
import codecs
from datetime import datetime, timedelta

from regparse.PluginManager import PluginBase


class PluginClass(PluginBase):
    default_template = 'userassist.html'

    def process_keys(self, hive):
        userassist = "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\UserAssist"

        #Giuds for the various Operating Systems
        guids = ["{CEBFF5CD-ACE2-4F4F-9178-9926F41749EA}",
                 "{F4E57C4B-2036-45F0-A9AB-443BCFE33D9F}",
                 "{5E6AB780-7743-11CF-A12B-00AA004AE837}",
                 "{75048700-EF1F-11D0-9888-006097DEACF9}"
                 ]
        userassist_entries = []
        
        #Reference: registrydecoder.googlecode.com/svn/trunk/templates/template_files/user_assist.py
        for g in guids:
            try:
                for sks in Registry.Registry(hive).open(userassist).subkey(g).subkey("Count").values():
                    #Windows 7
                    if len(sks.value()) > 16:# 68:
                        runcount = struct.unpack("I", sks.value()[4:8])[0]
                        date = struct.unpack("Q", sks.value()[60:68])[0]
                        last_write = Registry.Registry(hive).open(userassist).subkey(g).subkey("Count").timestamp()
                        key = Registry.Registry(hive).open(userassist).subkey(g).name()
                        skey = Registry.Registry(hive).open(userassist).subkey(g).subkey("Count").name()
                        sub_key = key + skey
                        windate = self.convert_wintime(date)
                        data = codecs.decode(sks.name(), 'rot_13')
                        
                        userassist_entries.append((last_write, sub_key, runcount, windate, data))
                    
                    #Windows XP
                    elif len(sks.value()) == 16:
                        last_write = Registry.Registry(hive).open(userassist).subkey(g).subkey("Count").timestamp()
                        key = Registry.Registry(hive).open(userassist).subkey(g).name()
                        skey = Registry.Registry(hive).open(userassist).subkey(g).subkey("Count").name()
                        sub_key = key + skey                        
                        session, runcount, date = struct.unpack("IIQ", sks.value())
                        runcount -= 5
                        windate = self.convert_wintime(date)
                        data = codecs.decode(sks.name(), 'rot_13')
                        
                        #print last_write, sub_key, runcount, windate, data
                        userassist_entries.append((last_write, sub_key, runcount, windate, data))
        
            except Registry.RegistryKeyNotFoundException as e:
                continue
            
        return userassist_entries

    def result_to_data(self, result):
        return dict(
            last_write=result[0],
            sub_key=result[1],
            runcount=result[2],
            windate=result[3],
            data=result[4]
        )
