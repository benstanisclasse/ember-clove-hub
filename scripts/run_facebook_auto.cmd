@echo off
rem Facebook Page photo posts: plans and schedules the next week through PostZen when it's due.
rem Does nothing unless data\facebook\rules.json has auto_publish true (the owner turns it on).
cd /d "%~dp0.."
if not defined POSTZEN_API_KEY (
  for /f "delims=" %%k in ('python -I -c "import re,os;print(re.search(r'pzn_[A-Za-z0-9_\-]+', open(os.path.join(os.environ['USERPROFILE'],'Downloads','key.txt')).read()).group(0))"') do set "POSTZEN_API_KEY=%%k"
)
python -I scripts\facebook_photos.py auto >> data\facebook\auto.log 2>&1
