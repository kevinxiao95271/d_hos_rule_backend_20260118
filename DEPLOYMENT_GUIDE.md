# 医疗病案质控系统 - 部署和使用指南

## 目录
1. [系统要求](#系统要求)
2. [快速部署](#快速部署)
3. [详细配置](#详细配置)
4. [使用指南](#使用指南)
5. [常见问题](#常见问题)
6. [维护指南](#维护指南)

---

## 系统要求

### 硬件要求
- CPU: 2核心及以上
- 内存: 4GB及以上
- 磁盘: 10GB可用空间

### 软件要求
- 操作系统: Windows 10/Linux/MacOS
- JDK: 1.8或更高版本
- Maven: 3.6或更高版本
- MySQL: 8.0或更高版本
- Python: 3.7或更高版本 (可选，用于测试)

---

## 快速部署

### 步骤1: 准备环境

#### 1.1 安装JDK
```bash
# 验证JDK安装
java -version

# 应该看到类似输出:
# java version "1.8.0_191"
```

#### 1.2 安装Maven
```bash
# 验证Maven安装
mvn --version

# 应该看到类似输出:
# Apache Maven 3.9.11
```

#### 1.3 准备MySQL数据库
确保MySQL服务正在运行，并且可以连接到数据库。

### 步骤2: 初始化数据库

#### 2.1 创建表结构
```bash
python create_tables.py
```

**预期输出**:
```
✓ 执行成功
✓ 执行成功
...
创建的表:
  - kiro_field_mapping
  - kiro_qc_batch_summary
  - kiro_qc_case_result
  - kiro_qc_defect_detail
  - kiro_qc_rule
  - kiro_qc_run_context

表创建完成！
```

#### 2.2 初始化规则数据
```bash
python init_rules.py
```

**预期输出**:
```
开始初始化规则...
✓ 规则 A18x03_value_check 初始化成功
✓ 规则 A18x01_cross_check_null 初始化成功
...
规则初始化完成！
```

### 步骤3: 配置应用

编辑 `src/main/resources/application.yml`:

```yaml
spring:
  datasource:
    url: jdbc:mysql://your-host:port/database?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=Asia/Shanghai
    username: your-username
    password: your-password
```

### 步骤4: 编译项目

```bash
mvn clean package -DskipTests
```

**预期输出**:
```
[INFO] BUILD SUCCESS
[INFO] Total time: 8.145 s
```

### 步骤5: 启动服务

```bash
java -jar target/qc-system-1.0.0.jar
```

**预期输出**:
```
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::        (v2.7.18)

Started QcApplication in 5.229 seconds
```

### 步骤6: 验证部署

#### 6.1 访问Swagger文档
浏览器打开: http://localhost:4101/swagger-ui/index.html

#### 6.2 测试API
```bash
# 使用curl测试
curl http://localhost:4101/api/qc/rules

# 或使用Python测试脚本
python test_api_auto.py
```

---

## 详细配置

### 数据库配置

#### MySQL连接池配置
```yaml
spring:
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://host:port/database?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: password
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
      connection-timeout: 30000
```

### 服务端口配置

修改 `application.yml`:
```yaml
server:
  port: 4101  # 修改为你需要的端口
```

### 日志配置

```yaml
logging:
  level:
    com.medical.qc: debug  # 开发环境使用debug
    # com.medical.qc: info  # 生产环境使用info
  file:
    name: logs/qc-system.log
    max-size: 10MB
    max-history: 30
```

### MyBatis配置

```yaml
mybatis:
  mapper-locations: classpath:mapper/*.xml
  type-aliases-package: com.medical.qc.entity
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl  # 开发环境
    # log-impl: org.apache.ibatis.logging.slf4j.Slf4jImpl  # 生产环境
```

---

## 使用指南

### 1. 规则管理

#### 1.1 查看所有规则
```bash
GET http://localhost:4101/api/qc/rules
```

#### 1.2 搜索规则
```bash
# 按字段编码搜索
GET http://localhost:4101/api/qc/rules/search?fieldCode=A18x01

# 按关键词搜索
GET http://localhost:4101/api/qc/rules/search?keyword=新生儿

# 组合搜索
GET http://localhost:4101/api/qc/rules/search?fieldCode=A18x01&keyword=体重
```

#### 1.3 添加新规则
直接在数据库中插入:
```sql
INSERT INTO kiro_qc_rule 
(rule_code, field_name, field_code, table_name, rule_type, deduct_score, description, status)
VALUES 
('NEW_RULE_001', '字段名称', 'FIELD_CODE', 'd_mr', 'range_check', -4, '规则描述', 'active');
```

### 2. 单个病案质控

#### 2.1 执行质控
```bash
POST http://localhost:4101/api/qc/check/single?a48=19079841&a49=1
```

#### 2.2 查看结果
```bash
GET http://localhost:4101/api/qc/result/case?a48=19079841&a49=1
```

**返回结果说明**:
- `finalScore`: 最终得分 (100分制)
- `defectCount`: 缺陷数量
- `totalDeduct`: 总扣分
- `defectsByField`: 按字段分组的缺陷列表
- `allDefects`: 所有缺陷的明细列表

### 3. 批量质控

#### 3.1 按月质控
```bash
POST http://localhost:4101/api/qc/check/batch
Content-Type: application/json

{
  "periodType": "month",
  "year": 2020,
  "month": 1
}
```

#### 3.2 按季度质控
```bash
POST http://localhost:4101/api/qc/check/batch
Content-Type: application/json

{
  "periodType": "quarter",
  "year": 2020,
  "quarter": 1
}
```

#### 3.3 按年质控
```bash
POST http://localhost:4101/api/qc/check/batch
Content-Type: application/json

{
  "periodType": "year",
  "year": 2020
}
```

#### 3.4 查看批量汇总
```bash
POST http://localhost:4101/api/qc/result/batch/summary
Content-Type: application/json

{
  "periodType": "month",
  "year": 2020,
  "month": 1
}
```

**返回结果说明**:
- `caseCount`: 病案数量
- `totalDefectCount`: 总缺陷数
- `avgDefect`: 平均缺陷 = 总缺陷数 / 病案数量
- `avgScore`: 平均得分
- `status`: 状态 (processing/completed)
- `progress`: 进度百分比

#### 3.5 查看批量明细
```bash
POST http://localhost:4101/api/qc/result/batch/cases
Content-Type: application/json

{
  "periodType": "month",
  "year": 2020,
  "month": 1
}
```

### 4. 使用Swagger测试

1. 打开浏览器访问: http://localhost:4101/swagger-ui/index.html
2. 选择要测试的接口
3. 点击 "Try it out"
4. 填写参数
5. 点击 "Execute"
6. 查看响应结果

---

## 常见问题

### Q1: 服务启动失败，提示端口被占用

**问题**: `Port 4101 was already in use`

**解决方案**:
```bash
# 方案1: 修改端口
# 编辑 application.yml，修改 server.port

# 方案2: 关闭占用端口的进程
# Windows:
netstat -ano | findstr :4101
taskkill /PID <进程ID> /F

# Linux:
lsof -i :4101
kill -9 <进程ID>
```

### Q2: 数据库连接失败

**问题**: `Communications link failure`

**解决方案**:
1. 检查数据库服务是否启动
2. 检查数据库连接信息是否正确
3. 检查防火墙设置
4. 检查MySQL用户权限

```sql
-- 授予权限
GRANT ALL PRIVILEGES ON database.* TO 'username'@'%' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;
```

### Q3: 规则不生效

**问题**: 质控时某些规则没有执行

**解决方案**:
1. 检查规则状态是否为 'active'
```sql
SELECT * FROM kiro_qc_rule WHERE status != 'active';
```

2. 更新规则状态
```sql
UPDATE kiro_qc_rule SET status = 'active' WHERE rule_code = 'RULE_CODE';
```

### Q4: 批量质控进度卡住

**问题**: 批量质控进度一直显示processing

**解决方案**:
1. 检查后端日志
2. 检查数据库连接
3. 重新执行批量质控

### Q5: Swagger页面无法访问

**问题**: 404 Not Found

**解决方案**:
1. 确认服务已启动
2. 检查URL是否正确: http://localhost:4101/swagger-ui/index.html
3. 检查Swagger依赖是否正确

---

## 维护指南

### 日常维护

#### 1. 日志管理
```bash
# 查看日志
tail -f logs/qc-system.log

# 清理旧日志
find logs/ -name "*.log" -mtime +30 -delete
```

#### 2. 数据库备份
```bash
# 备份数据库
mysqldump -h host -P port -u username -p database > backup_$(date +%Y%m%d).sql

# 恢复数据库
mysql -h host -P port -u username -p database < backup_20260116.sql
```

#### 3. 性能监控
```sql
-- 查看慢查询
SELECT * FROM mysql.slow_log ORDER BY query_time DESC LIMIT 10;

-- 查看表大小
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.tables
WHERE table_schema = 'database'
ORDER BY size_mb DESC;
```

### 定期维护

#### 1. 清理历史数据
```sql
-- 清理3个月前的缺陷明细
DELETE FROM kiro_qc_defect_detail 
WHERE check_time < DATE_SUB(NOW(), INTERVAL 3 MONTH);

-- 清理6个月前的批量汇总
DELETE FROM kiro_qc_batch_summary 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 6 MONTH);
```

#### 2. 优化数据库
```sql
-- 优化表
OPTIMIZE TABLE kiro_qc_defect_detail;
OPTIMIZE TABLE kiro_qc_case_result;
OPTIMIZE TABLE kiro_qc_batch_summary;

-- 分析表
ANALYZE TABLE kiro_qc_defect_detail;
ANALYZE TABLE kiro_qc_case_result;
```

#### 3. 更新规则
```sql
-- 禁用旧规则
UPDATE kiro_qc_rule SET status = 'draft' WHERE rule_code = 'OLD_RULE';

-- 启用新规则
UPDATE kiro_qc_rule SET status = 'active' WHERE rule_code = 'NEW_RULE';
```

### 故障排查

#### 1. 服务无响应
```bash
# 检查进程
ps aux | grep qc-system

# 检查端口
netstat -an | grep 4101

# 重启服务
kill -9 <进程ID>
java -jar target/qc-system-1.0.0.jar
```

#### 2. 内存溢出
```bash
# 增加JVM内存
java -Xms512m -Xmx2048m -jar target/qc-system-1.0.0.jar
```

#### 3. 数据库连接池耗尽
```yaml
# 调整连接池配置
spring:
  datasource:
    hikari:
      maximum-pool-size: 20  # 增加最大连接数
      minimum-idle: 10       # 增加最小空闲连接数
```

---

## 升级指南

### 版本升级步骤

1. **备份数据**
```bash
mysqldump -h host -P port -u username -p database > backup_before_upgrade.sql
```

2. **停止服务**
```bash
kill -9 <进程ID>
```

3. **更新代码**
```bash
git pull origin main
```

4. **执行数据库迁移**
```bash
# 如果有新的表结构变更
python migrate_database.py
```

5. **重新编译**
```bash
mvn clean package -DskipTests
```

6. **启动服务**
```bash
java -jar target/qc-system-1.0.0.jar
```

7. **验证升级**
```bash
python test_api_auto.py
```

---

## 生产环境建议

### 1. 使用systemd管理服务 (Linux)

创建 `/etc/systemd/system/qc-system.service`:
```ini
[Unit]
Description=Medical QC System
After=network.target

[Service]
Type=simple
User=qcuser
WorkingDirectory=/opt/qc-system
ExecStart=/usr/bin/java -jar /opt/qc-system/qc-system-1.0.0.jar
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
systemctl start qc-system
systemctl enable qc-system
systemctl status qc-system
```

### 2. 使用Nginx反向代理

```nginx
server {
    listen 80;
    server_name qc.example.com;

    location / {
        proxy_pass http://localhost:4101;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 配置HTTPS

```bash
# 使用Let's Encrypt
certbot --nginx -d qc.example.com
```

---

## 联系支持

如有问题，请联系:
- 技术支持: support@example.com
- 文档: http://docs.example.com
- Issue: https://github.com/example/qc-system/issues

---

**最后更新**: 2026-01-16
**文档版本**: 1.0.0
