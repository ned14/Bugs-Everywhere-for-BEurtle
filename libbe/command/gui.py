# Copyright (C) 2012 Niall Douglas <http://www.nedproductions.biz/>
#
# This file is part of Bugs Everywhere.
#
# Bugs Everywhere is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option) any
# later version.
#
# Bugs Everywhere is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Bugs Everywhere.  If not, see <http://www.gnu.org/licenses/>.

import sys, os, subprocess

import libbe
import libbe.command


class Gui (libbe.command.Command):
    """Opens a GUI for issue management
    """
    name = 'gui'

    def __init__(self, *args, **kwargs):
        libbe.command.Command.__init__(self, *args, **kwargs)
        self.args.extend([
                libbe.command.Argument(
                    name='path', metavar='"path"', default=None,
                    optional=True),
               ])

    def _run(self, **params):
        path=params['path'] if 'path' in params else None
        exepath=os.path.dirname(os.path.abspath(__file__))
        while len(exepath)>3 and not os.path.exists(os.path.join(exepath, "begui")) and not os.path.exists(os.path.join(exepath, "begui.exe")):
            exepath=os.path.dirname(exepath)
        if len(exepath)<=3:
            sys.stderr.write("ERROR: Couldn't find begui or begui.exe in any directory above my location\n")
            return 1
        exepath=os.path.join(exepath, "begui")
        args=[exepath]
        if path is not None: args.append(path)
        print("Executing '%s'" % " ".join(args))
        return subprocess.call(args)

    def _long_help(self):
        return """
Opens a GUI for issue management
"""
