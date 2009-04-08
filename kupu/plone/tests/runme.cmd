@echo off
setlocal
set PLONEHOME=%1"
set PLONEHOME=%PLONEHOME:"=%
if "%PLONEHOME%"=="" set PLONEHOME=c:\Plone20
set PYTHONPATH=%PLONEHOME%\Zope\lib\python
set PRODUCTS_PATH=;%~D0%~P0..\..\..;%PLONEHOME%\Zope\lib\python\Products;%PLONEHOME%\Data\Products
set INSTANCE_HOME=%PLONEHOME%\Data
set SOFTWARE_HOME=%PLONEHOME%\Zope\lib\python
@set PYTHON=C:\Plone20\Zope\bin\python.exe
rem "%PYTHON%" %~D0%~P0test_browserSupportsKupu.py %2
rem "%PYTHON%" %~D0%~P0test_librarymanager.py
rem "%PYTHON%" %~D0%~P0test_links.py
rem "%PYTHON%" %~D0%~P0test_html2captioned.py
rem "%PYTHON%" %~D0%~P0test_resourcetypemapper.py
rem "%PYTHON%" %~D0%~P0test_urls.py
"%PYTHON%" "%~D0%~P0runalltests.py" %2
endlocal
