# 智能边缘视觉分析网关 - 系统需求与设计规格说明书 (v1.1)

## 1. 系统概述
**产品名称**：智能边缘视觉分析网关 (Intelligent Edge Visual Analysis Gateway)  
**应用场景**：养殖猪场等边缘环境。  
**核心引擎**：基于 `qwen3-vl:2b` 多模态大模型，通过 Ollama 接口调用。  
**核心价值**：结合边缘侧实时抓拍与中心侧大模型复核，实现对人、车、动物及异常行为的精准识别与闭环管理。

## 2. 详细功能需求

### 2.1 目标检测 (Target Detection)
系统需支持以下两类目标检测能力：
1.  **核心预设目标**：
    *   人 (Person)
    *   车 (Car/Vehicle)
    *   猪 (Pig)
    *   鼠 (Rat)
    *   鸟 (Bird)
    *   猫 (Cat)
    *   狗 (Dog)
    *   鸡 (Chicken)
2.  **自定义自然语言目标**：
    *   支持用户通过自然语言描述定义新的检测目标（例如：“穿红衣服的人”、“躺着的猪”）。
    *   系统需将自然语言描述转化为 System Prompt 注入模型。

### 2.2 事件复核 (Event Review)
实现“上报-分析-展示”的闭环流程：
*   **输入 (Input)**：提供 API 接口接收边缘设备上报的事件包（包含：设备ID、时间戳、初筛事件类型、现场抓拍图片 Base64/URL）。
*   **分析 (Analysis)**：网关调用 Qwen3-VL 对图片进行推理，判断事件真实性（例如：上报“有鼠”，模型判断“是/否”及置信度）。
*   **输出 (Output)**：
    *   API 响应分析结果。
    *   WEB 端实时弹窗报警。
    *   数据库记录事件详情及复核结果。

### 2.3 批量测试与验证 (Batch Lab) **(新增)**
为了方便测试大模型效果，增加独立的批量测试页面。支持 **拖拽上传** 批量图片。
用户需在测试前选定本次任务类型：
1.  **纯目标检测模式 (Raw Detection)**：
    *   **输入**：一批原始图片 (Raw Images)。
    *   **处理**：系统依次调用大模型，识别图中所有包含的预设目标。
    *   **输出**：展示图片列表，下方标注模型识别到的目标文本及置信度。
2.  **事件复核验证模式 (Review Verification)**：
    *   **输入**：一批**带有目标分类矩形框**的图片（模拟边缘算法已绘制框线）。
    *   **注意**：矩形框上的分类可能不准确（例如把猫框选并标记为“鼠”）。
    *   **用户操作**：用户指定“待验证目标”（如：鼠）。
    *   **Prompt 策略**：系统构建 Prompt（“图中标记框内的物体是[鼠]吗？请忽略框线本身的干扰，只判断物体特征。”）。
    *   **输出**：复核列表，标记“一致/不一致” (True/False) 及模型分析理由。

### 2.4 系统配置 (System Configuration)
*   **模型管理**：
    *   提供大模型选择下拉列表（Dropdown）。
    *   **系统默认选中**：`ollama:qwen3-vl:2b`。
    *   支持刷新 Ollama 现有模型列表。
*   **Prompt 管理**：针对不同目标配置不同的 System Prompt。

## 3. 页面交互与布局设计 (UI/UX)
遵循“高端、动态、极简”的设计原则，采用深色模式（Dark Mode）。

### 3.1 导航布局
采用经典的 **顶部-左侧 (Top-Left)** 二级导航结构：
*   **顶部一级菜单 (Top Header)**：
    *   **监控中心 (Monitor Center)**：实时态势感知。
    *   **事件复核 (Event Review)**：历史事件查询与人工审核。
    *   **批量实验室 (Batch Lab)**：**(新增)** 批量上传与模型测试。
    *   **系统设置 (System Config)**：模型配置与目标管理。
*   **左侧二级菜单 (Left Sidebar)**：
    *   *监控中心下*：[ 实时看板 | 报警流 ]
    *   *事件复核下*：[ 待复核 | 已归档 ]
    *   *批量实验室下*：[ 目标检测测试 | 标注复核验证 ]
    *   *系统设置下*：[ 模型设置 | 目标定义 | API 密钥 ]

### 3.2 视觉风格
*   **配色**：深灰背景 (`#1a1a1a`) 搭配 科技绿 (`#00ff9d`) 与 警示红 (`#ff4d4d`)。
*   **组件**：使用 Glassmorphism (毛玻璃) 效果的卡片容器。
*   **交互**：按钮悬停微动画，上传区域支持拖拽并带有呼吸灯效。

## 4. 系统架构与技术栈
*   **后端**：Flask (Python 3.10+)。
*   **前端**：HTML5 + Vanilla CSS (CSS3 Variables & Flex/Grid) + Vanilla JS (ES6+)。
*   **数据库**：SQLite (轻量级/开发) 或 PostgreSQL。
*   **AI 接口**：Ollama API (Localhost)。
*   **通信协议**：RESTful API (JSON)。

## 5. 项目目录结构规划
```text
d:/project/vllm-test/
├── app/
│   ├── __init__.py          # Flask App 工厂
│   ├── routes/              # 路由蓝图 (Blueprint)
│   │   ├── main.py          # 页面路由
│   │   ├── api.py           # 上报接口与测试接口
│   ├── services/            # 业务逻辑
│   │   ├── ollama_svc.py    # Ollama 调用封装
│   │   ├── image_proc.py    # 图片预处理
│   ├── models.py            # 数据库模型
│   ├── static/              # 静态资源
│   │   ├── css/
│   │   │   ├── style.css    # 核心样式
│   │   │   ├── theme.css    # 变量定义
│   │   ├── js/
│   │   │   ├── main.js      # 全局JS
│   │   │   ├── upload.js    # 批量上传逻辑
│   ├── templates/           # Jinja2 模板
│   │   ├── base.html        # 基础布局
│   │   ├── batch_lab.html   # 批量测试页
│   │   ├── ...
├── config.py                # 配置文件
├── run.py                   # 启动入口
├── requirements.txt
└── SYSTEM_REQUIREMENTS.md   # 本文档
```
