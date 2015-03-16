'''
The MIT License (MIT)

Copyright (c) 2015 Patrick Olsen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Author: Patrick Olsen
Email: patrick.olsen@sysforensics.org
Twitter: @patrickrolsen
'''
from modules.PluginManager import ListPlugins
#import logging
#logging.basicConfig(level=logging.DEBUG)

class ProcessHive(object):

    def __init__(self, plugin_name=None, hive=None, format=None, format_file=None):
        self.plugin_name = plugin_name
        self.hive = hive
        self.format = format
        self.format_file = format_file

    def getHive(self, hive=None, format=None, format_file=None, search=None):
        self.hive = hive
        self.format = format
        self.format_file = format_file
        self.search = search
        
        return(ListPlugins(self.plugin_name, self.hive).ActivatePlugin().ProcessPlugin(self.hive, self.format, self.format_file, self.search))