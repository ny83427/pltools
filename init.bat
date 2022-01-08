@echo off
:: https://chocolatey.org/install
:: Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
:: cinst python -y
:: 使用Chocolatey安装PYTHON运行环境先
mkdir C:\Tmp\pltools
pip install selenium chromedriver-autoinstaller
