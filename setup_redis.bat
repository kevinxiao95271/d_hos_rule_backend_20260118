@echo off
echo ===== Redis 安装和启动脚本 =====

echo.
echo 1. 检查Redis是否已安装...
where redis-server >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Redis已安装
    goto :start_redis
) else (
    echo ❌ Redis未安装
    goto :install_redis
)

:install_redis
echo.
echo 2. 安装Redis...
echo 请选择安装方式:
echo [1] 使用Chocolatey安装 (推荐)
echo [2] 手动下载安装
echo [3] 跳过安装
set /p choice="请输入选择 (1-3): "

if "%choice%"=="1" goto :choco_install
if "%choice%"=="2" goto :manual_install
if "%choice%"=="3" goto :skip_install
goto :install_redis

:choco_install
echo.
echo 使用Chocolatey安装Redis...
where choco >nul 2>&1
if %errorlevel% == 0 (
    choco install redis-64 -y
    if %errorlevel% == 0 (
        echo ✅ Redis安装成功
        goto :start_redis
    ) else (
        echo ❌ Redis安装失败
        goto :manual_install
    )
) else (
    echo ❌ Chocolatey未安装，请先安装Chocolatey或选择手动安装
    goto :manual_install
)

:manual_install
echo.
echo 手动安装Redis:
echo 1. 访问 https://github.com/microsoftarchive/redis/releases
echo 2. 下载 Redis-x64-3.0.504.msi
echo 3. 运行安装程序
echo 4. 安装完成后重新运行此脚本
echo.
pause
goto :end

:skip_install
echo 跳过Redis安装，假设Redis已通过其他方式安装
goto :start_redis

:start_redis
echo.
echo 3. 启动Redis服务...

:: 检查Redis服务是否已运行
tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ Redis服务已在运行
    goto :test_redis
)

:: 尝试启动Redis服务
echo 启动Redis服务...
start "Redis Server" redis-server

:: 等待服务启动
timeout /t 3 /nobreak >nul

:: 再次检查服务状态
tasklist /FI "IMAGENAME eq redis-server.exe" 2>NUL | find /I /N "redis-server.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ Redis服务启动成功
) else (
    echo ❌ Redis服务启动失败
    echo 请手动启动Redis: redis-server
    pause
    goto :end
)

:test_redis
echo.
echo 4. 测试Redis连接...
redis-cli ping
if %errorlevel% == 0 (
    echo ✅ Redis连接测试成功
) else (
    echo ❌ Redis连接测试失败
    echo 请检查Redis服务状态
)

echo.
echo 5. Redis信息:
redis-cli info server | findstr "redis_version"
redis-cli info memory | findstr "used_memory_human"

echo.
echo ===== Redis设置完成 =====
echo.
echo 下一步:
echo 1. 重新编译应用: mvn clean package -DskipTests
echo 2. 启动应用: java -jar target\qc-system-1.0.0.jar
echo 3. 运行性能测试: python test_redis_performance.py
echo.

:end
pause