@echo off
echo 医疗质控系统性能测试
echo ========================

echo 1. 测试优化批量处理...
python test_optimized_batch_performance.py

echo.
echo 2. 如果需要单独测试，可以使用以下命令：
echo    python -c "import requests; print(requests.post('http://localhost:4101/api/qc/check/batch/optimized', json={'periodType':'year','year':2023}).json())"

echo.
echo 测试完成！
pause
