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
import yapsy.PluginManager
from yapsy.PluginManager import PluginManager
from plugins import runkeys
#import logging
#logging.basicConfig(level=logging.DEBUG)

class ListPlugins(object):

    def __init__(self, plugin_name=None, hive=None):
        self.plugin_name = plugin_name
        self.hive = hive

    def AllPlugins(self):
        manager = yapsy.PluginManager.PluginManager()
        manager.setPluginPlaces(['plugins'])
        manager.setPluginInfoExtension("plugin")
        #manager.setCategoriesFilter({
        #    "Persistence" : <>,
        #    "User" : <>,
        #    "Internet": <>,
        #})
        manager.collectPlugins()
        
        for self.pluginInfo in manager.getAllPlugins():
            print('%s:\n\tVer: %s\n\tDescription: %s\n\tFields: %s' % (self.pluginInfo.name.upper(), \
                                     self.pluginInfo.version, \
                                     self.pluginInfo.description, \
                                     self.pluginInfo.fields))

    def Plugin(self):
        manager = yapsy.PluginManager.PluginManager()
        manager.setPluginPlaces(['plugins'])
        manager.setPluginInfoExtension("plugin")
        manager.collectPlugins()

        for self.pluginInfo in manager.getAllPlugins():
            if self.pluginInfo.name == self.plugin_name:
                return(self.pluginInfo.name)
            else:
                print "Couldn't find tht plugin. Here is a list of current plugins."
                return([ListPlugins().AllPlugins()])
            exit(0)
    
    def ActivatePlugin(self):
        manager = yapsy.PluginManager.PluginManager()
        manager.setPluginPlaces(['plugins'])
        manager.setPluginInfoExtension("plugin")
        manager.collectPlugins()
        
        for pluginInfo in manager.getAllPlugins():
            if pluginInfo.name == self.plugin_name:
                if self.plugin_name is not None:
                    if pluginInfo is not None:
                        manager.activatePluginByName(pluginInfo.name)
                        return(pluginInfo.plugin_object)