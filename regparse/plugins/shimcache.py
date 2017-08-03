import struct
import cStringIO as sio

import datetime

from regparse.PluginManager import PluginBase
from Registry import Registry

# Values used by Windows 5.2 and 6.0 (Server 2003 through Vista/Server 2008)
CACHE_MAGIC_NT5_2 = 0xbadc0ffe
CACHE_HEADER_SIZE_NT5_2 = 0x8
NT5_2_ENTRY_SIZE32 = 0x18
NT5_2_ENTRY_SIZE64 = 0x20

# Values used by Windows 6.1 (Win7 and Server 2008 R2)
CACHE_MAGIC_NT6_1 = 0xbadc0fee
CACHE_HEADER_SIZE_NT6_1 = 0x80
NT6_1_ENTRY_SIZE32 = 0x20
NT6_1_ENTRY_SIZE64 = 0x30
CSRSS_FLAG = 0x2

# Values used by Windows 5.1 (WinXP 32-bit)
WINXP_MAGIC32 = 0xdeadbeef
WINXP_HEADER_SIZE32 = 0x190
WINXP_ENTRY_SIZE32 = 0x228
MAX_PATH = 520

# Values used by Windows 8
WIN8_STATS_SIZE = 0x80
WIN8_MAGIC = '00ts'

# Magic value used by Windows 8.1
WIN81_MAGIC = '10ts'

# Values used by Windows 10
WIN10_STATS_SIZE = 0x30
WIN10_CREATORS_STATS_SIZE = 0x34
WIN10_MAGIC = '10ts'
CACHE_HEADER_SIZE_NT6_4 = 0x30
CACHE_MAGIC_NT6_4 = 0x30


# Return a unique list while preserving ordering.
def unique_list(li):
    ret_list = []
    for entry in li:
        if entry not in ret_list:
            ret_list.append(entry)
    return ret_list


class PluginClass(PluginBase):
    default_template = 'shimcache.html'

    def process_keys(self, hive):
        reg = Registry.Registry(hive)
        out_list = []

        # Complete hive
        root = reg.root().subkeys()
        for key in root:
            # Check each ControlSet.
            try:
                if 'controlset' in key.name().lower():
                    session_man_key = reg.open('%s\\Control\\Session Manager' % key.name())
                    for subkey in session_man_key.subkeys():
                        # Read the Shim Cache structure.
                        if ('appcompatibility' in subkey.name().lower() or
                                    'appcompatcache' in subkey.name().lower()):
                            bin_data = str(subkey['AppCompatCache'].value())
                            tmp_list = self.read_cache(bin_data)

                            if tmp_list:
                                for row in tmp_list:
                                    if row not in out_list:
                                        out_list.append(row)

            except Registry.RegistryKeyNotFoundException:
                continue

            return out_list

    # Read the Shim Cache format, return a list of last modified dates/paths.
    def read_cache(self, cachebin, quiet=False):

        if len(cachebin) < 16:
            # Data size less than minimum header size.
            return None

        try:
            # Get the format type
            magic = struct.unpack("<L", cachebin[0:4])[0]

            # This is a Windows 2k3/Vista/2k8 Shim Cache format,
            if magic == CACHE_MAGIC_NT5_2:

                # Shim Cache types can come in 32-bit or 64-bit formats. We can
                # determine this because 64-bit entries are serialized with u_int64
                # pointers. This means that in a 64-bit entry, valid UNICODE_STRING
                # sizes are followed by a NULL DWORD. Check for this here.
                test_size = struct.unpack("<H", cachebin[8:10])[0]
                test_max_size = struct.unpack("<H", cachebin[10:12])[0]
                if (test_max_size - test_size == 2 and
                        struct.unpack("<L", cachebin[12:16])[0]) == 0:
                    if not quiet:
                        print "[+] Found 64bit Windows 2k3/Vista/2k8 Shim Cache data..."
                    entry = CacheEntryNt5(False)
                    return self.read_nt5_entries(cachebin, entry)

                # Otherwise it's 32-bit data.
                else:
                    if not quiet:
                        print "[+] Found 32bit Windows 2k3/Vista/2k8 Shim Cache data..."
                    entry = CacheEntryNt5(True)
                    return self.read_nt5_entries(cachebin, entry)

            # This is a Windows 7/2k8-R2 Shim Cache.
            elif magic == CACHE_MAGIC_NT6_1:
                test_size = (struct.unpack("<H",
                                           cachebin[CACHE_HEADER_SIZE_NT6_1:
                                           CACHE_HEADER_SIZE_NT6_1 + 2])[0])
                test_max_size = (struct.unpack("<H", cachebin[CACHE_HEADER_SIZE_NT6_1 + 2:
                CACHE_HEADER_SIZE_NT6_1 + 4])[0])

                # Shim Cache types can come in 32-bit or 64-bit formats.
                # We can determine this because 64-bit entries are serialized with
                # u_int64 pointers. This means that in a 64-bit entry, valid
                # UNICODE_STRING sizes are followed by a NULL DWORD. Check for this here.
                if (test_max_size - test_size == 2 and
                        struct.unpack("<L", cachebin[CACHE_HEADER_SIZE_NT6_1 + 4:
                            CACHE_HEADER_SIZE_NT6_1 + 8])[0]) == 0:
                    if not quiet:
                        print "[+] Found 64bit Windows 7/2k8-R2 Shim Cache data..."
                    entry = CacheEntryNt6(False)
                    return self.read_nt6_entries(cachebin, entry)
                else:
                    if not quiet:
                        print "[+] Found 32bit Windows 7/2k8-R2 Shim Cache data..."
                    entry = CacheEntryNt6(True)
                    return self.read_nt6_entries(cachebin, entry)

            # This is WinXP cache data
            elif magic == WINXP_MAGIC32:
                if not quiet:
                    print "[+] Found 32bit Windows XP Shim Cache data..."
                return self.read_winxp_entries(cachebin)

            # Check the data set to see if it matches the Windows 8 format.
            elif len(cachebin) > WIN8_STATS_SIZE and cachebin[WIN8_STATS_SIZE:WIN8_STATS_SIZE + 4] == WIN8_MAGIC:
                if not quiet:
                    print "[+] Found Windows 8/2k12 Apphelp Cache data..."
                return self.read_win8_entries(cachebin, WIN8_MAGIC)

            # Windows 8.1 will use a different magic dword, check for it
            elif len(cachebin) > WIN8_STATS_SIZE and cachebin[WIN8_STATS_SIZE:WIN8_STATS_SIZE + 4] == WIN81_MAGIC:
                if not quiet:
                    print "[+] Found Windows 8.1 Apphelp Cache data..."
                return self.read_win8_entries(cachebin, WIN81_MAGIC)

            # Windows 10 will use a different magic dword, check for it
            elif len(cachebin) > WIN10_STATS_SIZE and cachebin[WIN10_STATS_SIZE:WIN10_STATS_SIZE + 4] == WIN10_MAGIC:
                if not quiet:
                    print "[+] Found Windows 10 Apphelp Cache data..."
                return self.read_win10_entries(cachebin, WIN10_MAGIC)

            # Windows 10 Creators Update will use a different STATS_SIZE, account for it
            elif len(cachebin) > WIN10_CREATORS_STATS_SIZE and cachebin[
                                                               WIN10_CREATORS_STATS_SIZE:WIN10_CREATORS_STATS_SIZE + 4] == WIN10_MAGIC:
                if not quiet:
                    print "[+] Found Windows 10 Creators Update Apphelp Cache data..."
                return self.read_win10_entries(cachebin, WIN10_MAGIC, creators_update=True)

            else:
                print "[-] Got an unrecognized magic value of 0x%x... bailing" % magic
                return None

        except (RuntimeError, TypeError, NameError), err:
            print "[-] Error reading Shim Cache data: %s" % err
            return None

    # Read Windows 8/2k12/8.1 Apphelp Cache entry formats.
    @classmethod
    def read_win8_entries(cls, bin_data, ver_magic):
        offset = 0
        entry_meta_len = 12
        entry_list = []

        # Skip past the stats in the header
        cache_data = bin_data[WIN8_STATS_SIZE:]

        data = sio.StringIO(cache_data)
        while data.tell() < len(cache_data):
            header = data.read(entry_meta_len)
            # Read in the entry metadata
            # Note: the crc32 hash is of the cache entry data
            magic, crc32_hash, entry_len = struct.unpack('<4sLL', header)

            # Check the magic tag
            if magic != ver_magic:
                raise Exception("Invalid version magic tag found: 0x%x" % struct.unpack("<L", magic)[0])

            entry_data = sio.StringIO(data.read(entry_len))

            # Read the path length
            path_len = struct.unpack('<H', entry_data.read(2))[0]
            if path_len == 0:
                path = None
            else:
                path = entry_data.read(path_len).decode('utf-16le', 'replace').encode('utf-8')

            # Check for package data
            package_len = struct.unpack('<H', entry_data.read(2))[0]
            if package_len > 0:
                # Just skip past the package data if present (for now)
                entry_data.seek(package_len, 1)

            # Read the remaining entry data
            flags, unk_1, low_datetime, high_datetime, unk_2 = struct.unpack('<LLLLL', entry_data.read(20))

            # Check the flag set in CSRSS
            if flags & CSRSS_FLAG:
                exec_flag = True
            else:
                exec_flag = False

            last_mod_date = (low_datetime, high_datetime)

            row = dict(
                last_modified=last_mod_date,
                last_update=None,
                path=path,
                file_size=None,
                exec_flag=exec_flag
            )
            entry_list.append(row)

        return entry_list

    # Read Windows 10 Apphelp Cache entry format
    @classmethod
    def read_win10_entries(cls, bin_data, ver_magic, creators_update=False):

        offset = 0
        entry_meta_len = 12
        entry_list = []

        # Skip past the stats in the header
        if creators_update:
            cache_data = bin_data[WIN10_CREATORS_STATS_SIZE:]
        else:
            cache_data = bin_data[WIN10_STATS_SIZE:]

        data = sio.StringIO(cache_data)
        while data.tell() < len(cache_data):
            header = data.read(entry_meta_len)
            # Read in the entry metadata
            # Note: the crc32 hash is of the cache entry data
            magic, crc32_hash, entry_len = struct.unpack('<4sLL', header)

            # Check the magic tag
            if magic != ver_magic:
                raise Exception("Invalid version magic tag found: 0x%x" % struct.unpack("<L", magic)[0])

            entry_data = sio.StringIO(data.read(entry_len))

            # Read the path length
            path_len = struct.unpack('<H', entry_data.read(2))[0]
            if path_len == 0:
                path = None
            else:
                path = entry_data.read(path_len).decode('utf-16le', 'replace').encode('utf-8')

            # Read the remaining entry data
            low_datetime, high_datetime = struct.unpack('<LL', entry_data.read(8))

            last_mod_date = cls.convert_filetime(low_datetime, high_datetime)

            row = dict(
                last_modified=last_mod_date,
                last_update=None,
                path=path,
                file_size=None,
                exec_flag=None
            )
            entry_list.append(row)

        return entry_list

    # Read Windows 2k3/Vista/2k8 Shim Cache entry formats.
    @classmethod
    def read_nt5_entries(cls, bin_data, entry):

        try:
            entry_list = []
            contains_file_size = False
            entry_size = entry.size()
            exec_flag = ''

            num_entries = struct.unpack('<L', bin_data[4:8])[0]
            if num_entries == 0:
                return None

            # On Windows Server 2008/Vista, the filesize is swapped out of this
            # structure with two 4-byte flags. Check to see if any of the values in
            # "dwFileSizeLow" are larger than 2-bits. This indicates the entry contained file sizes.
            for offset in xrange(CACHE_HEADER_SIZE_NT5_2, (num_entries * entry_size) + CACHE_HEADER_SIZE_NT5_2,
                                 entry_size):

                entry.update(bin_data[offset:offset + entry_size])

                if entry.dwFileSizeLow > 3:
                    contains_file_size = True
                    break

            # Now grab all the data in the value.
            for offset in xrange(CACHE_HEADER_SIZE_NT5_2, (num_entries * entry_size) + CACHE_HEADER_SIZE_NT5_2,
                                 entry_size):

                entry.update(bin_data[offset:offset + entry_size])

                last_mod_date = cls.convert_filetime(entry.dwLowDateTime, entry.dwHighDateTime)

                path = bin_data[entry.Offset:entry.Offset + entry.wLength].decode('utf-16le', 'replace').encode(
                    'utf-8')
                path = path.replace("\\??\\", "")

                # It contains file size data.
                if contains_file_size:
                    hit = dict(
                        last_modified=last_mod_date,
                        last_update=None,
                        path=path,
                        file_size=entry.dwFileSizeLow,
                        exec_flag=None
                    )
                    if hit not in entry_list:
                        entry_list.append(hit)

                # It contains flags.
                else:
                    # Check the flag set in CSRSS
                    if entry.dwFileSizeLow & CSRSS_FLAG:
                        exec_flag = True
                    else:
                        exec_flag = False

                    hit = dict(
                        last_modified=last_mod_date,
                        last_update=None,
                        path=path,
                        file_size=None,
                        exec_flag=exec_flag
                    )
                    if hit not in entry_list:
                        entry_list.append(hit)

            return entry_list

        except (RuntimeError, ValueError, NameError), err:
            print "[-] Error reading Shim Cache data: %s..." % err
            return None

    # Read the Shim Cache Windows 7/2k8-R2 entry format,
    # return a list of last modifed dates/paths.
    @classmethod
    def read_nt6_entries(cls, bin_data, entry):

        try:
            entry_list = []
            exec_flag = ""
            entry_size = entry.size()
            num_entries = struct.unpack('<L', bin_data[4:8])[0]

            if num_entries == 0:
                return None

            # Walk each entry in the data structure.
            for offset in xrange(CACHE_HEADER_SIZE_NT6_1,
                                 num_entries * entry_size + CACHE_HEADER_SIZE_NT6_1,
                                 entry_size):

                entry.update(bin_data[offset:offset + entry_size])
                last_mod_date = cls.convert_filetime(entry.dwLowDateTime, entry.dwHighDateTime)

                path = (bin_data[entry.Offset:entry.Offset +
                        entry.wLength].decode('utf-16le', 'replace').encode('utf-8'))
                path = path.replace("\\??\\", "")

                # Test to see if the file may have been executed.
                if entry.FileFlags & CSRSS_FLAG:
                    exec_flag = True
                else:
                    exec_flag = False
                hit = dict(
                    last_modified=last_mod_date,
                    last_update=None,
                    path=path,
                    file_size=None,
                    exec_flag=exec_flag
                )

                if hit not in entry_list:
                    entry_list.append(hit)
            return entry_list

        except (RuntimeError, ValueError, NameError), err:
            print '[-] Error reading Shim Cache data: %s...' % err
            return None

    # Read the WinXP Shim Cache data. Some entries can be missing data but still
    # contain useful information, so try to get as much as we can.
    @classmethod
    def read_winxp_entries(cls, bin_data):

        entry_list = []

        try:

            num_entries = struct.unpack('<L', bin_data[8:12])[0]
            if num_entries == 0:
                return None

            for offset in xrange(WINXP_HEADER_SIZE32,
                                 (num_entries * WINXP_ENTRY_SIZE32) + WINXP_HEADER_SIZE32, WINXP_ENTRY_SIZE32):

                # No size values are included in these entries, so search for utf-16 terminator.
                path_len = bin_data[offset:offset + (MAX_PATH + 8)].find("\x00\x00")

                # if path is corrupt, procede to next entry.
                if path_len == 0:
                    continue
                path = bin_data[offset:offset + path_len + 1].decode('utf-16le').encode('utf-8')

                # Clean up the pathname.
                path = path.replace('\\??\\', '')
                if len(path) == 0: continue

                entry_data = (offset + (MAX_PATH + 8))

                # Get last mod time.
                last_mod_time = struct.unpack('<2L', bin_data[entry_data:entry_data + 8])
                last_mod_time = cls.convert_filetime(last_mod_time[0], last_mod_time[1])

                # Get last file size.
                file_size = struct.unpack('<2L', bin_data[entry_data + 8:entry_data + 16])[0]
                if file_size == 0:
                    file_size = None

                # Get last update time.
                exec_time = struct.unpack('<2L', bin_data[entry_data + 16:entry_data + 24])
                exec_time = cls.convert_filetime(exec_time[0], exec_time[1])
                hit = dict(
                    last_modified=last_mod_time,
                    last_update=exec_time,
                    path=path,
                    file_size=file_size,
                    exec_flag=None
                )
                if hit not in entry_list:
                    entry_list.append(hit)
            return entry_list

        except (RuntimeError, ValueError, NameError), err:
            print "[-] Error reading Shim Cache data %s" % err
            return None

    @classmethod
    # Convert FILETIME to datetime.
    # Based on http://code.activestate.com/recipes/511425-filetime-to-datetime/
    def convert_filetime(cls, dwLowDateTime, dwHighDateTime):

        try:
            date = datetime.datetime(1601, 1, 1, 0, 0, 0)
            temp_time = dwHighDateTime
            temp_time <<= 32
            temp_time |= dwLowDateTime
            return date + datetime.timedelta(microseconds=temp_time / 10)
        except OverflowError, err:
            return None


# Shim Cache format used by Windows 5.2 and 6.0 (Server 2003 through Vista/Server 2008)
class CacheEntryNt5(object):

    def __init__(self, is32bit, data=None):

        self.is32bit = is32bit
        if data != None:
            self.update(data)

    def update(self, data):

        if self.is32bit:
            entry = struct.unpack('<2H 3L 2L', data)
        else:
            entry = struct.unpack('<2H 4x Q 2L 2L', data)
        self.wLength = entry[0]
        self.wMaximumLength =  entry[1]
        self.Offset = entry[2]
        self.dwLowDateTime = entry[3]
        self.dwHighDateTime = entry[4]
        self.dwFileSizeLow = entry[5]
        self.dwFileSizeHigh = entry[6]

    def size(self):

        if self.is32bit:
            return NT5_2_ENTRY_SIZE32
        else:
            return NT5_2_ENTRY_SIZE64


# Shim Cache format used by Windows 6.1 (Win7 through Server 2008 R2)
class CacheEntryNt6(object):

    def __init__(self, is32bit, data=None):

        self.is32bit = is32bit
        if data != None:
            self.update(data)

    def update(self, data):

        if self.is32bit:
            entry = struct.unpack('<2H 7L', data)
        else:
            entry = struct.unpack('<2H 4x Q 4L 2Q', data)
        self.wLength = entry[0]
        self.wMaximumLength =  entry[1]
        self.Offset = entry[2]
        self.dwLowDateTime = entry[3]
        self.dwHighDateTime = entry[4]
        self.FileFlags = entry[5]
        self.Flags = entry[6]
        self.BlobSize = entry[7]
        self.BlobOffset = entry[8]

    def size(self):

        if self.is32bit:
            return NT6_1_ENTRY_SIZE32
        else:
            return NT6_1_ENTRY_SIZE64
