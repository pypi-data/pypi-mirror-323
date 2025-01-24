# Python第三方包二次封装

应该会用到一些其他依赖

## 注意

由于oracledb的原因，python版本需要大于3.7
由于部分语法使用最新Python语法，python版本需要大于3.10
打包本身还是得使用3.9

## 封装依赖

```shell
pip install build
pip install openpyxl
pip install twine
pip install pymysql
pip install oracledb
pip install scapy
pip install psutil
pip install loguru
pip install dataclasses-json
```

## 安装

```shell
pip install pylwr
```

打包与上传

```shell
Remove-Item -Path "dist" -Recurse -Force ; python -m build
Remove-Item -Path "build" -Recurse -Force ; python setup.py sdist bdist_wheel
python -m twine upload dist\*
```
