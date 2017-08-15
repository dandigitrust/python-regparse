import os, io, sys, imp
import ConfigParser
from collections import namedtuple

from Registry import Registry
from Registry.RegistryParse import parse_windows_timestamp as _parse_windows_timestamp

from datetime import datetime, timedelta

from regparse.jinja import JinjaEnv


Field = namedtuple("Field", ["name", "getter"])


class PluginBase(object):
    default_template = None

    def __init__(self, hives=None, search=None, format=None, format_file=None):
        self.hives = hives
        self.search = search
        self.format = format
        self.format_file = format_file

    def process_plugin(self):
        for data in self.process_to_data():
            self.output_data(data)

    def get_template(self):
        env = JinjaEnv.get_env()

        if self.format:
            return env.from_string(self.format[0])
        elif self.format_file:
            with open(self.format_file[0], "rb") as f:
                return env.from_string(f.read())
        elif self.default_template:
            return env.get_template(self.default_template)
        else:
            return None

    def process_keys(self, hive):
        """
        Override this to do all the heavy lifting here.

        :return: a list of "results" of any type.. This will be in turn processed by "result to data"
                 if you do not also override the method result_to_data, this must return a list of dictionaries,
                 each of which can be consumed but output_data
        """
        raise NotImplemented

    def results_to_data_list(self, results):
        """
        This must be overridden if process_keys returns anything other than a list
        :param results: results that comes back from process_keys
        :return: must return a ligitst of result_data dicts
        """
        return [self.result_to_data(r) for r in results]

    def result_to_data(self, result):
        """
        This needs to be overridden if process_keys returns anything other than a list of dictionaries
        :param result: a single result from the list of results from the process_keys method
        :return: a dictionary to be passed to the jinja template
        """
        return result

    def output_data(self, data):
        """
        This is used by the commandline application to output the results to the specified template.
        :param data:
        :return:
        """
        template = self.get_template()
        if template:
            sys.stdout.write(template.render(**data) + '\n')

    def process_to_data(self):
        rv = []
        for hive in self.hives:
            results = self.process_keys(hive)
            rv += self.results_to_data_list(results)
        return rv

    @classmethod
    def convert_wintime(cls, windate):
        # http://stackoverflow.com/questions/4869769/convert-64-bit-windows-date-time-in-python
        us = int(windate) / 10
        first_run = datetime(1601, 1, 1) + timedelta(microseconds=us)
        return first_run

    @classmethod
    def make_value_getter(cls, value_name):
        """ return a function that fetches the value from the registry key """

        def _value_getter(key):
            try:
                return key.value(value_name).value()
            except Registry.RegistryValueNotFoundException:
                return None

        return _value_getter

    @classmethod
    def make_windows_timestamp_value_getter(cls, value_name):
        """
        return a function that fetches the value from the registry key
          as a Windows timestamp.
        """
        f = cls.make_value_getter(value_name)

        def _value_getter(key):
            try:
                ts = f(key)
                if ts:
                    return cls.parse_windows_timestamp(ts)
            except ValueError:
                pass

            return None

        return _value_getter

    @classmethod
    def parse_unix_timestamp(cls, qword):
        return datetime.fromtimestamp(qword)

    @classmethod
    def parse_windows_timestamp(cls, qword):
        try:
            return _parse_windows_timestamp(qword)
        except ValueError:
            return None

    @classmethod
    def make_unix_timestamp_value_getter(cls, value_name):
        """
        return a function that fetches the value from the registry key
          as a UNIX timestamp.
        """
        f = cls.make_value_getter(value_name)

        def _value_getter(key):
            try:
                unix_timestamp = f(key)
                if unix_timestamp:
                    return cls.parse_unix_timestamp(f(key))
            except ValueError:
                pass
            return None

        return _value_getter


class RegparsePluginManager(object):
    def __init__(self, plugin_directory=None, plugin=None):
        self.plugin_directory = plugin_directory
        self.plugin = plugin

    def gatherallPlugins(self, plugin_directory):
        allPlugins = []
        for plugin in os.listdir(plugin_directory):
            if plugin.endswith(".py") and plugin[:-3] != "__init__":
                plugin_name = plugin[:-3]
                allPlugins.append(plugin_name)
        return (allPlugins)

    def listPlugin(self, plugin_directory):
        for plugin in self.gatherallPlugins(plugin_directory):
            print plugin

    def detailedPlugin(self, plugin_directory):
        dict = {}

        for plugin_doc in os.listdir(plugin_directory):
            if plugin_doc.endswith(".plugin"):
                plugin_doc_path = os.path.join(plugin_directory, plugin_doc)
                config = ConfigParser.RawConfigParser(allow_no_value=True)
                config.readfp(open(plugin_doc_path))
                try:
                    plugin = config.get("Documentation", "Plugin")
                    author = config.get("Documentation", "Author")
                    version = config.get("Documentation", "Version")
                    reference = config.get("Documentation", "Reference")
                    printfields = config.get("Documentation", "PrintFields")
                    description = config.get("Documentation", "Description")
                    print plugin.upper()
                    print '\tPlugin: \t%s' % (plugin.upper())
                    print '\tAuthor: \t%s' % (author)
                    print '\tVersion: \t%s' % (version)
                    print '\tReference: \t%s' % (reference)
                    print '\tPrint Fields: \t%s' % (printfields)
                    print '\tDescription: \t%s' % (description)
                except ConfigParser.NoOptionError:
                    print plugin_doc.upper()[:-7] + " does not have a proper .plugin config file."

    def findPlugin(self, plugin, plugin_directory):
        try:
            found_plugins = imp.find_module(plugin, [plugin_directory])

        except ImportError as error:
            print 'Plugin Not Found:', error

        return found_plugins

    def loadPlugin(self, plugin, found_plugin):
        try:
            module = imp.load_module(plugin, found_plugin[0], found_plugin[1], found_plugin[2])
        except TypeError as error:
            print error

        return module


class HelperFunctions(object):
    def __init__(self, hive=None):
        self.hive = hive

    def CurrentControlSet(self):
        select = Registry.Registry(self.hive).open("Select")
        current = select.value("Current").value()
        controlsetnum = "ControlSet00%d" % (current)
        return (controlsetnum)
