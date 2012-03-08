Bugs Everywhere (BEurtle fork)
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
Forked by Niall Douglas http://www.nedprod.com/programs/Win32/BEurtle/

Herein is a fork by me from the master BE GIT repo at http://gitorious.org/be/be.
The main change is that I have patched BE in various ways to make it work better on
Windows. The following may or may not have been incorporated upstream by the time you
read this:

1. Added in a be.bat and be.py as a command

2. Hacked around Windows's inability for parent processes to set the stdin/stdout
charset for child processes by going via environment variables, namely
BE_INPUT_ENCODING and BE_OUTPUT_ENCODING. You can use these to get the BE process
to interpret stdin and stdout as UTF-8 or whatever.

3. Hacked a version generating script (!Generate_version.bat) as most Windows folk
won't have sed and awk kicking around.

4. Made several hacks to enable BE running from within a ZIP archive. This lets you
package up BE into a self contained Windows install which is extremely useful for
BEurtle's purposes. You'll need bbfreeze (easy_install bbfreeze) for the script
!Generate_exe_bbfreeze.py to work, and it will spit out a self-contained directory
into dist.

5. Added be vcs, a thin wrapper for the VCS API in the storage backend. This lets
you talk to the underlying VCS via BE rather than having to write your own VCS
support code. This lets BEurtle drop its VCS support code entirely which is great.

Note that I haven't had any success with getting BE to run under IronPython. It also
crashes out an IronPython compile. Furthermore I haven't got PyInstaller to work, nor
py2exe. You can see their scripts in the notworking directory. Even if you look into
!Generate_exe_bbfreeze.py you'll see extensive hacking of the output because BE is
written in a particular *dynamic* way which prevents correct static analysis, so all
the standard ways of bundling it up fail to include most of BE and its dependencies.

Niall Douglas
February 2012
 