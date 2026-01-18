@echo off
echo ========================================
echo 重启Spring Boot应用
echo ========================================

echo.
echo 1. 停止现有应用...
taskkill /f /im java.exe 2>nul
timeout /t 3 >nul

echo.
echo 2. 启动应用...
cd /d "%~dp0"
if exist "target\medical-qc-0.0.1-SNAPSHOT.jar" (
    echo 使用Maven构建的JAR文件...
    start "Medical QC Service" java -jar target\medical-qc-0.0.1-SNAPSHOT.jar
) else (
    echo 使用Maven直接运行...
    start "Medical QC Service" mvn spring-boot:run
)

echo.
echo 3. 等待应用启动...
timeout /t 10 >nul

echo.
echo 4. 检查应用状态...
curl -s http://localhost:4101/api/health >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ 应用启动成功
) else (
    echo ⚠️  应用可能还在启动中，请稍等...
)

echo.
echo ========================================
echo 重启完成
echo ========================================
echo.
echo 下一步操作:
echo 1. 等待应用完全启动 (约30秒)
echo 2. 运行: python test_ethnicity_fix.py
echo 3. 验证民族字段显示正确
echo.
pause