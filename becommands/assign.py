"""Assign an individual or group to fix a bug"""
from libbe import bugdir, cmdutil, names 
__desc__ = __doc__

def execute(args):
    """
    >>> from libbe import tests, names
    >>> import os
    >>> dir = tests.simple_bug_dir()
    >>> os.chdir(dir.dir)
    >>> dir.get_bug("a").assigned is None
    True
    >>> execute(("a",))
    >>> dir.get_bug("a").assigned == names.creator()
    True
    >>> execute(("a", "someone"))
    >>> dir.get_bug("a").assigned
    'someone'
    >>> execute(("a","none"))
    >>> dir.get_bug("a").assigned is None
    True
    >>> tests.clean_up()
    """
    assert(len(args) in (0, 1, 2))
    if len(args) == 0:
        print help()
        return
    bug = cmdutil.get_bug(args[0])
    if len(args) == 1:
        bug.assigned = names.creator()
    elif len(args) == 2:
        if args[1] == "none":
            bug.assigned = None
        else:
            bug.assigned = args[1]
    bug.save()


def help():
    return """be assign bug-id [assignee]

Assign a person to fix a bug.

By default, the bug is self-assigned.  If an assignee is specified, the bug
will be assigned to that person.

Assignees should be the person's Bugs Everywhere identity, the string that
appears in Creator fields.

To un-assign a bug, specify "none" for the assignee.
"""
