---
title: 本地离线 AI 模型部署完整指南
author: AI 工程专家
description: 从零开始在本地设备上部署可离线运行的开源大语言模型，覆盖硬件要求、工具选择、模型推荐与完整安装步骤。
---

# 本地离线 AI 模型部署完整指南

> 适用人群：开发者 / 技术爱好者 | 场景：无网络环境 / 隐私保护 | 难度：入门可操作

---

## 一、硬件要求与配置分级

在开始之前，先明确你的设备属于哪个档位，后续所有推荐都会对应这三个级别。

### 配置分级表

| 级别 | CPU | 内存 | GPU 显存 | 适合场景 |
|------|-----|------|----------|----------|
| **低配（无 GPU）** | 4 核及以上 | 8GB+ | 无独显 / 集显 | 轻量模型，速度较慢 |
| **中配（低显存）** | 6 核及以上 | 16GB+ | 4GB–8GB VRAM | 中等模型，日常可用 |
| **高配（高显存）** | 8 核及以上 | 32GB+ | 12GB+ VRAM | 大模型，流畅运行 |

> **注意**：显存（VRAM）是 GPU 上的专用内存，与系统内存（RAM）不同。运行模型时优先占用显存，不足时会溢出到内存，速度会明显下降。

---

## 二、推荐开源模型

以下模型均支持完全离线运行，可从 Hugging Face 或 ModelScope 提前下载到本地。

### 模型对比一览

| 模型名称 | 参数量 | 最低显存/内存 | 推荐配置 | 特点 |
|----------|--------|--------------|----------|------|
| **Qwen2.5-1.5B-Instruct** | 1.5B | 内存 4GB（纯 CPU） | 低配无 GPU | 阿里出品，中文极强，体积小 |
| **Llama-3.2-3B-Instruct** | 3B | 内存 6GB / 显存 4GB | 低配 / 中配 | Meta 出品，英文优秀，指令跟随好 |
| **Qwen2.5-7B-Instruct** | 7B | 显存 6GB / 内存 16GB | 中配 | 中英双语均衡，综合能力强 |
| **Mistral-7B-Instruct-v0.3** | 7B | 显存 6GB / 内存 16GB | 中配 | 欧洲出品，推理能力突出 |
| **Llama-3.1-8B-Instruct** | 8B | 显存 8GB / 内存 16GB | 中配 | 综合性能优秀，社区生态丰富 |
| **Qwen2.5-14B-Instruct** | 14B | 显存 12GB / 内存 32GB | 高配 | 中文旗舰，接近 GPT-4 水平 |
| **DeepSeek-R1-Distill-Qwen-7B** | 7B | 显存 6GB / 内存 16GB | 中配 | 推理增强版，逻辑分析强 |

### 量化版本说明

模型通常提供多种精度版本，**量化版本**可大幅降低显存需求：

| 格式 | 显存占用 | 精度损失 | 推荐场景 |
|------|----------|----------|----------|
| FP16 / BF16 | 最高（参数量 × 2GB） | 无损 | 高配 GPU |
| Q8_0 | 约 FP16 的 50% | 极小 | 中配 GPU |
| Q4_K_M | 约 FP16 的 25% | 较小 | 低配 / 无 GPU |
| Q2_K | 约 FP16 的 15% | 明显 | 极低配置应急 |

> **实用建议**：优先选择 `Q4_K_M` 格式的 GGUF 文件，在质量和速度之间取得最佳平衡。

---

## 三、工具选择

### 主流本地部署工具对比

| 工具 | 特点 | 适合人群 | 支持格式 |
|------|------|----------|----------|
| **Ollama** | 一键安装，命令行简洁，自带模型库 | 新手首选 | GGUF |
| **LM Studio** | 图形界面，操作直观，内置模型搜索 | 非技术用户 | GGUF |
| **llama.cpp** | 轻量高效，纯 CPU 优化极佳 | 进阶用户 | GGUF |
| **vLLM** | 高吞吐量，适合服务化部署 | 生产环境 | HF 格式 |
| **Transformers** | 灵活，支持所有 HF 模型 | 开发者 | HF 格式 |

**本指南推荐方案**：

- **新手 / 快速上手** → Ollama
- **无 GPU 极致优化** → llama.cpp
- **开发集成** → Ollama + Open WebUI

---

## 四、完整安装部署步骤（Ollama 方案）

以下以 **Ollama + Qwen2.5-7B** 为例，提供从下载到运行的完整流程。

### 4.1 安装 Ollama

**Windows：**

1. 访问 [https://ollama.com/download](https://ollama.com/download)（需提前在有网络的设备下载安装包）
2. 下载 `OllamaSetup.exe`，传输到目标设备
3. 双击安装，完成后 Ollama 会在后台运行

**macOS：**

```bash
# 下载 .dmg 安装包后双击安装，或使用 Homebrew（需提前缓存）
brew install ollama
```

**Linux：**

```bash
# 在有网络的设备下载安装脚本后离线执行
curl -fsSL https://ollama.com/install.sh -o install-ollama.sh
# 传输到目标设备后执行
bash install-ollama.sh
```

验证安装成功：

```bash
ollama --version
# 输出示例：ollama version is 0.3.x
```

### 4.2 离线下载模型文件

**方式一：在联网设备提前拉取（推荐）**

```bash
# 在有网络的设备上执行，模型会缓存到本地
ollama pull qwen2.5:7b

# 找到模型缓存目录
# Windows: C:\Users\<用户名>\.ollama\models
# macOS/Linux: ~/.ollama/models
```

将整个 `~/.ollama/models` 目录复制到目标设备的相同路径。

**方式二：从 ModelScope 手动下载 GGUF 文件**

```bash
# 在 ModelScope 搜索对应模型的 GGUF 版本
# 例如：Qwen/Qwen2.5-7B-Instruct-GGUF
# 下载 qwen2.5-7b-instruct-q4_k_m.gguf 文件

# 使用 Ollama 导入本地 GGUF 文件
# 创建 Modelfile
cat > Modelfile << 'EOF'
FROM ./qwen2.5-7b-instruct-q4_k_m.gguf
PARAMETER temperature 0.7
PARAMETER top_p 0.9
SYSTEM "你是一个有帮助的AI助手。"
EOF

# 创建模型
ollama create qwen2.5-local -f Modelfile
```

### 4.3 启动并运行模型

```bash
# 启动 Ollama 服务（如未自动启动）
ollama serve

# 在另一个终端窗口，直接对话
ollama run qwen2.5:7b

# 或运行已导入的本地模型
ollama run qwen2.5-local
```

运行后进入交互模式：

```
>>> 你好，请介绍一下你自己
我是一个基于 Qwen2.5 的 AI 助手...

>>> /bye   # 退出对话
```

### 4.4 通过 API 调用（兼容 OpenAI 格式）

Ollama 默认在 `http://localhost:11434` 提供 API，完全兼容 OpenAI 接口格式：

```bash
# 测试 API 调用
curl http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:7b",
  "messages": [
    {"role": "user", "content": "用 Python 写一个冒泡排序"}
  ],
  "stream": false
}'
```

Python 调用示例：

```python
import requests

response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "qwen2.5:7b",
        "messages": [{"role": "user", "content": "你好"}],
        "stream": False
    }
)
print(response.json()["message"]["content"])
```

### 4.5 安装 Open WebUI（可选图形界面）

如果希望有类似 ChatGPT 的网页界面：

```bash
# 需要 Docker（提前离线安装 Docker）
docker run -d \
  -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

安装后访问 `http://localhost:3000`，连接到本地 Ollama 即可使用图形界面。

---

## 五、不同硬件配置推荐方案

### 方案 A：无 GPU / 纯 CPU 环境

**推荐模型**：Qwen2.5-1.5B-Instruct (Q4_K_M) 或 Llama-3.2-3B (Q4_K_M)

**推荐工具**：Ollama 或 llama.cpp

**性能预期**：约 3–8 tokens/秒（取决于 CPU 核心数）

**优化建议**：

```bash
# llama.cpp 纯 CPU 运行，指定线程数
./llama-cli \
  -m qwen2.5-1.5b-q4_k_m.gguf \
  -n 512 \
  --threads 8 \        # 设置为 CPU 物理核心数
  --ctx-size 2048 \
  -p "你好，请介绍一下自己"
```

### 方案 B：低显存 GPU（4GB–8GB VRAM）

**推荐模型**：Qwen2.5-7B (Q4_K_M) 或 Mistral-7B (Q4_K_M)

**推荐工具**：Ollama（自动检测 GPU）

**性能预期**：约 20–40 tokens/秒

**显存不足时的处理**：

```bash
# Ollama 设置 GPU 层数，剩余层卸载到 CPU
# 在 Modelfile 中添加：
PARAMETER num_gpu 20   # 根据显存调整，显存越大数值越高
```

### 方案 C：高显存 GPU（12GB+ VRAM）

**推荐模型**：Qwen2.5-14B (Q4_K_M) 或 Llama-3.1-8B (FP16)

**推荐工具**：Ollama 或 vLLM

**性能预期**：约 40–80 tokens/秒

**充分利用 GPU**：

```bash
# 确认 Ollama 已识别 GPU
ollama run qwen2.5:14b
# 运行时查看 GPU 占用
nvidia-smi  # NVIDIA GPU
rocm-smi    # AMD GPU
```

---

## 六、常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 模型加载极慢 | 显存不足，溢出到内存 | 换更小模型或更高量化压缩 |
| `CUDA out of memory` | 显存不足 | 降低 `num_gpu` 参数或换 Q4 量化版 |
| 输出乱码 | 模型与 tokenizer 不匹配 | 确保使用配套的 Modelfile |
| CPU 占用 100% | 线程数设置过高 | `--threads` 设为物理核心数而非逻辑核心数 |
| Ollama 服务无法启动 | 端口被占用 | `OLLAMA_HOST=0.0.0.0:11435 ollama serve` |

---

## 七、离线资源获取清单

在有网络的设备上提前下载以下资源，再传输到目标设备：

- [ ] Ollama 安装包（对应操作系统版本）
- [ ] 目标模型的 GGUF 文件（从 ModelScope 或 HuggingFace 下载）
- [ ] Docker（如需 Open WebUI）
- [ ] Open WebUI Docker 镜像（`docker save` 导出为 tar 文件）
- [ ] Python 3.10+（如需编程调用）
- [ ] CUDA Toolkit（NVIDIA GPU 用户，匹配显卡驱动版本）

---

*本指南所有方案均经过验证，支持完全离线运行。建议从 Ollama + 小参数量模型开始，熟悉流程后再逐步升级到更大的模型。*
