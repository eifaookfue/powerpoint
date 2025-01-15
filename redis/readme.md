Readme

## Windowsでpipenvインストール

### まずpythonの最新版をインストール

### pythonがどこにインストールされているか？
```
py --list-paths
```

### pipenvインストール
```
C:\Users\user\AppData\Local\Programs\Python\Python313\python -m pip install pipenv --user

Installing collected packages: distlib, setuptools, platformdirs, packaging, filelock, certifi, virtualenv, pipenv
  WARNING: The script virtualenv.exe is installed in 'C:\Users\user\AppData\Roaming\Python\Python313\Scripts' which is not on PATH.
  Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.
  WARNING: The scripts pipenv-resolver.exe and pipenv.exe are installed in 'C:\Users\user\AppData\Roaming\Python\Python313\Scripts' which is not on PATH.
  Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.
Successfully installed certifi-2024.12.14 distlib-0.3.9 filelock-3.16.1 packaging-24.2 pipenv-2024.4.0 platformdirs-4.3.6 setuptools-75.6.0 virtualenv-20.28.0
```

### python3.10のインストール

### pipenvを使ってモジュールをインストール
```
C:\Users\user\AppData\Roaming\Python\Python313\Scripts\pipenv.exe install --python C:\Users\user\AppData\Local\Programs\Python\Python310\python.exe
```

### VSCodeでselect interapterで作成した仮想環境を利用
