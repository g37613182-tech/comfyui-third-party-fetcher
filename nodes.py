import os
import json
from typing import Dict, Any, Optional

# 版本号
__version__ = "1.1.0"


class ThirdPartyMediaFetcher:
    """三方平台内容爬取节点 v1.1.0 - 支持抖音、TikTok、Sora2等

    注意：使用此节点需要 Matrix 平台权限和 CapTools SDK。
    安装依赖: pip install bytedance.captools==0.1.65 -i https://bytedpypi.byted.org/simple

    配置方式：
    - 环境变量 MATRIX_REP_KEY: 你的 rep_key
    - 或在节点输入中填写 rep_key
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "platform": (["douyin", "tiktok", "sora"], {
                    "default": "douyin",
                    "tooltip": "选择要爬取的平台"
                }),
                "url": ("STRING", {
                    "default": "",
                    "placeholder": "https://v.douyin.com/xxxxx",
                    "tooltip": "三方平台内容链接"
                }),
            },
            "optional": {
                "rep_key": ("STRING", {
                    "default": "",
                    "placeholder": "你的 rep_key 或留空从环境变量读取",
                    "tooltip": "Matrix rep_key。留空则从 MATRIX_REP_KEY 环境变量读取"
                }),
                "cookie": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Cookie信息（TikTok/Sora需要）"
                }),
                "device_id": ("STRING", {
                    "default": "",
                    "tooltip": "Device ID（TikTok需要）"
                }),
                "authorization": ("STRING", {
                    "default": "",
                    "tooltip": "Authorization Token（Sora需要）"
                }),
                "cut_path": ("STRING", {
                    "default": "",
                    "tooltip": "Sora导航路径"
                }),
                "total": ("INT", {
                    "default": 10,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "tooltip": "获取数量（0表示默认，Sora用）"
                }),
                "cursor": ("STRING", {
                    "default": "",
                    "tooltip": "分页游标（Sora用）"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("JSON", "VIDEO_URL", "TITLE", "AUTHOR")
    FUNCTION = "fetch_media"
    CATEGORY = "media/fetch"
    DESCRIPTION = "从抖音、TikTok等三方平台提取媒资信息（需要Matrix权限和CapTools SDK）"

    def fetch_media(self, platform, url, rep_key="",
                    cookie="", device_id="", authorization="", cut_path="",
                    total=10, cursor=""):
        """调用Matrix三方内容爬取API"""

        # 获取 rep_key
        final_rep_key = rep_key or os.environ.get("MATRIX_REP_KEY", "")

        if not final_rep_key:
            return (json.dumps({"error": "需要提供 rep_key（节点输入或 MATRIX_REP_KEY 环境变量）"}), "", "", "")

        if not url:
            return (json.dumps({"error": "URL不能为空"}), "", "", "")

        # 平台特定验证
        if platform == "tiktok" and not cookie:
            return (json.dumps({"error": "TikTok需要Cookie参数"}), "", "", "")

        # 构建请求参数
        params = {
            "third_media_platform": platform,
            "url": url,
        }

        # 平台特定参数
        if platform == "tiktok":
            params.update({
                "cookie": cookie,
                "device_id": device_id,
            })

        elif platform == "sora":
            params.update({
                "cookie": cookie,
                "authorization": authorization,
                "cut": cut_path,
                "total": total,
                "cursor": cursor,
            })

        # 调用Matrix API
        try:
            result = self._call_matrix_api(final_rep_key, params)

            # 解析返回结果
            video_url = self._extract_video_url(result, platform)
            title = self._extract_title(result, platform)
            author = self._extract_author(result, platform)

            return (
                json.dumps(result, ensure_ascii=False),
                video_url,
                title,
                author
            )

        except Exception as e:
            return (
                json.dumps({"error": str(e)}),
                "",
                "",
                ""
            )

    def _call_matrix_api(self, rep_key: str, params: Dict[str, Any]) -> Dict:
        """调用Matrix三方内容爬取API - 使用CapTools SDK"""
        try:
            from bytedance.captools import CapToolsClient
        except ImportError:
            raise ImportError(
                "CapTools SDK not found (v1.1.0). BA Platform: pip install bytedance.captools==0.1.65 -i https://bytedpypi.byted.org/simple"
            )

        # 初始化 CapTools 客户端
        # 使用 rep_key 作为 task_id 或配置
        client = CapToolsClient()

        # 调用 media_extract 原子能力
        # req_key 为 media_extract
        result = client.call(
            req_key="media_extract",
            params=params,
            rep_key=rep_key
        )

        return result

    def _extract_video_url(self, result: Dict, platform: str) -> str:
        """从结果中提取视频URL"""
        try:
            if platform == "douyin":
                return result.get("video", {}).get("play_addr", {}).get("url_list", [""])[0]
            elif platform == "tiktok":
                return result.get("video", {}).get("play_addr", {}).get("url_list", [""])[0]
            elif platform == "sora":
                # Sora可能是列表
                videos = result.get("videos", [])
                if videos:
                    return videos[0].get("url", "")
            return ""
        except:
            return ""

    def _extract_title(self, result: Dict, platform: str) -> str:
        """从结果中提取标题"""
        try:
            if platform in ["douyin", "tiktok"]:
                return result.get("desc", "")
            elif platform == "sora":
                videos = result.get("videos", [])
                if videos:
                    return videos[0].get("title", "")
            return ""
        except:
            return ""

    def _extract_author(self, result: Dict, platform: str) -> str:
        """从结果中提取作者"""
        try:
            if platform in ["douyin", "tiktok"]:
                author = result.get("author", {})
                return author.get("nickname", author.get("unique_id", ""))
            elif platform == "sora":
                return result.get("user", {}).get("name", "")
            return ""
        except:
            return ""


# 节点注册
NODE_CLASS_MAPPINGS = {
    "ThirdPartyMediaFetcher": ThirdPartyMediaFetcher,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ThirdPartyMediaFetcher": "🌐 三方平台内容爬取 v1.1.0",
}
