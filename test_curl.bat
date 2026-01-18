@echo off
chcp 65001
echo ================================================================================
echo 医疗病案质控系统API测试 (使用curl)
echo ================================================================================
echo.

echo 1. 测试获取规则列表
curl -X GET "http://localhost:4101/api/qc/rules"
echo.
echo.

echo 2. 测试单个病案质控 (A48=19079841, A49=1)
curl -X POST "http://localhost:4101/api/qc/check/single?a48=19079841&a49=1"
echo.
echo.

echo 3. 测试获取单个病案结果
curl -X GET "http://localhost:4101/api/qc/result/case?a48=19079841&a49=1"
echo.
echo.

echo 4. 测试批量质控 - 2020年1月
curl -X POST "http://localhost:4101/api/qc/check/batch" -H "Content-Type: application/json" -d "{\"periodType\":\"month\",\"year\":2020,\"month\":1}"
echo.
echo.

echo 5. 测试获取批量汇总 - 2020年1月
curl -X POST "http://localhost:4101/api/qc/result/batch/summary" -H "Content-Type: application/json" -d "{\"periodType\":\"month\",\"year\":2020,\"month\":1}"
echo.
echo.

echo ================================================================================
echo 测试完成！
echo Swagger文档: http://localhost:4101/swagger-ui/index.html
echo ================================================================================
pause
