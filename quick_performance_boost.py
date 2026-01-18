#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速性能优化脚本 - 最小改动获得最大收益
只需修改3行代码,预期性能提升20-30倍!
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """备份文件"""
    backup_path = file_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ 已备份: {backup_path}")
    return backup_path

def apply_optimization_1(file_path):
    """优化1: 启用并行处理 (预计8倍提升)"""
    print("\n=== 优化1: 启用并行处理 ===")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找并替换串行处理为并行处理
    old_line = "processBatchRecordsSerial(records, rules, request, summary, batchKey);"
    new_line = "processBatchRecordsParallel(records, rules, request, summary, batchKey);"

    if old_line in content:
        content = content.replace(old_line, new_line)
        print(f"✅ 已启用并行处理")
        print(f"   修改: {old_line}")
        print(f"   改为: {new_line}")
        return content, True
    else:
        print(f"⚠️  未找到需要修改的代码")
        return content, False

def apply_optimization_2(content):
    """优化2: 增加线程数为CPU核心数 (预计1.5倍提升)"""
    print("\n=== 优化2: 优化线程池大小 ===")

    # 查找并替换固定线程数为动态线程数
    old_pattern = r'private final ExecutorService parallelExecutor = Executors\.newFixedThreadPool\(8\);'
    new_code = 'private final ExecutorService parallelExecutor = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors() * 2);'

    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_code, content)
        print(f"✅ 已优化线程池大小")
        print(f"   从固定8线程改为: CPU核心数 × 2")
        return content, True
    else:
        print(f"⚠️  未找到需要修改的代码")
        return content, False

def apply_optimization_3(content):
    """优化3: 增大数据库批次大小 (预计2倍提升)"""
    print("\n=== 优化3: 增大数据库批次 ===")

    # 查找并替换批次大小
    old_pattern = r'private static final int DB_BATCH_SIZE = 50;'
    new_code = 'private static final int DB_BATCH_SIZE = 200;'

    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_code, content)
        print(f"✅ 已增大数据库批次")
        print(f"   从50改为200")
        return content, True
    else:
        print(f"⚠️  未找到需要修改的代码")
        return content, False

def add_performance_logging(content):
    """添加性能监控日志"""
    print("\n=== 添加性能监控 ===")

    # 在processBatchRecordsParallel方法开始添加性能计时
    pattern = r'(private void processBatchRecordsParallel\([^{]+\{)'
    replacement = r'\1\n        long methodStartTime = System.currentTimeMillis();\n        log.info("开始并行处理 {} 个病案,使用 {} 个线程", records.size(), parallelExecutor);'

    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        print(f"✅ 已添加性能监控日志")
        return content, True
    else:
        print(f"⚠️  未找到合适的位置添加日志")
        return content, False

def main():
    print("=" * 60)
    print("医疗质控系统 - 快速性能优化")
    print("=" * 60)
    print("\n📊 预期性能提升:")
    print("   优化1 (启用并行):     8倍")
    print("   优化2 (优化线程池):   1.5倍")
    print("   优化3 (增大批次):     2倍")
    print("   ----------------------------------------")
    print("   综合预期提升:        24倍!")
    print("\n   单病案: 29秒 → 1.2秒")
    print("   96病案: 46分钟 → 2分钟")
    print("=" * 60)

    # 文件路径
    file_path = "src/main/java/com/medical/qc/service/BatchQcServiceOptimized.java"

    if not os.path.exists(file_path):
        print(f"\n❌ 错误: 文件不存在 {file_path}")
        print(f"请确保在项目根目录运行此脚本")
        return

    print(f"\n📁 目标文件: {file_path}")

    # 备份文件
    backup_path = backup_file(file_path)

    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        modified = False

        # 应用优化1: 启用并行处理
        content, changed = apply_optimization_1(file_path)
        modified = modified or changed

        # 应用优化2: 优化线程池
        content, changed = apply_optimization_2(content)
        modified = modified or changed

        # 应用优化3: 增大批次
        content, changed = apply_optimization_3(content)
        modified = modified or changed

        # 添加性能监控
        content, changed = add_performance_logging(content)

        if modified:
            # 写入修改后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print("\n" + "=" * 60)
            print("✅ 优化完成!")
            print("=" * 60)
            print(f"\n📝 已修改文件: {file_path}")
            print(f"💾 备份文件: {backup_path}")

            print("\n📋 下一步操作:")
            print("   1. 重新编译项目:")
            print("      mvn clean compile")
            print()
            print("   2. 重启服务:")
            print("      mvn spring-boot:run")
            print()
            print("   3. 测试性能:")
            print("      python test_optimized_performance.py")
            print()
            print("   4. 如需回滚:")
            print(f"      复制备份文件 {backup_path}")
            print(f"      覆盖到 {file_path}")

        else:
            print("\n⚠️  未执行任何修改")
            print("可能的原因:")
            print("   1. 优化已经应用过")
            print("   2. 代码结构已改变")
            print("   3. 文件版本不匹配")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print(f"正在恢复备份...")
        shutil.copy2(backup_path, file_path)
        print(f"✅ 已恢复原始文件")

if __name__ == "__main__":
    main()
