# Start TechnoPath System
# This script starts both backend and frontend

Write-Host "Starting TechnoPath System..." -ForegroundColor Green

# Start Django Backend
Write-Host "Starting Django backend on http://127.0.0.1:8000 ..." -ForegroundColor Cyan
$backend = Start-Process -FilePath "python" -ArgumentList "manage.py", "runserver", "127.0.0.1:8000" -WorkingDirectory "c:\Users\User\Downloads\version8_technopath\version4_technopath\backend_django" -PassThru -WindowStyle Minimized

# Wait a moment for backend to initialize
Start-Sleep -Seconds 3

# Start Vue Frontend
Write-Host "Starting Vue frontend on http://localhost:5187 ..." -ForegroundColor Cyan
$frontend = Start-Process -FilePath "npm" -ArgumentList "run", "dev", "--", "--port", "5187" -WorkingDirectory "c:\Users\User\Downloads\version8_technopath\version4_technopath\frontend" -PassThru -WindowStyle Minimized

Write-Host "`nSystem started!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5187/" -ForegroundColor Yellow
Write-Host "Backend:  http://127.0.0.1:8000/" -ForegroundColor Yellow
Write-Host "`nPress Ctrl+C to stop both servers..." -ForegroundColor Gray

# Keep script running
while ($true) {
    Start-Sleep -Seconds 1
}
