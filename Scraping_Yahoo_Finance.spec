# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['D:\\Hekal\\Personal\\Freelancing\\Scraping_Finance.Yahoo.com\\Scraping_Yahoo_Finance.py'],
             pathex=['D:\\Hekal\\Personal\\Freelancing\\Scraping_Finance.Yahoo.com'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Scraping_Yahoo_Finance',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
