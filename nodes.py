import os
from comfy_api.latest import ComfyExtension, io, ui
from typing_extensions import override
import json
from typing import Dict, Any, Optional


class ThirdPartyMediaFetcher(io.ComfyNode):
    """三方平台内容爬取节点 - 支持抖音、TikTok、Sora2等

    注意：使用此节点需要 Matrix 平台权限。
    请在环境变量或节点输入中配置 API 地址和认证信息：
    - MATRIX_BASE_URL: Matrix API 基础地址
    - MATRIX_REP_KEY: 你的 rep_key
    """

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="ThirdPartyMediaFetcher",
            display_name="🌐 三方平台内容爬取",
            category="media/fetch",
            description="从抖音、TikTok等三方平台提取媒资信息（需要Matrix权限）",
            inputs=[
                # Matrix API 配置（有权限的人填写）
                io.String.Input(
                    "matrix_base_url",
                    multiline=False,
                    default="",
                    placeholder="https://matrix.xxx.net/api 或留空从环境变量读取",
                    tooltip="Matrix API 基础地址。留空则从 MATRIX_BASE_URL 环境变量读取"
                ),

                io.String.Input(
                    "rep_key",
                    multiline=False,
                    default="",
                    placeholder="你的 rep_key 或留空从环境变量读取",
                    tooltip="Matrix rep_key。留空则从 MATRIX_REP_KEY 环境变量读取"
                ),

                # 平台选择
                io.Combo.Input(
                    "platform",
                    options=["douyin", "tiktok", "sora"],
                    default="douyin",
                    tooltip="选择要爬取的平台"
                ),

                # URL输入
                io.String.Input(
                    "url",
                    multiline=False,
                    placeholder="https://v.douyin.com/xxxxx",
                    tooltip="三方平台内容链接"
                ),

                # Cookie (TikTok/Sora需要)
                io.String.Input(
                    "cookie",
                    multiline=True,
                    default="",
                    tooltip="Cookie信息（TikTok/Sora需要）"
                ),

                io.String.Input(
                    "device_id",
                    default="",
                    tooltip="Device ID（TikTok需要）"
                ),

                # Sora特有参数
                io.String.Input(
                    "authorization",
                    default="",
                    tooltip="Authorization Token（Sora需要）"
                ),

                io.String.Input(
                    "cut_path",
                    default="",
                    tooltip="Sora导航路径"
                ),

                io.Int.Input(
                    "total",
                    default=10,
                    min=0,
                    max=100,
                    step=1,
                    tooltip="获取数量（0表示默认，Sora用）"
                ),

                io.String.Input(
                    "cursor",
                    default="",
                    tooltip="分页游标（Sora用）"
                ),
            ],
            outputs=[
                io.String.Output("JSON", tooltip="返回的完整JSON数据"),
                io.String.Output("VIDEO_URL", tooltip="视频直链"),
                io.String.Output("TITLE", tooltip="视频标题"),
                io.String.Output("AUTHOR", tooltip="作者信息"),
            ],
        )

    @classmethod
    def validate_inputs(cls, matrix_base_url, rep_key, platform, url, **kwargs):
        # 检查 Matrix 配置
        final_base_url = matrix_base_url or os.environ.get("MATRIX_BASE_URL", "")
        final_rep_key = rep_key or os.environ.get("MATRIX_REP_KEY", "")

        if not final_base_url:
            return "需要提供 Matrix Base URL（节点输入或 MATRIX_BASE_URL 环境变量）"
        if not final_rep_key:
            return "需要提供 rep_key（节点输入或 MATRIX_REP_KEY 环境变量）"

        if not url:
            return "URL不能为空"
        if not url.startswith(("http://", "https://")):
            return "URL格式不正确"

        # 平台特定验证
        if platform == "tiktok" and not kwargs.get("cookie"):
            return "TikTok需要Cookie参数"

        return True

    @classmethod
    async def execute(cls, matrix_base_url, rep_key, platform, url, cookie, device_id,
                      authorization, cut_path, total, cursor):
        """调用Matrix三方内容爬取API"""

        # 获取 Matrix 配置（优先使用节点输入，其次环境变量）
        final_base_url = matrix_base_url or os.environ.get("MATRIX_BASE_URL", "")
        final_rep_key = rep_key or os.environ.get("MATRIX_REP_KEY", "")

        if not final_base_url or not final_rep_key:
            raise ValueError("Matrix Base URL 和 rep_key 必须提供（节点输入或环境变量）")

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
            result = await cls._call_matrix_api(final_base_url, final_rep_key, params)

            # 解析返回结果
            video_url = cls._extract_video_url(result, platform)
            title = cls._extract_title(result, platform)
            author = cls._extract_author(result, platform)

            return io.NodeOutput(
                json.dumps(result, ensure_ascii=False),
                video_url,
                title,
                author,
                ui=ui.PreviewText(f"✅ 成功获取 {platform} 内容\n标题: {title}\n作者: {author}")
            )

        except Exception as e:
            return io.NodeOutput(
                json.dumps({"error": str(e)}),
                "", "", "",
                ui=ui.PreviewText(f"❌ 获取失败: {str(e)}")
            )

    @classmethod
    async def _call_matrix_api(cls, base_url: str, rep_key: str, params: Dict[str, Any]) -> Dict:
        """调用Matrix三方内容爬取API"""
        import httpx

        headers = {
            "Authorization": f"Bearer {rep_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/third_media/fetch",
                headers=headers,
                json=params
            )
            response.raise_for_status()
            return response.json()

    @classmethod
    def _extract_video_url(cls, result: Dict, platform: str) -> str:
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

    @classmethod
    def _extract_title(cls, result: Dict, platform: str) -> str:
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

    @classmethod
    def _extract_author(cls, result: Dict, platform: str) -> str:
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


# 扩展注册
class ThirdPartyExtension(ComfyExtension):
    @override
    async def get_node_list(self) -> list[type[io.ComfyNode]]:
        return [ThirdPartyMediaFetcher]


async def comfy_entrypoint() -> ThirdPartyExtension:
    return ThirdPartyExtension()
