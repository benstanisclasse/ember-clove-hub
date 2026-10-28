@echo off
rem Ember Studio dashboard for the local network: http://<this machine>:8790
rem Loads the PostZen key into this window only (from Downloads\key.txt unless POSTZEN_API_KEY is already set).
cd /d "%~dp0..\.."
if not defined POSTZEN_API_KEY (
  for /f "delims=" %%k in ('python -I -c "import re,os;print(re.search(r'pzn_[A-Za-z0-9_\-]+', open(os.path.join(os.environ['USERPROFILE'],'Downloads','key.txt')).read()).group(0))"') do set "POSTZEN_API_KEY=%%k"
)
python scripts\studio\dashboard_server.py --port 8790 --every-min 15
