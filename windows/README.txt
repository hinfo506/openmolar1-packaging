Our aim here is to build a windows installer package "openmolar_X_X_X.msi" for openmolar.

To make a windows executable, get openmolar running on a windows machine. (32 or 64 bit is important)
Do this by running python setup.py install, then finding win_openmolar.pyw

Now install pyinstaller on that machine.
make_exe.bat can then be run, which uses pyinstaller to create a standalone file
named openmolar.exe complete with openmolar icon.
You should be able to double click on this file and get into the application.


Now install Wix.
Wix uses an xml file to determine which files are included in the installer, and
utilises a uuid for each component.

I have automated the generation of that file by analysing the setup.py script.

So, 1st step is to generate that wxs file run (on a windows machine!) ./makewxs.py > openmolar.wxs

Once we have a valid wxs file, this needs to be "linked" and "compiled" by the
wix toolset.
(note - the compiler has to include the WixUIExtension)

linking.
    ~$ candle.exe openmolar.wxs
    this will produce a further file named openmolar.wixobj
compiling.
    ~$ light.exe -ext WixUIExtension openmolar.wixobj

If all has gone to plan one should have a openmolar.msi file, which you should
rename with the correct versioning (manually) to openmolar_X_X_X.msi


The msi file generated can be tested using
msiexec \i openmolar.exe  \l output.log           #for install/repair/remove



NOTES:
The files named *.wixobj, *.wixpdb and *.spec are generated automatically, and
can be largely ignored.
