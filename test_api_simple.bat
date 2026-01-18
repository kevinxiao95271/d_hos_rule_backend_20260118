@echo off
echo Testing API connection...
curl -X GET http://localhost:4101/api/qc/status
echo.
echo.
echo Testing single case QC...
curl -X POST http://localhost:4101/api/qc/check/single -H "Content-Type: application/json" -d "{\"mrKey\":\"test_key\"}"
echo.
pause