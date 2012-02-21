# -*- mode: python -*-
import os
files=["be.py"]
a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py')]+files,
             pathex=['G:\\BEurtle\\BE'])
# BE doesn't specify itself internally properly, so PyInstaller gets confused ...
for dirpath, dirnames, filenames in os.walk("libbe"):
    for filename in filenames:
        if filename[-3:]==".py":
			libbeitem=dirpath[dirpath.find('libbe'):].replace(os.path.sep, '.')+"."+filename[:-3]
			found=False
			for item in a.pure:
			    if item[0]==libbeitem:
					found=True
					break
			if not found:
				print "Missing", libbeitem, "..."
				item=(libbeitem, os.path.join(dirpath, filename)+'c', "PYMODULE")
				a.pure.append(item)
pyz = PYZ(a.pure)
if 0: # not single file
    exe = EXE(pyz,
          a.scripts+ [('v', '', 'OPTION')],
          exclude_binaries=1,
          name=os.path.join('build\\pyi.win32\\be', 'be.exe'),
          debug=True,
          strip=False,
          upx=True,
          console=True )
    coll = COLLECT( exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name=os.path.join('dist', 'be'))
else:
    exe = EXE( pyz,
          a.scripts+ [('v', '', 'OPTION')],
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'be.exe'),
          debug=True,
          strip=False,
          upx=True,
          console=True )
