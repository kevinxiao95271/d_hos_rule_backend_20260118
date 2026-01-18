#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko
import time
import sys

# 远程服务器配置
REMOTE_HOST = "81.71.44.180"
REMOTE_USER = "root"
REMOTE_PASSWORD = "Yiguo9527_"

def execute_remote_command(ssh, command, timeout=30):
    """执行远程命令并返回结果"""
    try:
        stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
        
        # 等待命令执行完成
        exit_status = stdout.channel.recv_exit_status()
        
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        
        return exit_status, output, error
    
    except Exception as e:
        return -1, "", str(e)

def check_redis_status(ssh):
    """检查Redis服务状态"""
    print("=== 检查Redis服务状态 ===")
    
    # 1. 检查Redis是否已安装
    print("1. 检查Redis是否已安装...")
    exit_status, output, error = execute_remote_command(ssh, "which redis-server")
    
    if exit_status == 0:
        print(f"✅ Redis已安装: {output}")
        redis_installed = True
    else:
        print("❌ Redis未安装")
        redis_installed = False
    
    # 2. 检查Redis服务是否运行
    if redis_installed:
        print("2. 检查Redis服务状态...")
        exit_status, output, error = execute_remote_command(ssh, "systemctl status redis")
        
        if "active (running)" in output:
            print("✅ Redis服务正在运行")
            redis_running = True
        else:
            print("❌ Redis服务未运行")
            redis_running = False
    else:
        redis_running = False
    
    # 3. 测试Redis连接
    if redis_running:
        print("3. 测试Redis连接...")
        exit_status, output, error = execute_remote_command(ssh, "redis-cli ping")
        
        if "PONG" in output:
            print("✅ Redis连接正常")
            redis_accessible = True
        else:
            print(f"❌ Redis连接失败: {output} {error}")
            redis_accessible = False
    else:
        redis_accessible = False
    
    return redis_installed, redis_running, redis_accessible

def install_redis(ssh):
    """安装Redis"""
    print("\n=== 安装Redis ===")
    
    # 1. 更新包管理器
    print("1. 更新包管理器...")
    exit_status, output, error = execute_remote_command(ssh, "yum update -y", timeout=120)
    if exit_status != 0:
        print(f"⚠️  包管理器更新警告: {error}")
    
    # 2. 安装EPEL仓库（如果需要）
    print("2. 安装EPEL仓库...")
    exit_status, output, error = execute_remote_command(ssh, "yum install -y epel-release")
    if exit_status != 0:
        print(f"⚠️  EPEL安装警告: {error}")
    
    # 3. 安装Redis
    print("3. 安装Redis...")
    exit_status, output, error = execute_remote_command(ssh, "yum install -y redis", timeout=180)
    
    if exit_status == 0:
        print("✅ Redis安装成功")
        return True
    else:
        print(f"❌ Redis安装失败: {error}")
        
        # 尝试使用其他方法安装
        print("尝试使用源码编译安装...")
        commands = [
            "cd /tmp",
            "wget http://download.redis.io/redis-stable.tar.gz",
            "tar xzf redis-stable.tar.gz",
            "cd redis-stable",
            "make",
            "make install"
        ]
        
        for cmd in commands:
            print(f"执行: {cmd}")
            exit_status, output, error = execute_remote_command(ssh, cmd, timeout=300)
            if exit_status != 0:
                print(f"❌ 命令失败: {error}")
                return False
        
        print("✅ Redis源码安装完成")
        return True

def configure_redis(ssh):
    """配置Redis"""
    print("\n=== 配置Redis ===")
    
    # 1. 创建Redis配置文件
    print("1. 创建Redis配置文件...")
    
    redis_config = """# Redis配置文件
bind 127.0.0.1
port 6379
timeout 0
keepalive 300
daemonize yes
supervised no
pidfile /var/run/redis_6379.pid
loglevel notice
logfile /var/log/redis_6379.log
databases 16
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /var/lib/redis
maxmemory 256mb
maxmemory-policy allkeys-lru
"""
    
    # 写入配置文件
    exit_status, output, error = execute_remote_command(ssh, 
        f"echo '{redis_config}' > /etc/redis.conf")
    
    if exit_status == 0:
        print("✅ Redis配置文件创建成功")
    else:
        print(f"❌ 配置文件创建失败: {error}")
    
    # 2. 创建Redis数据目录
    print("2. 创建Redis数据目录...")
    execute_remote_command(ssh, "mkdir -p /var/lib/redis")
    execute_remote_command(ssh, "chown redis:redis /var/lib/redis")
    
    # 3. 创建systemd服务文件
    print("3. 创建systemd服务文件...")
    
    service_config = """[Unit]
Description=Advanced key-value store
After=network.target

[Service]
Type=forking
User=redis
Group=redis
ExecStart=/usr/local/bin/redis-server /etc/redis.conf
ExecStop=/usr/local/bin/redis-cli shutdown
Restart=always

[Install]
WantedBy=multi-user.target
"""
    
    exit_status, output, error = execute_remote_command(ssh, 
        f"echo '{service_config}' > /etc/systemd/system/redis.service")
    
    if exit_status == 0:
        print("✅ systemd服务文件创建成功")
    else:
        print(f"❌ 服务文件创建失败: {error}")
    
    # 4. 创建redis用户
    print("4. 创建redis用户...")
    execute_remote_command(ssh, "useradd -r -s /bin/false redis")
    
    # 5. 重新加载systemd
    execute_remote_command(ssh, "systemctl daemon-reload")

def start_redis(ssh):
    """启动Redis服务"""
    print("\n=== 启动Redis服务 ===")
    
    # 1. 启动Redis服务
    print("1. 启动Redis服务...")
    exit_status, output, error = execute_remote_command(ssh, "systemctl start redis")
    
    if exit_status == 0:
        print("✅ Redis服务启动成功")
    else:
        print(f"❌ Redis服务启动失败: {error}")
        
        # 尝试直接启动
        print("尝试直接启动Redis...")
        exit_status, output, error = execute_remote_command(ssh, 
            "nohup redis-server /etc/redis.conf > /dev/null 2>&1 &")
        
        if exit_status == 0:
            print("✅ Redis直接启动成功")
        else:
            print(f"❌ Redis直接启动失败: {error}")
            return False
    
    # 2. 设置开机自启
    print("2. 设置Redis开机自启...")
    execute_remote_command(ssh, "systemctl enable redis")
    
    # 3. 等待服务启动
    print("3. 等待服务启动...")
    time.sleep(3)
    
    # 4. 测试连接
    print("4. 测试Redis连接...")
    exit_status, output, error = execute_remote_command(ssh, "redis-cli ping")
    
    if "PONG" in output:
        print("✅ Redis连接测试成功")
        return True
    else:
        print(f"❌ Redis连接测试失败: {output} {error}")
        return False

def get_redis_info(ssh):
    """获取Redis信息"""
    print("\n=== Redis信息 ===")
    
    # Redis版本
    exit_status, output, error = execute_remote_command(ssh, "redis-cli info server | grep redis_version")
    if exit_status == 0:
        print(f"Redis版本: {output}")
    
    # 内存使用
    exit_status, output, error = execute_remote_command(ssh, "redis-cli info memory | grep used_memory_human")
    if exit_status == 0:
        print(f"内存使用: {output}")
    
    # 连接数
    exit_status, output, error = execute_remote_command(ssh, "redis-cli info clients | grep connected_clients")
    if exit_status == 0:
        print(f"连接数: {output}")

def main():
    """主函数"""
    print("=== 远程Redis安装和配置脚本 ===")
    print(f"目标服务器: {REMOTE_HOST}")
    print()
    
    # 建立SSH连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print("连接到远程服务器...")
        ssh.connect(REMOTE_HOST, username=REMOTE_USER, password=REMOTE_PASSWORD, timeout=10)
        print("✅ SSH连接成功")
        
        # 检查Redis状态
        redis_installed, redis_running, redis_accessible = check_redis_status(ssh)
        
        # 根据状态决定操作
        if redis_accessible:
            print("\n✅ Redis已正常运行，无需安装")
        elif redis_installed and not redis_running:
            print("\n⚡ Redis已安装但未运行，尝试启动...")
            if start_redis(ssh):
                print("✅ Redis启动成功")
            else:
                print("❌ Redis启动失败")
                return False
        else:
            print("\n🔧 需要安装Redis...")
            if install_redis(ssh):
                configure_redis(ssh)
                if start_redis(ssh):
                    print("✅ Redis安装和配置完成")
                else:
                    print("❌ Redis启动失败")
                    return False
            else:
                print("❌ Redis安装失败")
                return False
        
        # 获取Redis信息
        get_redis_info(ssh)
        
        print(f"\n✅ Redis设置完成！")
        print(f"Redis地址: {REMOTE_HOST}:6379")
        print("下一步: 更新应用配置使用远程Redis")
        
        return True
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False
    
    finally:
        ssh.close()

if __name__ == "__main__":
    if main():
        print("\n🎉 Redis设置成功！")
    else:
        print("\n💥 Redis设置失败！")
        sys.exit(1)