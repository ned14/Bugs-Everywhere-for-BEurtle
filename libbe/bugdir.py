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
import os
import os.path
import errno
import time
import unittest
import doctest

from beuuid import uuid_gen
import mapfile
import bug
import cmdutil
import utility
from rcs import rcs_by_name, detect_rcs, installed_rcs, PathNotInRoot

class NoBugDir(Exception):
    def __init__(self, path):
        msg = "The directory \"%s\" has no bug directory." % path
        Exception.__init__(self, msg)
        self.path = path

class NoRootEntry(Exception):
    def __init__(self, path):
        self.path = path
        Exception.__init__(self, "Specified root does not exist: %s" % path)

class AlreadyInitialized(Exception):
    def __init__(self, path):
        self.path = path
        Exception.__init__(self, 
                           "Specified root is already initialized: %s" % path)

class InvalidValue(ValueError):
    def __init__(self, name, value):
        msg = "Cannot assign value %s to %s" % (value, name)
        Exception.__init__(self, msg)
        self.name = name
        self.value = value


TREE_VERSION_STRING = "Bugs Everywhere Tree 1 0\n"


def setting_property(name, valid=None, doc=None):
    def getter(self):
        value = self.settings.get(name) 
        if valid is not None:
            if value not in valid:
                raise InvalidValue(name, value)
        return value
    
    def setter(self, value):
        if valid is not None:
            if value not in valid and value is not None:
                raise InvalidValue(name, value)
        if value is None:
            del self.settings[name]
        else:
            self.settings[name] = value
        self._save_settings(self.get_path("settings"), self.settings)
    
    return property(getter, setter, doc=doc)


class BugDir (list):
    """
    File-system access:
    When rooted in non-bugdir directory, BugDirs live completely in
    memory until the first call to .save().  This creates a '.be'
    sub-directory containing configurations options, bugs, comments,
    etc.  Once this sub-directory has been created (possibly by
    another BugDir instance) any changes to the BugDir in memory will
    be flushed to the file system automatically.  However, the BugDir
    will only load information from the file system when it loads new
    bugs/comments that it doesn't already have in memory, or when it
    explicitly asked to do so (e.g. .load() or __init__(loadNow=True)).
    """
    def __init__(self, root=None, sink_to_existing_root=True,
                 assert_new_BugDir=False, allow_rcs_init=False,
                 loadNow=False, rcs=None):
        list.__init__(self)
        self.settings = {}
        if root == None:
            root = os.getcwd()
        if sink_to_existing_root == True:
            self.root = self.find_root(root)
        else:
            if not os.path.exists(root):
                raise NoRootEntry(root)
            self.root = root
        if loadNow == True:
            self.load()
        else:
            if assert_new_BugDir == True:
                if os.path.exists(self.get_path()):
                    raise AlreadyInitialized, self.get_path()
            if rcs == None:
                rcs = self.guess_rcs(allow_rcs_init)
            self.rcs = rcs

    def find_root(self, path):
        """
        Search for an existing bug database dir and it's ancestors and
        return a BugDir rooted there.
        """
        if not os.path.exists(path):
            raise NoRootEntry(path)
        versionfile = utility.search_parent_directories(path, os.path.join(".be", "version"))
        if versionfile != None:
            beroot = os.path.dirname(versionfile)
            root = os.path.dirname(beroot)
            return root
        else:
            beroot = utility.search_parent_directories(path, ".be")
            if beroot == None:
                raise NoBugDir(path)
            return beroot
        
    def get_version(self, path=None):
        if path == None:
            path = self.get_path("version")
        try:
            tree_version = self.rcs.get_file_contents(path)
        except AttributeError, e:
            # haven't initialized rcs yet
            tree_version = file(path, "rb").read().decode("utf-8")
        return tree_version

    def set_version(self):
        self.rcs.set_file_contents(self.get_path("version"), TREE_VERSION_STRING)

    rcs_name = setting_property("rcs_name",
                                ("None", "bzr", "git", "Arch", "hg"),
                                doc="The name of the current RCS.  Kept seperate to make saving/loading settings easy.  Don't set this attribute.  Set .rcs instead, and .rcs_name will be automatically adjusted.")

    _rcs = None

    def _get_rcs(self):
        return self._rcs

    def _set_rcs(self, rcs):
        if rcs == None:
            rcs = rcs_by_name("None")
        self._rcs = rcs
        rcs.root(self.root)
        self.rcs_name = rcs.name

    rcs = property(_get_rcs, _set_rcs, doc="A revision control system (RCS) instance")

    target = setting_property("target", doc="The current project development target")

    def get_path(self, *args):
        my_dir = os.path.join(self.root, ".be")
        if len(args) == 0:
            return my_dir
        assert args[0] in ["version", "settings", "bugs"], str(args)
        return os.path.join(my_dir, *args)

    def guess_rcs(self, allow_rcs_init=False):
        deepdir = self.get_path()
        if not os.path.exists(deepdir):
            deepdir = os.path.dirname(deepdir)
        rcs = detect_rcs(deepdir)
        install = False
        if rcs.name == "None":
            if allow_rcs_init == True:
                rcs = installed_rcs()
                rcs.init(self.root)
        self.rcs = rcs
        return rcs

    def load(self):
        version = self.get_version()
        if version != TREE_VERSION_STRING:
            raise NotImplementedError, "BugDir cannot handle version '%s' yet." % version
        else:
            if not os.path.exists(self.get_path()):
                raise NoBugDir(self.get_path())
            self.settings = self._get_settings(self.get_path("settings"))
            self.rcs = rcs_by_name(self.rcs_name)
            self._clear_bugs()
            for uuid in self.list_uuids():
                self._load_bug(uuid)
            
        self._bug_map_gen()

    def save(self):
        self.rcs.mkdir(self.get_path())
        self.set_version()
        self._save_settings(self.get_path("settings"), self.settings)
        self.rcs.mkdir(self.get_path("bugs"))
        for bug in self:
            bug.save()

    def _get_settings(self, settings_path):
        try:
            settings = mapfile.map_load(settings_path)
        except mapfile.NoSuchFile:
            settings = {"rcs_name": "None"}
        return settings

    def _save_settings(self, settings_path, settings):
        if not os.path.exists(self.get_path()):
            # don't save settings until the bug directory has been
            # initialized.  this initialization happens the first time
            # a bug directory is saved (BugDir.save()).  If the user
            # is just working with a BugDir in memory, we don't want
            # to go cluttering up his file system with settings files.
            return
        try:
            mapfile.map_save(self.rcs, settings_path, settings)
        except PathNotInRoot, e:
            # Special case for configuring duplicate bugdir settings
            none_rcs = rcs_by_name("None")
            none_rcs.root(settings_path)
            mapfile.map_save(none_rcs, settings_path, settings)

    def duplicate_bugdir(self, revision):
        duplicate_path = self.rcs.duplicate_repo(revision)

        # setup revision RCS as None, since the duplicate may not be initialized for versioning
        duplicate_settings_path = os.path.join(duplicate_path, ".be", "settings")
        duplicate_settings = self._get_settings(duplicate_settings_path)
        if "rcs_name" in duplicate_settings:
            duplicate_settings["rcs_name"] = "None"
            self._save_settings(duplicate_settings_path, duplicate_settings)

        return BugDir(duplicate_path, loadNow=True)

    def remove_duplicate_bugdir(self):
        self.rcs.remove_duplicate_repo()

    def _bug_map_gen(self):
        map = {}
        for bug in self:
            map[bug.uuid] = bug
        self.bug_map = map

    def list_uuids(self):
        uuids = []
        if os.path.exists(self.get_path()):
            # list the uuids on disk
            for uuid in os.listdir(self.get_path("bugs")):
                if not (uuid.startswith('.')):
                    uuids.append(uuid)
                    yield uuid
        # and the ones that are still just in memory
        for bug in self:
            if bug.uuid not in uuids:
                uuids.append(bug.uuid)
                yield bug.uuid

    def _clear_bugs(self):
        while len(self) > 0:
            self.pop()

    def _load_bug(self, uuid):
        bg = bug.Bug(bugdir=self, uuid=uuid, loadNow=True)
        self.append(bg)
        self._bug_map_gen()
        return bg

    def new_bug(self, uuid=None, summary=None):
        bg = bug.Bug(bugdir=self, uuid=uuid, summary=summary)
        self.append(bg)
        self._bug_map_gen()
        return bg

    def remove_bug(self, bug):
        self.remove(bug)
        bug.remove()

    def bug_shortname(self, bug):
        """
        Generate short names from uuids.  Picks the minimum number of
        characters (>=3) from the beginning of the uuid such that the
        short names are unique.
        
        Obviously, as the number of bugs in the database grows, these
        short names will cease to be unique.  The complete uuid should be
        used for long term reference.
        """
        chars = 3
        for uuid in self.bug_map.keys():
            if bug.uuid == uuid:
                continue
            while (bug.uuid[:chars] == uuid[:chars]):
                chars+=1
        return bug.uuid[:chars]

    def bug_from_shortname(self, shortname):
        """
        >>> bd = simple_bug_dir()
        >>> bug_a = bd.bug_from_shortname('a')
        >>> print type(bug_a)
        <class 'libbe.bug.Bug'>
        >>> print bug_a
        a:om: Bug A
        """
        matches = []
        for bug in self:
            if bug.uuid.startswith(shortname):
                matches.append(bug)
        if len(matches) > 1:
            raise cmdutil.UserError("More than one bug matches %s.  Please be more"
                                    " specific." % shortname)
        if len(matches) == 1:
            return matches[0]
        raise KeyError("No bug matches %s" % shortname)

    def bug_from_uuid(self, uuid):
        if uuid not in self.bug_map:
            self._bug_map_gen()
            if uuid not in self.bug_map:
                raise KeyError("No bug matches %s" % uuid +str(self.bug_map)+str(self))
        return self.bug_map[uuid]


def simple_bug_dir():
    """
    For testing
    >>> bugdir = simple_bug_dir()
    >>> ls = list(bugdir.list_uuids())
    >>> ls.sort()
    >>> print ls
    ['a', 'b']
    """
    dir = utility.Dir()
    assert os.path.exists(dir.path)
    bugdir = BugDir(dir.path, sink_to_existing_root=False, allow_rcs_init=True)
    bugdir._dir_ref = dir # postpone cleanup since dir.__del__() removes dir.
    bug_a = bugdir.new_bug("a", summary="Bug A")
    bug_a.creator = "John Doe <jdoe@example.com>"
    bug_a.time = 0
    bug_b = bugdir.new_bug("b", summary="Bug B")
    bug_b.creator = "Jane Doe <jdoe@example.com>"
    bug_b.time = 0
    bug_b.status = "closed"
    bugdir.save()
    return bugdir


class BugDirTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
    def setUp(self):
        self.dir = utility.Dir()
        self.bugdir = BugDir(self.dir.path, sink_to_existing_root=False, allow_rcs_init=True)
        self.rcs = self.bugdir.rcs
    def tearDown(self):
        self.rcs.cleanup()
        self.dir.cleanup()
    def fullPath(self, path):
        return os.path.join(self.dir.path, path)
    def assertPathExists(self, path):
        fullpath = self.fullPath(path)
        self.failUnless(os.path.exists(fullpath)==True,
                        "path %s does not exist" % fullpath)
        self.assertRaises(AlreadyInitialized, BugDir,
                          self.dir.path, assertNewBugDir=True)
    def versionTest(self):
        if self.rcs.versioned == False:
            return
        original = self.bugdir.rcs.commit("Began versioning")
        bugA = self.bugdir.bug_from_uuid("a")
        bugA.status = "fixed"
        self.bugdir.save()
        new = self.rcs.commit("Fixed bug a")
        dupdir = self.bugdir.duplicate_bugdir(original)
        self.failUnless(dupdir.root != self.bugdir.root, "%s, %s" % (dupdir.root, self.bugdir.root))
        bugAorig = dupdir.bug_from_uuid("a")
        self.failUnless(bugA != bugAorig, "\n%s\n%s" % (bugA.string(), bugAorig.string()))
        bugAorig.status = "fixed"
        self.failUnless(bug.cmp_status(bugA, bugAorig)==0, "%s, %s" % (bugA.status, bugAorig.status))
        self.failUnless(bug.cmp_severity(bugA, bugAorig)==0, "%s, %s" % (bugA.severity, bugAorig.severity))
        self.failUnless(bug.cmp_assigned(bugA, bugAorig)==0, "%s, %s" % (bugA.assigned, bugAorig.assigned))
        self.failUnless(bug.cmp_time(bugA, bugAorig)==0, "%s, %s" % (bugA.time, bugAorig.time))
        self.failUnless(bug.cmp_creator(bugA, bugAorig)==0, "%s, %s" % (bugA.creator, bugAorig.creator))
        self.failUnless(bugA == bugAorig, "\n%s\n%s" % (bugA.string(), bugAorig.string()))
        self.bugdir.remove_duplicate_bugdir()
        self.failUnless(os.path.exists(dupdir.root)==False, str(dupdir.root))
    def testRun(self):
        self.bugdir.new_bug(uuid="a", summary="Ant")
        self.bugdir.new_bug(uuid="b", summary="Cockroach")
        self.bugdir.new_bug(uuid="c", summary="Praying mantis")
        length = len(self.bugdir)
        self.failUnless(length == 3, "%d != 3 bugs" % length)
        uuids = list(self.bugdir.list_uuids())
        self.failUnless(len(uuids) == 3, "%d != 3 uuids" % len(uuids))
        self.failUnless(uuids == ["a","b","c"], str(uuids))
        bugA = self.bugdir.bug_from_uuid("a")
        bugAprime = self.bugdir.bug_from_shortname("a")
        self.failUnless(bugA == bugAprime, "%s != %s" % (bugA, bugAprime))
        self.bugdir.save()
        self.versionTest()

unitsuite = unittest.TestLoader().loadTestsFromTestCase(BugDirTestCase)
suite = unittest.TestSuite([unitsuite])#, doctest.DocTestSuite()])
