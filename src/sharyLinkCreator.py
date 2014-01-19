#!/usr/bin/python3
# encoding: utf-8
'''
sharyLinkCreator -- Share files using your own public server instance

@author:     Adrien CLERC

@copyright:  2014

@license:    MIT

@contact:    bugs-github@antipoul.fr
'''

import sys
import os.path
import re

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from datetime import datetime

from owncloud import OwncloudService
from utils import UploadPaths

import zenityUI

ui = zenityUI

__all__ = []
__version__ = 0.1
__date__ = '2014-01-01'
__updated__ = '2014-01-01'

LINKS_DIRECTORY = '/sharyLinkCreator/'

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def parse_commandline():
    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Adrien CLERC on %s.
  Copyright 2014. All rights reserved.

  Licensed under the MIT License

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))


    server = None
    username = None
    password = None
    paths = None
    verbose = None
    no_recurse = None
    inpat = None
    expat = None
    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-s', '--server', dest='server', help='Your sharing server, e.g. https://owncloud.example.org', required = True)
        parser.add_argument('-u', '--username', dest='username', help='Username')
        parser.add_argument('-p', '--password', dest='password', help='Your password')
        parser.add_argument("--no-recursion", dest="no_recurse", action="store_true", help="Disable recurse into subfolders [default: %(default)s]")
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument("-i", "--include", dest="include", type=re.compile, help="only include paths matching this regex pattern. Note: exclude is given preference over include. [default: %(default)s]", metavar="PATTERN" )
        parser.add_argument("-e", "--exclude", dest="exclude", type=re.compile, help="exclude paths matching this regex pattern. [default: %(default)s]", metavar="PATTERN" )
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest="paths", help="paths to folder(s) with source file(s) [default: %(default)s]", metavar="path", nargs='+')

        # Process arguments
        args = parser.parse_args()
        
        server = args.server
        username = args.username
        password = args.password
        paths = args.paths
        verbose = args.verbose
        no_recurse = args.no_recurse
        inpat = args.include
        expat = args.exclude

    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help\n")
        raise
        
    return (server, username, password, paths, verbose, no_recurse, inpat, expat)

def build_paths(paths, include, exclude, recurse):
    # TODO : renvoyer un dictionnaire avec répertoire de base en absolu: liste de fichiers
    def apply_patterns(path, include, exclude):
        # Apply excludes first
        if exclude and exclude.match(path):
            return False
        # Then if includes, apply it
        elif include:
            if not include.match(path):
                return False
        # Here the file passed all filters
        return True
    
    built_paths = UploadPaths()
    # Take all absolute path first
    paths[:] = [os.path.split(os.path.abspath(path)) for path in paths]
    # And now filter them
    paths[:] = [(base, name) for (base, name) in paths if apply_patterns(name, include, exclude)]
    
    for (base, filename) in paths:
        built_paths.setdefault(base, []).append(filename)
        if os.path.isdir(os.path.join(base, filename)):
            files = built_paths[base]
            for (parent, subdirnames, subfilenames) in os.walk(os.path.join(base, filename)):
                # Replace the base to make the path relative to it
                parent = os.path.relpath(parent, base)
                # Filter, modifying list inplace, to disallow recursion if the directory is excluded
                subdirnames[:] = [subdirname for subdirname in subdirnames if apply_patterns(subdirname, include, exclude)]
                subfilenames[:] = [subfilename for subfilename in subfilenames if apply_patterns(subfilename, include, exclude)]
                files += [os.path.join(parent, dirname) for dirname in subdirnames]
                files += [os.path.join(parent, subfilename) for subfilename in subfilenames]
                    
            
    return built_paths

def main(argv=None):
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    (server, username, password, paths, verbose, no_recurse, include, exclude) = parse_commandline()
    
    monitor = ui.show_progress_dialog('Connecting to {}'.format(server), True)
    
    monitor.write_progress(0, 'Building path list')
    upload_paths = build_paths(paths, include, exclude, not no_recurse)
    if not upload_paths:
        return
    
    if not username or not password:
        # Close monitor while asking credentials
        monitor.close()
        (username, password) = ui.ask_credentials(server, username)
        # Restore monitor
        monitor = ui.show_progress_dialog('Connecting to {}'.format(server), True)
    
    service = None
    
    monitor.write_progress(0, 'Validating credentials')
    try:
        service = OwncloudService(server, username, password)
    except Exception as e:
        monitor.close()
        ui.show_error(str(e))
        return
    
    base_directory = LINKS_DIRECTORY
    single_file = upload_paths.total_size == 1
    if not single_file:
        base_directory += '{}/'.format(datetime.today())
        
    monitor.write_progress(0, 'Creating base directory')
    if service.is_directory(base_directory) or service.create_directory(base_directory, '/'):
        monitor.close()
        monitor = ui.show_progress_dialog('Uploading files')
        failed_files = service.upload_files(upload_paths, base_directory, progress_monitor = monitor)
        
        sharedPath = base_directory + '/' + upload_paths.full_paths()[0] if single_file else base_directory
        print('Sharing {}…'.format(sharedPath))
        share_link = service.share_path(sharedPath)
        print('Shared link: {}'.format(share_link))
        
        try:
            from sh import xsel
            xsel('-i', _in = str(share_link))
        except Exception as e:
            print('Unable to copy to clipboard: {}'.format(e))
        ui.show_shared_url(share_link, failed_files)
        
    else:
        monitor.close()
        ui.show_error('Fail to create base directory {}'.format(base_directory))
    
if __name__ == "__main__":
        
    
    sys.exit(main())