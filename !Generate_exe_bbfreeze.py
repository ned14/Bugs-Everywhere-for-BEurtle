import os, bbfreeze, zipfile, compileall
compileall.compile_dir("libbe")
f=bbfreeze.Freezer()
f.addScript("be.py")
f.addModule("htmlentitydefs")
f.addModule("jinja2")
print "Assembling ..."
f()

# Hack in the missing files from libbe
with zipfile.ZipFile("dist/library.zip", "a") as zf:
    existing=[f for f in zf.namelist() if f[:6]=='libbe/']
    #print existing
    for dirpath, dirnames, filenames in os.walk("libbe"):
        for filename in filenames:
            if filename[-4:]==".pyc":
                path=os.path.join(dirpath, filename).replace(os.sep, '/')
                if path not in existing:
                    print "Adding file", path, "..."
                    zf.write(path)
