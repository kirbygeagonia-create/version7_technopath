@echo off
cd /d "c:\Users\User\Downloads\version8_technopath\version4_technopath\backend_django"
echo Running migrations...
python manage.py migrate
echo.
echo Starting Django server...
start python manage.py runserver 8000
echo.
echo Django should be running on http://localhost:8000
pause
