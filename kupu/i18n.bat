@echo off
if cmdextversion 2 goto :cmdok
echo Sorry, this batch file requires a more recent version of Windows.
goto :eof

:cmdok
setlocal
setlocal enabledelayedexpansion
cd %~P0

set I18NDUDE=c:\python25\python.exe c:\python25\scripts\i18ndude-script.py
if "%1"=="" goto :help
goto :%1
:help
echo This script does some common i18n tasks:
echo    %0 check
echo          --- checks i18n attributes on all files
echo    %0 kupu
echo          --- checks i18n attributes for domain "kupu" only  
echo    %0 kupuconfig
echo          --- checks i18n attributes for domain "kupuconfig" only  
echo    %0 kupu.pot
echo          --- creates a new kupu.pot file
echo    %0 kupuconfig.pot
echo          --- creates a new kupuconfig.pot file
echo    %0 kupusync
echo          --- synchronises kupu.pot with all kupu-XX.po files
echo    %0 kupuconfigsync
echo          --- synchronises kupuconfig.pot with all kupuconfig-XX.po files
goto :eof
:check
REM %I18NDUDE% find-untranslated common\drawers\* default\* plone\*
goto :eof
:kupupox
for %%f in (common\kupu.pox) do %I18NDUDE% find-untranslated %%f
goto :eof
:kupu
call :setKUPU
for %%f in (%KUPU%) do %I18NDUDE% find-untranslated %%f
goto :eof
:kupuconfig
call :setKUPUCONFIG
for %%f in (%KUPUCONFIG%) do %I18NDUDE% find-untranslated %%f
goto :eof

:kupuconfig.pot
call :setKUPUCONFIG
%I18NDUDE% rebuild-pot --pot i18n\kupuconfig.pot --create kupuconfig %KUPUCONFIG%
goto :eof

:kupuconfigsync
set KCPO=
for %%f in (i18n\kupuconfig-*.po) do set KCPO=!KCPO! %%f
%I18NDUDE% sync --pot i18n\kupuconfig.pot %KCPO%
goto :eof

:kupupox.pot
%I18NDUDE% rebuild-pot --pot i18n\kupupox.pot --create kupupox common\kupu.pox
goto :eof

:kupupoxsync
set KXPO=
for %%f in (i18n\kupupox-*.po) do set KXPO=!KXPO! %%f
%I18NDUDE% sync --pot i18n\kupupox.pot %KXPO%
goto :eof

:kupu.pot
call :setKUPU
%I18NDUDE% rebuild-pot --pot i18n\kupu.pot --create kupu %KUPU%
goto :eof

:kupusync
set KPO=
for %%f in (i18n\kupu-*.po) do set KCPO=!KCPO! %%f
%I18NDUDE% sync --pot i18n\kupu.pot %KCPO%
goto :eof

:setKUPUCONFIG
set KUPUCONFIG=
for %%f in (default\*) do (find /C "i18n:domain=""kupuconfig""" %%f && set KUPUCONFIG=!KUPUCONFIG! %%f) >nul
for %%f in (plone\*) do (find /C "i18n:domain=""kupuconfig""" %%f && set KUPUCONFIG=!KUPUCONFIG! %%f) >nul
for %%f in (plone\kupu_plone_layer\*) do (find /C "i18n:domain=""kupuconfig""" %%f && set KUPUCONFIG=!KUPUCONFIG! %%f) >nul
for %%f in (common\kupudrawers\*) do (find /C "i18n:domain=""kupuconfig""" %%f && set KUPUCONFIG=!KUPUCONFIG! %%f) >nul
goto :eof
:setKUPU
set KUPU=
for %%f in (default\*) do (find /C "i18n:domain=""kupu""" %%f && set KUPU=!KUPU! %%f) >nul
for %%f in (plone\*) do (find /C "i18n:domain=""kupu""" %%f && set KUPU=!KUPU! %%f) >nul
for %%f in (plone\kupu_plone_layer\*) do (find /C "i18n:domain=""kupu""" %%f && set KUPU=!KUPU! %%f) >nul
for %%f in (common\kupudrawers\*) do (find /C "i18n:domain=""kupu""" %%f && set KUPU=!KUPU! %%f) >nul
goto :eof
