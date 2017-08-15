from collections import namedtuple

from Registry import Registry

from regparse.PluginManager import PluginBase, Field


class NotAnAmcacheHive(Exception):
    pass


class PluginClass(PluginBase):
    default_template = 'amcache.html'

    def __init__(self,  hives=None, search=None, format=None, format_file=None):
        super(PluginClass, self).__init__(hives=hives, search=search, format=format, format_file=format_file)

        # via: http://www.swiftforensics.com/2013/12/amcachehve-in-windows-8-goldmine-for.html
        # Product Name    UNICODE string
        # ==============================================================================
        # 0   Product Name    UNICODE string
        # 1   Company Name    UNICODE string
        # 2   File version number only    UNICODE string
        # 3   Language code (1033 for en-US)  DWORD
        # 4   SwitchBackContext   QWORD
        # 5   File Version    UNICODE string
        # 6   File Size (in bytes)    DWORD
        # 7   PE Header field - SizeOfImage   DWORD
        # 8   Hash of PE Header (unknown algorithm)   UNICODE string
        # 9   PE Header field - Checksum  DWORD
        # a   Unknown QWORD
        # b   Unknown QWORD
        # c   File Description    UNICODE string
        # d   Unknown, maybe Major & Minor OS version DWORD
        # f   Linker (Compile time) Timestamp DWORD - Unix time
        # 10  Unknown DWORD
        # 11  Last Modified Timestamp FILETIME
        # 12  Created Timestamp   FILETIME
        # 15  Full path to file   UNICODE string
        # 16  Unknown DWORD
        # 17  Last Modified Timestamp 2   FILETIME
        # 100 Program ID  UNICODE string
        # 101 SHA1 hash of file

        self.FIELDS = [
            Field("path", self.make_value_getter("15")),
            Field("sha1", self.make_value_getter("101")),
            Field("size", self.make_value_getter("6")),
            Field("file_description", self.make_value_getter("c")),
            Field("source_key_timestamp", lambda key: key.timestamp()),
            Field("created_timestamp", self.make_windows_timestamp_value_getter("12")),
            Field("modified_timestamp", self.make_windows_timestamp_value_getter("11")),
            Field("modified_timestamp2", self.make_windows_timestamp_value_getter("17")),
            Field("linker_timestamp", self.make_unix_timestamp_value_getter("f")),
            Field("product", self.make_value_getter("0")),
            Field("company", self.make_value_getter("1")),
            Field("pe_sizeofimage", self.make_value_getter("7")),
            Field("version_number", self.make_value_getter("2")),
            Field("version", self.make_value_getter("5")),
            Field("language", self.make_value_getter("3")),
            Field("header_hash", self.make_value_getter("8")),
            Field("pe_checksum", self.make_value_getter("9")),
            Field("amcache_id", self.make_value_getter("100")),
            Field("switchbackcontext", self.make_value_getter("4")),
        ]

    def parse_execution_entry(self, key):
        rv = {}
        for e in self.FIELDS:
            rv[e.name] = e.getter(key)
        return rv

    def process_keys(self, hive):
        reg = Registry.Registry(hive)
        try:
            volumes = reg.open("Root\\File")
        except Registry.RegistryKeyNotFoundException:
            raise NotAnAmcacheHive()

        ret = []
        for volume_key in volumes.subkeys():
            for file_key in volume_key.subkeys():
                ret.append(self.parse_execution_entry(file_key))
        return ret



