# -*- mode: python -*-

block_cipher = None


a = Analysis(['C:\\Python34\\Scripts\\win_openmolar.pyw'],
             pathex=['E:\\windows'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='openmolar',
          debug=False,
          strip=False,
          upx=True,
          console=True , icon='C:\\Program Files\\openmolar\\resources\\icons\\openmolar.ico')
