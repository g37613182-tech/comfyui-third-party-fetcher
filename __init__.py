import subprocess
import sys
import os


def ensure_captools_installed():
    """确保 CapTools SDK 已安装"""
    try:
        import bytedance.captools
        return True
    except ImportError:
        print("[ThirdPartyMediaFetcher] CapTools SDK not found, attempting to install...")

        # 尝试安装（使用字节内部源）
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "--user",  # 安装到用户目录，避免权限问题
                "--break-system-packages",  # 允许在系统环境中安装
                "-i", "https://bytedpypi.byted.org/simple",  # 字节内部源
                "bytedance.captools>=0.0.24"
            ])

            # 重新加载模块
            import importlib
            import site
            importlib.reload(site)

            # 再次尝试导入
            import bytedance.captools
            print("[ThirdPartyMediaFetcher] ✅ CapTools SDK installed successfully")
            return True

        except subprocess.CalledProcessError as e:
            print(f"[ThirdPartyMediaFetcher] ❌ Failed to install CapTools SDK: {e}")
            print("[ThirdPartyMediaFetcher] Please install manually: pip install -i https://bytedpypi.byted.org/simple 'bytedance.captools>=0.0.24'")
            return False

        except Exception as e:
            print(f"[ThirdPartyMediaFetcher] ❌ Unexpected error: {e}")
            return False


# 尝试安装依赖
ensure_captools_installed()

# 导入节点
from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
