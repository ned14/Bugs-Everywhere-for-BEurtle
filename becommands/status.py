# Copyright (C) 2005 Aaron Bentley and Panometrics, Inc.
# <abentley@panoramicfeedback.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""Show or change a bug's status"""
from libbe import cmdutil, bugdir, bug
__desc__ = __doc__

def execute(args, test=False):
    """
    >>> import os
    >>> bd = bugdir.simple_bug_dir()
    >>> os.chdir(bd.root)
    >>> execute(["a"], test=True)
    open
    >>> execute(["a", "closed"], test=True)
    >>> execute(["a"], test=True)
    closed
    >>> execute(["a", "none"], test=True)
    Traceback (most recent call last):
    UserError: Invalid status: none
    """
    parser = get_parser()
    options, args = parser.parse_args(args)
    complete(options, args, parser)
    if len(args) not in (1,2):
        raise cmdutil.UsageError
    bd = bugdir.BugDir(from_disk=True, manipulate_encodings=not test)
    bug = bd.bug_from_shortname(args[0])
    if len(args) == 1:
        print bug.status
    else:
        try:
            bug.status = args[1]
        except ValueError, e:
            if e.name != "status":
                raise
            raise cmdutil.UserError ("Invalid status: %s" % e.value)
        bd.save()

def get_parser():
    parser = cmdutil.CmdOptionParser("be status BUG-ID [STATUS]")
    return parser


def help():
    longhelp=["""
Show or change a bug's status.

If no status is specified, the current value is printed.  If a status
is specified, it will be assigned to the bug.

Status levels are:
"""]
    try: # See if there are any per-tree status configurations
        bd = bugdir.BugDir(from_disk=True, manipulate_encodings=False)
    except bugdir.NoBugDir, e:
        pass # No tree, just show the defaults
    longest_status_len = max([len(s) for s in bug.status_values])
    for status in bug.status_values :
        description = bug.status_description[status]
        s = "%*s : %s\n" % (longest_status_len, status, description)
        longhelp.append(s)
    longhelp = ''.join(longhelp)
    return get_parser().help_str() + longhelp

def complete(options, args, parser):
    for option,value in cmdutil.option_value_pairs(options, parser):
        if value == "--complete":
            # no argument-options at the moment, so this is future-proofing
            raise cmdutil.GetCompletions()
    for pos,value in enumerate(args):
        if value == "--complete":
            try: # See if there are any per-tree status configurations
                bd = bugdir.BugDir(from_disk=True,
                                   manipulate_encodings=False)
            except bugdir.NoBugDir:
                bd = None
            if pos == 0: # fist positional argument is a bug id 
                ids = []
                if bd != None:
                    bd.load_all_bugs()
                    ids = [bd.bug_shortname(bg) for bg in bd]
                raise cmdutil.GetCompletions(ids)
            elif pos == 1: # second positional argument is a status
                raise cmdutil.GetCompletions(bug.status_values)
            raise cmdutil.GetCompletions()
