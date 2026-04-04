#!/usr/bin/env python3
"""
配置检查器
用于验证配置文件的一致性和正确性
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Settings, load_env_file
from utils.common.logger import get_logger

logger = get_logger(__name__)

def check_config_consistency():
    """检查配置文件的一致性"""
    logger.info("开始检查配置文件一致性...")
    
    # 检查所有环境配置文件
    env_files = [
        ".env.base",
        ".env.development",
        ".env.testing",
        ".env.staging",
        ".env.standard",
        ".env.full",
        ".env.minimal",
        ".env.example"
    ]
    
    project_root = Path(__file__).parent.parent
    config_dir = project_root / "config" / "envs"
    
    for env_file in env_files:
        file_path = config_dir / env_file
        if file_path.exists():
            logger.info(f"检查配置文件: {env_file}")
            try:
                # 加载配置文件并验证
                load_env_file(env_file)
                # 为每个环境创建Settings实例进行验证
                if env_file == ".env.base":
                    # 基础配置文件，使用默认环境
                    settings = Settings(env="development")
                else:
                    # 从文件名提取环境名称
                    env_name = env_file.replace(".env.", "")
                    if env_name in ["development", "testing", "staging", "production"]:
                        settings = Settings(env=env_name)
                    else:
                        # 对于其他配置文件，使用默认环境
                        settings = Settings(env="development")
                
                # 打印配置摘要
                config_summary = settings.get_config_summary()
                logger.info(f"配置摘要: {config_summary}")
                logger.info(f"✓ 配置文件 {env_file} 验证通过")
            except Exception as e:
                logger.error(f"✗ 配置文件 {env_file} 验证失败: {e}")
        else:
            logger.warning(f"配置文件不存在: {env_file}")
    
    logger.info("配置文件一致性检查完成")

def check_video_enabled_consistency():
    """检查VIDEO_ENABLED配置的一致性"""
    logger.info("开始检查VIDEO_ENABLED配置一致性...")
    
    # 检查所有环境配置文件中的VIDEO_ENABLED设置
    env_files = [
        ".env.development",
        ".env.testing",
        ".env.staging"
    ]
    
    project_root = Path(__file__).parent.parent
    config_dir = project_root / "config" / "envs"
    
    for env_file in env_files:
        file_path = config_dir / env_file
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "VIDEO_ENABLED" in content:
                    # 提取VIDEO_ENABLED的值
                    for line in content.split('\n'):
                        line = line.strip()
                        if line.startswith("VIDEO_ENABLED="):
                            value = line.split('=', 1)[1].strip()
                            logger.info(f"{env_file}: VIDEO_ENABLED={value}")
                else:
                    logger.info(f"{env_file}: VIDEO_ENABLED (使用基础配置值)")
    
    logger.info("VIDEO_ENABLED配置一致性检查完成")

def main():
    """主函数"""
    try:
        logger.info("=== 配置检查器 ===")
        
        # 检查配置文件一致性
        check_config_consistency()
        
        # 检查VIDEO_ENABLED配置一致性
        check_video_enabled_consistency()
        
        logger.info("=== 配置检查完成 ===")
        return 0
    except Exception as e:
        logger.error(f"配置检查失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())