@ECHO off

REM Activate the virtual environment
call "C:\Users\pc\Desktop\Installment\virtual\Scripts\activate.bat"

REM Start Django server in minimized window
start /min cmd /c "python manage.py runserver"


REM Start Electron app
start /min cmd /c "npm run Installment"

EXIT
