# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['clasper.py'],
             pathex=['C:\\Users\\chinm\\Documents\\GitHub\\py_knots\\py_knots'],
             binaries=[],
             datas=[],
             hiddenimports=['sgraph', 'braid', 'col_perm',
             'visualization', 'casson_gordon', 'pres_mat'],
             hookspath=[],
             hooksconfig={},
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
          [],
          exclude_binaries=True,
          name='clasper',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='clasper')
