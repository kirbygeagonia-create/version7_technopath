# Restart chatbot server script
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 1
cd "$PSScriptRoot"
python app.py
