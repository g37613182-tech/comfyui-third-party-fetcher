# ComfyUI 三方平台内容爬取节点

从抖音、TikTok、Sora2等三方平台提取媒资信息。

## 重要提示

**此节点需要 Matrix 平台权限。**

代码中**不包含任何默认的 API 地址或认证信息**。有权限的人需要自行配置才能使用。

## 安装

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/guoyuanwei/comfyui-third-party-fetcher.git
cd comfyui-third-party-fetcher
pip install -r requirements.txt
```

## 配置方式（二选一）

### 方式1：环境变量（推荐）

在启动 ComfyUI 前设置环境变量：

```bash
export MATRIX_BASE_URL="https://matrix.xxx.net/api"
export MATRIX_REP_KEY="your_rep_key_here"
python main.py
```

Windows:
```cmd
set MATRIX_BASE_URL=https://matrix.xxx.net/api
set MATRIX_REP_KEY=your_rep_key_here
python main.py
```

### 方式2：节点输入

在工作流中直接填写：
- `matrix_base_url`: Matrix API 基础地址
- `rep_key`: 你的 rep_key

## 使用

在ComfyUI中添加 "🌐 三方平台内容爬取" 节点：

1. **配置 Matrix 连接**（如果未设置环境变量）
   - 填写 `matrix_base_url`
   - 填写 `rep_key`

2. **选择平台**（douyin/tiktok/sora）

3. **输入 URL**

4. **根据平台要求填写鉴权参数**
   - TikTok: Cookie + Device ID
   - Sora: Cookie + Authorization

5. **运行工作流**

## 输出

- **JSON**: 返回的完整JSON数据
- **VIDEO_URL**: 视频直链
- **TITLE**: 视频标题
- **AUTHOR**: 作者信息

## 支持平台

| 平台 | 状态 | 必需参数 |
|------|------|----------|
| 抖音 | ✅ | URL |
| TikTok | ✅ | URL, Cookie, Device ID |
| Sora2 | ✅ | URL, Cookie, Authorization |

## 注意事项

- 此节点需要字节内部 Matrix 平台权限
- TikTok 需要在海外环境执行
- 请妥善保管 rep_key，不要提交到任何仓库
- 没有权限的人无法使用此节点

## 权限说明

此节点本身只是一个客户端封装，**不包含任何内置权限**。只有拥有 Matrix 平台 rep_key 的人才能使用。
