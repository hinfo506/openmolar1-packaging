#! /usr/bin/python

import os
import re
import sys
import platform
import uuid
from xml.dom import minidom

# necessary so that setup finds the resources
# before we import setup, we need to find the src directory


def source_folders():
    for dir_ in sorted([p for p in os.listdir()
                 if re.match("openmolar-\d\.\d\.\d", p)]):
        if os.path.isdir(dir_):
            yield os.path.abspath(dir_)


path = os.path.abspath(os.path.dirname(__file__))
EXE_PATH = os.path.join(path, "dist", "openmolar.exe")
if not os.path.isfile(EXE_PATH):
    sys.exit("Cannot find %s!\nQUITTING" % EXE_PATH)

# this script should be run on windows, but I test on debian.
if platform.system() == "Windows":
    OUTFILE = os.path.join(path, "openmolar.wxs")
    os.chdir(path)
    os.chdir("../")
    SRCDIR = list(source_folders())[-1]
else:
    print("WARNING - THIS SCRIPT SHOULD BE RUN ON WINDOWS")
    SRCDIR = "/home/neil/openmolar/openmolar1"
    OUTFILE = os.path.join(path, "openmolar_debian.wxs")

os.chdir(SRCDIR)
sys.path.insert(0, SRCDIR)   # for correct path to setup.py
sys.path.insert(0, os.path.join(SRCDIR, "src")) # for corect path to version.py

import setup
from openmolar.settings.version import VERSION

'''
this module generates our wix file.
usage is make_wxs.py > openmolar.wxs
'''

print("running make_wxs\nutilising DATA_FILES from %s" % setup.__file__)

# NEVER CHANGE THIS!!!
UPGRADE_GUID = "3E52AFB20C5511E6B04339339F36C610"


m = re.match("(\d+).(\d+).(\d+)-", VERSION)
if not m:
    sys.exit("VERSION %s should be in the form x.x.x-foo\nQUITTING" % VERSION)

version_digits = m.groups()
VERSION = "%s.%s.%s.0" % version_digits

RESOURCES_PATH = os.path.abspath(os.path.join(SRCDIR, "src", "openmolar",
                                              "resources"))

ICON_PATH = os.path.join(RESOURCES_PATH, "icons", "openmolar.ico")
DIALOG_BITMAP_PATH = os.path.join(RESOURCES_PATH, 'win_install_dialog.bmp')
BANNER_BITMAP_PATH = os.path.join(RESOURCES_PATH, 'win_install_banner.bmp')

LICENSE_PATH = os.path.abspath(os.path.join(path, "license.rtf"))

EXIT_MESSAGE = '''Thank you for installing OpenMolar.

Please join the openmolar community and contribute
to the documentation, the source code or
internationalisation.

Find out more at http://openmolar.com'''


def _template():

    '''
    This is a function so that vim folds the nasty big string!
    '''

    template = r'''
    <Product Id="*" UpgradeCode="{{ UPGRADE_GUID }}"
    Name="OpenMolar" Version="{{ VERSION }}"
    Manufacturer="OpenMolar" Language="1033">
        <Package InstallerVersion="200" Compressed="yes" Comments="Windows Installer Package for OpenMolar"/>
        <Media Id="1" Cabinet="openmolar.cab" EmbedCab="yes"/>

        <WixVariable Id="WixUILicenseRtf" Value="{{ LICENSE_RTF }}" />

        <!-- Define icons (ID should not be longer than 18 chars and must end with ".exe") -->
        <Icon Id="Icon.exe" SourceFile="{{ ICON }}"/>

        <!-- Set properties for add/remove programs -->
        <Property Id="ARPPRODUCTICON" Value="Icon.exe"/>
        <Property Id="ARPHELPLINK" Value="http://openmolar.com"/>
        <Property Id="ARPURLINFOABOUT" Value="http://openmolar.com"/>
        <Property Id="ARPNOREPAIR" Value="1"/>
        <Upgrade Id="{{ UPGRADE_GUID }}">
            <UpgradeVersion Minimum="{{ VERSION }}" OnlyDetect="yes" Property="NEWERVERSIONDETECTED"/>
            <UpgradeVersion Minimum="0.0.0" Maximum="{{ VERSION }}"
            IncludeMinimum="yes" IncludeMaximum="no" Property="OLDERVERSIONBEINGUPGRADED"/>
        </Upgrade>
        <Condition Message="A newer version of this software is already installed.">
            NOT NEWERVERSIONDETECTED
        </Condition>
        <Directory Id="TARGETDIR" Name="SourceDir">
            <Directory Id="ProgramFilesFolder">

                <Directory Id="INSTALLDIR" Name="OpenMolar">
                    <Component Id="MainExecutable" Guid="63C30814-E8BF-4C22-B551-63ADAD252774">
                        <File Id="OpenMolar.exe" Source="{{ EXE_PATH }}" KeyPath="yes" Checksum="yes">
                        </File>
                    </Component>

                    <Directory Id="LocaleDIR" Name="locale">
                    {{ LOCALE_FILES }}
                    </Directory>

                    <Directory Id="ResourcesDIR" Name="resources">
                    {{ RESOURCE_FILES }}
                    </Directory>

                </Directory>
            </Directory>

            <Directory Id="ProgramMenuFolder">
                <Directory Id="ProgramMenuSubfolder" Name="OpenMolar">
                    <Component Id="ApplicationShortcuts" Guid="34486FA2-FF2D-433F-B0E9-5DEA3BE1732F">
                        <Shortcut Id="ApplicationShortcut1" Name="Openmolar" Description="Dental Practice Management Suite"
                                    Target="[INSTALLDIR]openmolar.exe" WorkingDirectory="INSTALLDIR"/>
                        <RegistryValue Root="HKCU" Key="Software\OpenMolar\OpanMolar"
                                    Name="installed" Type="integer" Value="1" KeyPath="yes"/>
                        <RemoveFolder Id="ProgramMenuSubfolder" On="uninstall"/>
                    </Component>
                </Directory>
            </Directory>
        </Directory>

      <InstallExecuteSequence>
         <RemoveExistingProducts After="InstallValidate"/>
      </InstallExecuteSequence>

        <Feature Id="DefaultFeature" Level="1">
            <ComponentRef Id="MainExecutable"/>
            <ComponentRef Id="ApplicationShortcuts"/>
            {{ COMPONENT_REFS }}
        </Feature>

        <!-- Define the UI to use - NOTE this requires extra arguments when
        usng light.exe -->

        <WixVariable Id="WixUIDialogBmp" Value="{{ DIALOG_BITMAP_PATH }}" />
        <WixVariable Id="WixUIBannerBmp" Value="{{ BANNER_BITMAP_PATH }}" />
        <UIRef Id="WixUI_Minimal" />
        <UIRef Id="WixUI_ErrorProgressText" />

        <Property Id="WIXUI_EXITDIALOGOPTIONALTEXT"
        Value="{{ EXIT_MESSAGE }}"
        />

        </Product>'''

    return ('<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">\n'
            '%s\n</Wix>\n' % template)


def locale_files():
    '''
    iterate over the files usually installed by setup.py and add to the file
    '''
    folder_no, file_no = 0, 0
    data =''
    component_refs = ""
    for folder, files in setup.DATA_FILES:
        if "locale" not in folder:
            continue
        folder_no += 1
        dirname = os.path.split(folder)[1]
        if dirname != "locale":  # files are not in a subfolder
            data += '<Directory Id="locale_subdir%s" Name="%s">\n' % (
                folder_no, dirname)
        for file_ in files:
            file_no += 1
            guid = uuid.uuid1().hex.upper()
            ref = "locale_component%d" % file_no
            data += ('<Component Id="%s" Guid="%s">\n'
                     '<File Id="locale_file%d" Source="%s" '
                     'KeyPath="yes" Checksum="yes" />\n'
                     '</Component>\n' % (ref, guid, file_no, file_))
            component_refs += '<ComponentRef Id="%s" />\n' % ref
        if dirname != "locale":  # files are not in a subfolder
            data += "</Directory>\n\n"

    return data, component_refs


def resource_files():
    '''
    iterate over the files usually installed by setup.py and add to the file
    '''
    folder_no, file_no = 0, 0
    data =''
    component_refs = ""
    for folder, files in setup.DATA_FILES:
        if "resources" not in folder:
            continue
        folder_no += 1
        dirname = os.path.split(folder)[1]
        if dirname != "resources":  # files are not in a subfolder
            data += ('<Directory Id="resource_folder%s" Name="%s">\n' % (
                folder_no, dirname))
        for file_ in files:
            file_no += 1
            guid = uuid.uuid1().hex.upper()
            ref = "resource_component%d" % file_no
            data += ('<Component Id="%s" Guid="%s">\n'
                     '<File Id="resource_file%d" Source="%s" '
                     'KeyPath="yes" Checksum="yes" />\n'
                     '</Component>\n' % (ref, guid, file_no, file_))
            component_refs += '<ComponentRef Id="%s" />\n' % ref
        if dirname != "resources":  # files are not in a subfolder
            data += "</Directory>\n\n"

    return data, component_refs


def main():
    t = _template().replace("{{ VERSION }}", VERSION)
    t = t.replace("{{ LICENSE_RTF }}", LICENSE_PATH)
    t = t.replace("{{ ICON }}", ICON_PATH)
    t = t.replace("{{ DIALOG_BITMAP_PATH }}", DIALOG_BITMAP_PATH)
    t = t.replace("{{ BANNER_BITMAP_PATH }}", BANNER_BITMAP_PATH)
    t = t.replace("{{ EXE_PATH }}", EXE_PATH)
    t = t.replace("{{ EXIT_MESSAGE }}", EXIT_MESSAGE)
    t = t.replace("{{ UPGRADE_GUID }}", UPGRADE_GUID)
    locale_components, locale_refs = locale_files()
    t = t.replace("{{ LOCALE_FILES }}", locale_components)
    resource_components, resource_refs = resource_files()
    t = t.replace("{{ RESOURCE_FILES }}", resource_components)
    t = t.replace("{{ COMPONENT_REFS }}", locale_refs + resource_refs)
    return t


def prettify(xml):
    '''
    default minidom.toprettyxml produces way too many blank lines.
    '''
    d = minidom.parseString(xml)
    prettyxml = d.toprettyxml(indent=' '*2, encoding="UTF-8").decode("UTF-8")
    xml_lines = prettyxml.split('\n')
    return '\n'.join([line for line in xml_lines if line.strip()])


if __name__ == "__main__":
    xml_ = main()
    f = open(OUTFILE, "w")
    f.write(prettify(xml_))
    f.close()
