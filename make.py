import sys
import os
import shutil
import glob

if len(sys.argv)<2: 
    print("No project name given.")
    print("Call this scrip like this: python make.py <projectname>")
    input("Press Enter to continue...")
    sys.exit(0)
if os.path.exists(sys.argv[1]): shutil.rmtree(sys.argv[1])
shutil.copytree("template", sys.argv[1])

for filename in glob.iglob(sys.argv[1]+'/**/*.*', recursive=True):
    try: IN = open(filename,"r").read()
    except UnicodeDecodeError: continue
    if "DEADBEEF" in filename:
        os.remove(filename)
        filename = filename.replace("DEADBEEF", sys.argv[1])
    OUT = IN.replace("DEADBEEF", sys.argv[1])
    open(filename,"w").write(OUT)
