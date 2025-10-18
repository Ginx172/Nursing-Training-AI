Write-Host "Starting Nursing Training AI..." -ForegroundColor Green
Set-Location "J:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\backend"
python -m uvicorn main_working:app --host 0.0.0.0 --port 8002 --reload
