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

import sys, inspect

import libbe
import libbe.command
import libbe.storage


class Vcs (libbe.command.Command):
    """Perform an operation to the underlying VCS
    """
    name = 'vcs'
    commands=['version', 'get_user_id', 'detect', 'root', 'init', 'destroy', 'add', 'remove', 'get_file_contents', 'path', 'isdir', 'listdir', 'commit', 'revision_id', 'changed']

    def __init__(self, *args, **kwargs):
        libbe.command.Command.__init__(self, *args, **kwargs)
        self.args.extend([
                libbe.command.Argument(
                    name='command', metavar='|'.join(self.commands), default=None,
                    optional=False),
                libbe.command.Argument(name='commandargs', metavar='"command args"', optional=True),
               ])

    def _run(self, **params):
        assert params['command'] in self.commands, 'Unsupported command.'
        storage = self._get_storage()
        cmd='_vcs_'+params['command']
        vcs_commands=dict([c for c in inspect.getmembers(storage, inspect.ismethod) if c[0][:5]=='_vcs_'])
        assert cmd in vcs_commands, 'Command missing from storage backend!'
        argspec=inspect.getargspec(vcs_commands[cmd])[0]
        if len(argspec): del argspec[0]
        args=[]
        if len(argspec)>0:
            assert params['commandargs'] is not None, 'Command needs arguments '+str(argspec)+'.'
            args+=params['commandargs'].split(' ')
        try:
            print >> self.stdout, "Calling", cmd, "with", args
            output=vcs_commands[cmd](*args)
            print >> self.stdout, "RESULT: "+str(output)
        except Exception, e:
            print >> self.stdout, "ERROR: "+str(e)
            return 1

    def _long_help(self):
        return """
Perform an operation to the underlying VCS.

This simply sends the specified command to whatever VCS is housing
this BE repo. This lets you interface with the underlying VCS via
BE rather than having to write your own support code. 
"""
