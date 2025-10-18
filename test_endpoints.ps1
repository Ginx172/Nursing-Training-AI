# Test endpoints script
Write-Host "Testing Nursing Training AI endpoints..." -ForegroundColor Green

# Test root endpoint
Write-Host "Testing root endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8002/" -Method GET
    Write-Host "✅ Root endpoint: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Root endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test auto summary
Write-Host "Testing auto summary..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8002/api/auto/summary" -Method GET
    Write-Host "✅ Auto summary: $($response.capabilities.question_banks) question banks" -ForegroundColor Green
} catch {
    Write-Host "❌ Auto summary failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test banks catalog
Write-Host "Testing banks catalog..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8002/api/banks/catalog?page=1&page_size=1" -Method GET
    Write-Host "✅ Banks catalog: $($response.total) total banks" -ForegroundColor Green
} catch {
    Write-Host "❌ Banks catalog failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test TTS endpoint
Write-Host "Testing TTS endpoint..." -ForegroundColor Yellow
try {
    $body = @{text="Test question"} | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "http://localhost:8002/api/audio/tts" -Method POST -ContentType "application/json" -Body $body
    Write-Host "✅ TTS endpoint: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ TTS endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Testing complete!" -ForegroundColor Green
