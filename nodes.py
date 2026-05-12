import os
import json
import asyncio
from typing import Dict, Any


class ThirdPartyMediaFetcher:
    """三方平台内容爬取节点 - 支持抖音、TikTok、Sora2等

    注意：使用此节点需要 Matrix 平台权限。
    请在环境变量或节点输入中配置 API 地址和认证信息：
    - MATRIX_BASE_URL: Matrix API 基础地址
    - MATRIX_REP_KEY: 你的 rep_key
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
                "matrix_base_url": ("STRING", {
                    "default": "",
                    "placeholder": "https://matrix.xxx.net/api 或留空从环境变量读取",
                    "tooltip": "Matrix API 基础地址。留空则从 MATRIX_BASE_URL 环境变量读取"
                }),
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
    DESCRIPTION = "从抖音、TikTok等三方平台提取媒资信息（需要Matrix权限）"

    def fetch_media(self, platform, url, matrix_base_url="", rep_key="",
                    cookie="", device_id="", authorization="", cut_path="",
                    total=10, cursor=""):
        """调用Matrix三方内容爬取API"""

        # 获取 Matrix 配置（优先使用节点输入，其次环境变量）
        final_base_url = matrix_base_url or os.environ.get("MATRIX_BASE_URL", "")
        final_rep_key = rep_key or os.environ.get("MATRIX_REP_KEY", "")

        if not final_base_url:
            return (json.dumps({"error": "需要提供 Matrix Base URL"}), "", "", "")
        if not final_rep_key:
            return (json.dumps({"error": "需要提供 rep_key"}), "", "", "")

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
            result = self._call_matrix_api_sync(final_base_url, final_rep_key, params)

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

    def _call_matrix_api_sync(self, base_url: str, rep_key: str, params: Dict[str, Any]) -> Dict:
        """同步调用Matrix三方内容爬取API"""
        import httpx

        headers = {
            "Authorization": f"Bearer {rep_key}",
            "Content-Type": "application/json",
        }

        # 使用同步客户端
        with httpx.Client(timeout=30.0) as client:
            full_url = f"{base_url}/third_media/fetch"
            print(f"[ThirdPartyMediaFetcher] Calling API: {full_url}")
            print(f"[ThirdPartyMediaFetcher] Params: {params}")

            response = client.post(
                full_url,
                headers=headers,
                json=params
            )

            print(f"[ThirdPartyMediaFetcher] Response status: {response.status_code}")
            print(f"[ThirdPartyMediaFetcher] Response content preview: {response.text[:500]}")

            # 检查状态码
            if response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}: {response.text[:200]}")

            # 尝试解析 JSON
            try:
                return response.json()
            except json.JSONDecodeError as e:
                raise Exception(f"Invalid JSON response: {e}. Content: {response.text[:200]}")

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
    "ThirdPartyMediaFetcher": "🌐 三方平台内容爬取",
}
