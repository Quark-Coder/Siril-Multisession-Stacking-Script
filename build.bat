@echo off
rmdir /s /q build
rmdir /s /q dist
pyinstaller -F --name="AutoStackScript_1.0.1"--icon=D:\Coding\Python\AnotherpySirilScript\icon.ico --strip --upx-dir=D:\Programs\upx --optimize=2 ^
--exclude-module=ipython ^
--exclude-module=backcall ^
--exclude-module=decorator ^
--exclude-module=jedi ^
--exclude-module=parso ^
--exclude-module=matplotlib-inline ^
--exclude-module=pickleshare ^
--exclude-module=prompt_toolkit ^
--exclude-module=wcwidth ^
--exclude-module=Pygments ^
--exclude-module=stack-data ^
--exclude-module=asttokens ^
--exclude-module=six ^
--exclude-module=executing ^
--exclude-module=pure-eval ^
--exclude-module=traitlets ^
--exclude-module=nbconvert ^
--exclude-module=beautifulsoup4 ^
--exclude-module=soupsieve ^
--exclude-module=bleach ^
--exclude-module=webencodings ^
--exclude-module=defusedxml ^
--exclude-module=Jinja2 ^
--exclude-module=MarkupSafe ^
--exclude-module=mistune ^
--exclude-module=nbclient ^
--exclude-module=jupyter_client ^
--exclude-module=python-dateutil ^
--exclude-module=pyzmq ^
--exclude-module=tornado ^
--exclude-module=fastjsonschema ^
--exclude-module=jsonschema ^
--exclude-module=attrs ^
--exclude-module=jsonschema-specifications ^
--exclude-module=referencing ^
--exclude-module=rpds-py ^
--exclude-module=pandocfilters ^
--exclude-module=tinycss2 ^
script.py
pause