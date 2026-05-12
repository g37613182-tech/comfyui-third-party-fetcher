# ComfyUI 三方平台内容爬取节点

## 🚀 功能
从抖音、TikTok、Sora2等三方平台提取媒资信息。

## 📦 安装

### 方式1：自动安装（推荐）
插件会在加载时自动安装所需的 CapTools SDK，无需手动操作：

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/g37613182-tech/comfyui-third-party-fetcher.git
```

然后重启 ComfyUI，插件会自动安装依赖。

### 方式2：手动安装（字节内部源）
如果自动安装失败，使用字节内部源手动安装：

```bash
cd ComfyUI/custom_nodes/comfyui-third-party-fetcher
pip install -i https://bytedpypi.byted.org/simple 'bytedance.captools>=0.0.24'
```

### BA 平台专用
在字节 BA 平台使用时：
1. 直接安装插件包即可
2. 插件会自动尝试安装 `bytedance.captools`
3. 如果自动安装失败，请截图终端报错信息，联系平台管理员

## 🔧 配置

### 方式1：环境变量（推荐）
```bash
export MATRIX_REP_KEY="你的rep_key"
python ComfyUI/main.py
```

### 方式2：节点输入
在节点中直接填写 `rep_key` 参数。

## 🎯 使用

### 节点参数
- **platform**: 平台选择 (douyin/tiktok/sora)
- **url**: 三方平台内容链接
- **rep_key**: Matrix rep_key（或通过环境变量）
- **cookie**: Cookie信息（TikTok/Sora需要）
- **device_id**: Device ID（TikTok需要）
- **authorization**: Authorization Token（Sora需要）
- **cut_path**: Sora导航路径
- **total**: 获取数量（Sora用）
- **cursor**: 分页游标（Sora用）

### 输出
- **JSON**: 完整返回数据
- **VIDEO_URL**: 视频直链
- **TITLE**: 视频标题
- **AUTHOR**: 作者信息

## ⚠️ 注意事项

1. **需要 Matrix 平台权限**，必须有有效的 rep_key
2. **TikTok 需要在海外环境执行**
3. **CapTools SDK 是必须的依赖**
4. 请妥善保管 rep_key，不要提交到公开仓库

## 🛠️ 技术栈
- ComfyUI V1 API
- CapTools Python SDK
- httpx (通过 SDK内部使用)

## 📄 许可证
MIT License

## 🔗 相关文档
- [Matrix 平台](https://capcut-aihub.bytedance.net/matrix/edit/media_extract)
- [CapTools Python SDK](https://code.byted.org/capcut-server/agent_tool_common/tree/feat/agent_tool_sdk)
