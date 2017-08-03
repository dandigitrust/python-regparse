"""
Author: Patrick Olsen
Email: patrick.olsen@sysforensics.org
Twitter: @patrickrolsen

Thanks to Willi Ballenthin for https://github.com/williballenthin/python-registry
"""

import argparse
import os

import regparse
from regparse.PluginManager import RegparsePluginManager


def main():
    parser = argparse.ArgumentParser(description='Parse Windows Registry hives.')
    parser.add_argument('--plugin', required=False,
                        help='Specify plugin to run.')
    parser.add_argument('--listplugins', required=False, 
                        action='store_true', 
                        help='Lists all of the available plugins.')
    parser.add_argument('--plugindetails', required=False, 
                        action='store_true', 
                        help='Lists details available plugins.')
    parser.add_argument('--hives', required=False, 
                        nargs='*', 
                        help='Registry Hives.')
    parser.add_argument('--search', required=False, 
                        nargs='*',
                        help='Provide a search value and search the hive(s).')     
    parser.add_argument('--format', action="store", metavar="format",
                        nargs=1, dest="format",
                        help="Custom output.")
    parser.add_argument('--format_file', action="store", metavar="format_file",
                        nargs=1, dest="format_file",
                        help="Custom output template.")
    args = parser.parse_args()

    regparse_package_dir = os.path.abspath(os.path.dirname(regparse.__file__))
    plugin_directory = os.path.join(regparse_package_dir, "plugins/")

    if args.listplugins:
        RegparsePluginManager().listPlugin(plugin_directory)
    
    elif args.plugindetails:
        RegparsePluginManager().detailedPlugin(plugin_directory)
    
    elif args.plugin is not None:
        found_plugin = RegparsePluginManager().findPlugin(args.plugin, plugin_directory)
        activated_plugin = RegparsePluginManager().loadPlugin(args.plugin, found_plugin)
        
        activated_plugin.PluginClass(args.hives, args.search, args.format, args.format_file).ProcessPlugin()

    else:
        exit(0)

if __name__ == "__main__":
    main()
