@echo off
echo 医疗质控系统优化版本部署脚本
echo ================================

echo 1. 停止当前服务...
for /f "tokens=1" %%i in ('jps -l ^| findstr "medical-qc"') do (
    echo 停止进程 %%i
    taskkill /PID %%i /F
)

echo 2. 清理和编译...
mvn clean compile
if %errorlevel% neq 0 (
    echo 编译失败！
    pause
    exit /b 1
)

echo 3. 打包...
mvn package -DskipTests
if %errorlevel% neq 0 (
    echo 打包失败！
    pause
    exit /b 1
)

echo 4. 启动服务...
start "Medical QC Service" java -jar target/medical-qc-*.jar

echo 5. 等待服务启动...
timeout /t 10

echo 6. 验证服务状态...
curl http://localhost:4101/api/qc/status

echo 部署完成！
echo 现在可以使用优化接口: POST /api/qc/check/batch/optimized
pause
