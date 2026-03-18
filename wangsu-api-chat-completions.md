# Wangsu ECA Chat Completions API

Source: https://www.wangsu.com/document/eca/api-chat-completions?rsr=ws

Note: This file was generated from a locally rendered HTML snapshot of the source page.

## 聊天生成API说明

## 调用指南

### cURL请求示例

#### 纯文本输入

```bash
curl -X POST "${AIGATEWAY_URL}" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer ${AIGATEWAY_TOKEN}" \
-d '{
    "model": "deepseek-r1",
    "messages": [
        {
            "role": "user",
            "content": "请介绍下网宿的ECA边缘应用产品？"
        }
    ]
}'
```

#### 单图片输入

```bash
curl -X POST "${AIGATEWAY_URL}" \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer ${AIGATEWAY_TOKEN}" \
 -d '{
   "model": "edusolve-v1",
   "messages": [
     {
       "role": "user",
       "content": [
         {
           "type": "text",
           "text": "解答图片里的题目"
         },
         {
           "type": "image_url",
           "image_url": {
             "url": "https://xxxxxxx.png"
           }
         }
       ]
     }
   ],
   "stream": true,
   "max_tokens": 300
 }'
```

#### 多图片输入

```bash
curl -X POST "${AIGATEWAY_URL}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AIGATEWAY_TOKEN}" \
  -d '{
    "model": "gemini-3-pro-image-preview",
    "stream": true,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "text": "Generate a new image as per my requirements: A Chinese model wearing this dress, everything else unchanged",
                    "type": "text"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://xxxxx.jpg"
                    }
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://xxxxx.jpg"
                    }
                }
            ]
        }
    ]
}'
```

#### 结构化输出

```bash
curl -X POST "${AIGATEWAY_URL}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${AIGATEWAY_TOKEN}" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful math tutor. Guide the user through the solution step by step."
      },
      {
        "role": "user",
        "content": "how can I solve 8x + 7 = -23"
      }
    ],
    "response_format": {
      "type": "json_schema",
      "json_schema": {
        "name": "math_reasoning",
        "schema": {
          "type": "object",
          "properties": {
            "steps": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "explanation": { "type": "string" },
                  "output": { "type": "string" }
                },
                "required": ["explanation", "output"],
                "additionalProperties": false
              }
            },
            "final_answer": { "type": "string" }
          },
          "required": ["steps", "final_answer"],
          "additionalProperties": false
        },
        "strict": true
      }
    }
  }'
```

注：多图片输入仅gemini-3-pro-image-preview、gemini-2.5-flash-image支持

### 请求方法

POST

### 请求 URL

${AIGATEWAY_URL}，如 https://aigateway.edgecloudapp.com/v1/xxx/yyy

### 请求头

| 请求头 | 取值 |
| --- | --- |
| Content-Type | application/json |
| Authorization | Bearer ${AIGATEWAY_TOKEN} |

### 请求主体

请求主体是⼀个JSON对象

| 参数名称 | 类型 | 说明 | 取值范围 | 默认值 | 必填 |
| --- | --- | --- | --- | --- | --- |
| model | string | 模型名称 | - | 根据AI网关配置 | 否 |
| messages | array | 对话的内容<br>纯文本输入示例: {<br>    "messages": [<br>        {<br>            "role": "system",<br>            "content": "你是一个产品咨询助手。"<br>        },<br>        {<br>            "role": "user",<br>            "content": "请介绍下网宿的ECA边缘应用产品？"<br>        }<br>    ]<br>}<br>图片url输入示例: {<br>     "messages": [<br>    {<br>      "role": "user",<br>      "content": [<br>        {"type": "text", "text": "请解答图片中的题目"},<br>        {"type": "image_url", "image_url": {"url": "https://example.com/my-image.jpg"}}<br>      ]<br>    }<br>  ]<br>}<br>图片base64输入示例: {<br>    "messages": [<br>    {<br>      "role": "user",<br>      "content": [<br>        {"type": "text", "text": "请解答图片中的题目"},<br>        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAABAAAAAQ...."}}<br>      ]<br>    }<br>  ]<br>} | - | - | 是 |
| - role | string | 消息发送者角色 | system/user/assistant | - | 是 |
| - content | string/array | 消息<br>当为字符串时，直接携带消息内容；<br>当为数组时，元素为对象，包含以下属性：<br>type<br>: 枚举，表示消息类型，取值为<br>text<br>或<br>image_url<br>，此属性必填。<br>text<br>: 字符串，表示文本消息内容，当<br>type<br>为<br>text<br>时必填。<br>image_url<br>: 对象，表示图片消息内容，当<br>type<br>为<br>image_url<br>时必填，其包含以下属性：<br>url<br>: 字符串，图片的URL或Base64编码。Base64格式为<br>data:image/{IMAGE_FORMAT};base64,{IMAGE_BASE64}<br>，其中<br>IMAGE_FORMAT<br>为图片格式（如<br>jpeg<br>、<br>png<br>等），<br>IMAGE_BASE64<br>为图片的Base64编码。 | - | - | 是 |
| stream | boolean | 是否流式输出 | true/false | 根据AI网关配置 | 否 |
| max_tokens | integer | 最大token数量 | - | 根据AI网关配置 | 否 |
| temperature | float | 采样温度。较高数值，输出更随机；较低数值，输出更集中和确定 | [0, 2.0] | 1 | 否 |
| top_p | float | 影响输出文本的多样性。取值越大则生成文本的多样性越强 | [0, 1.0] | 1 | 否 |
| eca_rag | object | RAG参数<br>RAG示例: "eca_rag": {<br>	"knowledge_id": "xxx"<br>} | - | - | 否 |
| - knowledge_id | string | 知识库的ID | - | - | 是 |
| eca_enable_search | boolean | 是否开启联网搜索 | true/false | false | 否 |
| reasoning_effort | string | 模型思考等级，支持的模型有OpenAI的o系列（不支持指定为none），阿里云qwen3，百度ernie-4.5、Anthropic的claude系列（不支持none）及谷歌的gemini系列。<br>与eca_thinking_config参数一起使用时eca_thinking_config优先生效 | low/medium/high/none | 模型默认 | 否 |
| eca_thinking_config | object | 指定思考长度，claude系列与gemini 2.5 系列支持，gemini 3系列建议使用 reasoning_effort<br>JSON 示例: "eca_thinking_config": {<br>	"type": "enabled",<br>	"budget_tokens": 128<br>} | - | - | 否 |
| - type | string | 是否在回答中返回思考内容，仅claude系列支持adaptive | adaptive/disabled/enabled | - | 否 |
| - budget_tokens | integer | 指定thinking的tokens数量，type=enabled 时生效 | gemini系列：[-1, 24576]<br>claude系列：[1024, max_tokens] | gemini系列：-1<br>claude系列：- | 否 |
| tools | array | 包含一个或多个工具对象的数组，供模型在 Function Calling 中调用。设置 tools 且模型判断需要调用工具时，响应会通过 tool_calls 返回工具信息<br>工具调用示例: {<br>    "messages": [<br>      {<br>        "role": "user",<br>        "content": "What'\''s the weather like in Boston today?"<br>      }<br>    ],<br>    "tools": [<br>      {<br>        "type": "function",<br>        "function": {<br>          "name": "get_current_weather",<br>          "description": "Get the current weather in a given location",<br>          "parameters": {<br>            "type": "object",<br>            "properties": {<br>              "location": {<br>                "type": "string",<br>                "description": "The city and state, e.g. San Francisco, CA"<br>              },<br>              "unit": {<br>                "type": "string",<br>                "enum": ["celsius", "fahrenheit"]<br>              }<br>            },<br>            "required": ["location"]<br>          }<br>        }<br>      }<br>   ]<br>} | - | - | 否 |
| eca_context_management | object | 上下文管理配置（包含工具调用结果清理策略）<br>上下文管理配置参数示例: {<br>  "model": "claude-4.5-sonnet",<br>  "stream": false,<br>  "tools": [...],<br>  "messages": [...],<br>  "max_tokens": 4000,<br>  "eca_context_management": {<br>    "edits": [<br>      {<br>        "type": "clear_tool_uses_20250919",<br>        "trigger": {<br>          "type": "input_tokens",<br>          "value": 100000<br>        },<br>        "keep": {<br>          "type": "tool_uses",<br>          "value": 3<br>        },<br>        "clear_tool_inputs": false<br>      }<br>    ]<br>  }<br>} | - | 无 | 否 |
| - edits | array | 上下文编辑策略列表 | - | 无 | 是（当配置eca_context_management时） |
| - type | string | 编辑策略类型（此处为工具调用结果清理策略） | clear_tool_uses_20250919 | 无 | 是 |
| - trigger | object | 触发清理策略的条件 | - | {"type":"input_tokens","value":100000} | 是 |
| - type | string | 触发条件的类型 | input_tokens/tool_uses | input_tokens | 是 |
| - value | number | 触发条件的阈值（当输入token数/工具调用次数超过该值时触发清理） | 正整数 | 100000 | 是 |
| - keep | object | 清理后保留的最近工具调用/结果对的数量 | - | {"type":"tool_uses","value":3} | 是 |
| -type | string | 保留数量的类型 | tool_uses | tool_uses | 是 |
| - value | number | 保留的最近工具调用/结果对的数量 | 正整数 | 3 | 是 |
| - clear_tool_inputs | boolean | 是否在清理工具结果时同时清理工具调用参数 | true/false | false | 否 |
| modalities | array | 模型生成的输出类型，一个模型可能支持多种类型组合，仅openai与gemini系列支持该参数<br>示例: "modalities":["text","image"] | text：表示模型应返回文本<br>image：表示模型应返回图片（仅gemini系列支持）<br>audio：表示模型应返回音频（仅openai系列支持） | ["text"] | 否 |
| eca_image_config | object | 图片生成参数，仅gemini-3-pro-image-preview、gemini-2.5-flash-image支持<br>示例: "eca_image_config": {<br>    "aspect_ratio ": "16:9",<br>    "image_size": "2K"<br>} | - | - | 否 |
| - aspect_ratio | string | 生成图片宽高比 | 1:1、2:3、3:2、3:4、4:3、4:5、5:4、9:16、16:9、21:9 | 1:1 | 否 |
| - image_size | string | 生成图片分辨率, 仅gemini-3.0-pro-image-preview支持 | 1K、2K、4K（4K需特殊申请） | 1K | 否 |
| response_format | object | 返回内容的格式，仅OpenAI（从gpt-4o开始）与Google Gemini系列的模型支持<br>示例: { "type": "json_schema", "json_schema": {...} } | {"type": "text"}：输出文字回复；<br>{"type": "json_schema","json_schema": {...} }：输出指定格式的JSON字符串，构造方式见<br>https://json-schema.org/docs | {"type": "text"} | 否 |

### 响应状态码（通用）

| 状态码 | 说明 |
| --- | --- |
| 200 | 请求成功 |
| 401 | 访问被拒绝，拒绝原因见响应主体。<br>可能的原因有：缺少Authorization请求头，token错误等。 |
| 403 | 访问被拒绝，拒绝原因见响应主体。<br>可能的原因有：请求主体格式错误、请求主体缺少用户问题等。 |
| 500 | 服务器内部错误，原因见响应主体 |

### 响应主体

#### stream模式

文本对话⼀般采⽤流式响应主体，content-type为 text/event-stream，这样可提升体验效果，响应主体是⼀个JSON对象。

| 参数名称 | 类型 | 说明 |
| --- | --- | --- |
| data | object | 存储消息的集合。最后一个data值固定为"[DONE]"，表示所有的data对象已发完，响应主体结束。 |
| - id | string | 该对话的唯一标识符 |
| - object | string | 对象名称 |
| - created | string | 创建聊天完成时的 Unix 时间戳（以秒为单位） |
| - model | string | 实际处理本次请求的模型名称 |
| - choices | array | 模型生成的 completion 的选择列表 |
| – index | int | 该completion在模型生成的completion的选择列表中的索引 |
| – delta | object | 模型生成的completion消息，生图请求应答图片url或图片的base64编码。<br>Base64格式：<br>data:image/${IMAGE_FORMAT};base64,${IMAGE_BASE64}<br>其中，IMAGE_FORMAT为图片格式：jpeg、png、gif等；IMAGE_BASE64为图片的 Base64 编码 |
| – finish_reason | string | stop<br>: 模型自然停止生成，或遇到stop序列中列出的字符串。<br>length:<br>输出长度达到了模型上下文长度限制，或达到了max_tokens的限制。<br>content_filter<br>: 输出内容因触发过滤策略而被过滤。<br>insufficient_system_resource<br>: 系统推理资源不足，生成被打断。 |

纯文本生成示例如下：

```text
data: {
    "id":"2cdfd198-31f6-9c69-ade8-82acb8c65ba1",
    "object":"chat.completion.chunk",
    "created":1739843952,
    "model": "gpt-4o",
    "choices":[
        {
            "index":0,
            "delta":{
                "role":"assistant",
                "content":"",
                "reasoning_content":"???"
            }
        }
    ]
}

...

data: {
    "id":"2cdfd198-31f6-9c69-ade8-82acb8c65ba1",
    "object":"chat.completion.chunk",
    "created":1739843964,
    "model": "gpt-4o",
    "choices":[
        {
            "index":0,
            "delta":{
                "role":"assistant",
                "content":"",
                "reasoning_content":""
            },
            "finish_reason":"stop"
        }
    ]
}
data: [DONE]
```

文本+图片生成示例如下：

```text
data: {"id":"chatcmpl-d9e62990a6d7430b8a8a5ac01d899158","object":"chat.completion.chunk","created":1765522174,"model":"gemini-2.5-flash-image","choices":[{"index":0,"delta":{"content":"Here","reasoning_content":""}}],"usage":{"prompt_tokens":7,"completion_tokens":1,"total_tokens":8,"completion_tokens_details":{},"prompt_tokens_details":{}}}

...

data: {"id":"chatcmpl-a134fe919a2840958b3f574d6bfc9b02","object":"chat.completion.chunk","created":1765522182,"model":"gemini-2.5-flash-image","choices":[{"index":0,"delta":{"content":[{"image_url":{"url":"data:image/png;base64,iVBORw0uQmCC..."},"type":"image_url"}]},"finish_reason":"stop"}],"usage":{"prompt_tokens":7,"completion_tokens":1302,"total_tokens":1309,"completion_tokens_details":{},"prompt_tokens_details":{}}}

data: [DONE]
```

工具调用响应：

```text
data: {"id":"chatcmpl-Cmz8IryT7O5SOSD8T7CPWVfnCs4hi","object":"chat.completion.chunk","created":1765790774,"model":"gpt-4o","choices":[{"index":0,"delta":{"role":"assistant","tool_calls":[{"id":"call_91ay0AOAPJ0TBEk7w0KjagQn","type":"function","function":{"name":"get_current_weather","arguments":""},"index":0}]}}]}

data: {"id":"chatcmpl-Cmz8IryT7O5SOSD8T7CPWVfnCs4hi","object":"chat.completion.chunk","created":1765790774,"model":"gpt-4o","choices":[{"index":0,"delta":{"tool_calls":[{"type":"","function":{"arguments":"{\""},"index":0}]}}]}

data: {"id":"chatcmpl-Cmz8IryT7O5SOSD8T7CPWVfnCs4hi","object":"chat.completion.chunk","created":1765790774,"model":"gpt-4o","choices":[{"index":0,"delta":{"tool_calls":[{"type":"","function":{"arguments":"location"},"index":0}]}}]}

data: {"id":"chatcmpl-Cmz8IryT7O5SOSD8T7CPWVfnCs4hi","object":"chat.completion.chunk","created":1765790774,"model":"gpt-4o","choices":[{"index":0,"delta":{"tool_calls":[{"type":"","function":{"arguments":"\":\""},"index":0}]}}]}

data: {"id":"chatcmpl-Cmz8IryT7O5SOSD8T7CPWVfnCs4hi","object":"chat.completion.chunk","created":1765790774,"model":"gpt-4o","choices":[{"index":0,"delta":{"tool_calls":[{"type":"","function":{"arguments":"Boston"},"index":0}]}}]}

data: {"id":"chatcmpl-Cmz8IryT7O5SOSD8T7CPWVfnCs4hi","object":"chat.completion.chunk","created":1765790774,"model":"gpt-4o","choices":[{"index":0,"delta":{"tool_calls":[{"type":"","function":{"arguments":","},"index":0}]}}]}

data: {"id":"chatcmpl-Cmz8IryT7O5SOSD8T7CPWVfnCs4hi","object":"chat.completion.chunk","created":1765790774,"model":"gpt-4o","choices":[{"index":0,"delta":{"tool_calls":[{"type":"","function":{"arguments":" MA"},"index":0}]}}]}

data: {"id":"chatcmpl-Cmz8IryT7O5SOSD8T7CPWVfnCs4hi","object":"chat.completion.chunk","created":1765790774,"model":"gpt-4o","choices":[{"index":0,"delta":{"tool_calls":[{"type":"","function":{"arguments":"\",\""},"index":0}]}}]}

data: {"id":"chatcmpl-Cmz8IryT7O5SOSD8T7CPWVfnCs4hi","object":"chat.completion.chunk","created":1765790774,"model":"gpt-4o","choices":[{"index":0,"delta":{"tool_calls":[{"type":"","function":{"arguments":"unit"},"index":0}]}}]}

data: {"id":"chatcmpl-Cmz8IryT7O5SOSD8T7CPWVfnCs4hi","object":"chat.completion.chunk","created":1765790774,"model":"gpt-4o","choices":[{"index":0,"delta":{"tool_calls":[{"type":"","function":{"arguments":"\":\""},"index":0}]}}]}

data: {"id":"chatcmpl-Cmz8IryT7O5SOSD8T7CPWVfnCs4hi","object":"chat.completion.chunk","created":1765790774,"model":"gpt-4o","choices":[{"index":0,"delta":{"tool_calls":[{"type":"","function":{"arguments":"fahren"},"index":0}]}}]}

data: {"id":"chatcmpl-Cmz8IryT7O5SOSD8T7CPWVfnCs4hi","object":"chat.completion.chunk","created":1765790774,"model":"gpt-4o","choices":[{"index":0,"delta":{"tool_calls":[{"type":"","function":{"arguments":"heit"},"index":0}]}}]}

data: {"id":"chatcmpl-Cmz8IryT7O5SOSD8T7CPWVfnCs4hi","object":"chat.completion.chunk","created":1765790774,"model":"gpt-4o","choices":[{"index":0,"delta":{"tool_calls":[{"type":"","function":{"arguments":"\"}"},"index":0}]}}]}

data: {"id":"chatcmpl-Cmz8IryT7O5SOSD8T7CPWVfnCs4hi","object":"chat.completion.chunk","created":1765790774,"model":"gpt-4o","choices":[{"index":0,"delta":{},"finish_reason":"tool_calls"}]}

data: {"id":"chatcmpl-Cmz8IryT7O5SOSD8T7CPWVfnCs4hi","object":"chat.completion.chunk","created":1765790774,"model":"gpt-4o","choices":[],"usage":{"prompt_tokens":161,"completion_tokens":31,"total_tokens":192,"completion_tokens_details":{},"prompt_tokens_details":{}}}

data: [DONE]
```

json_schema结构化输出示例：

```text
data: {"id":"chatcmpl-CxrslFQmin0CmrQyhsngKuWykEZYS","object":"chat.completion.chunk","created":1768384511,"model":"gpt-4o","choices":[{"index":0,"delta":{"role":"assistant","content":""}}]}

...

data: {"id":"chatcmpl-CxrslFQmin0CmrQyhsngKuWykEZYS","object":"chat.completion.chunk","created":1768384511,"model":"gpt-4o","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: {"id":"chatcmpl-CxrslFQmin0CmrQyhsngKuWykEZYS","object":"chat.completion.chunk","created":1768384511,"model":"gpt-4o","choices":[],"usage":{"prompt_tokens":101,"completion_tokens":183,"total_tokens":284,"completion_tokens_details":{},"prompt_tokens_details":{}}}

data: [DONE]
```

#### 非stream模式

content-type为 application/json，响应主体是一个JSON对象。

| 参数名称 | 类型 | 说明 |
| --- | --- | --- |
| id | string | 此次响应的唯一标识符，用于追踪和识别特定的响应 |
| model | string | 实际处理本次请求的模型名称 |
| object | string | 表示响应的对象类型，这里<br>chat.completion<br>表明是聊天完成后的响应 |
| created | int | 响应生成的时间戳，代表从 Unix 纪元（1970年1月1日 00:00:00 UTC）到响应生成时刻所经过的秒数 |
| choices | array | 包含模型生成的响应选项列表，通常只有一个选项，每个选项是一个包含相关信息的对象 |
| -index | int | 当前选择在<br>choices<br>数组中的索引位置，一般从0开始 |
| -message | object | 包含模型回复消息的相关信息 |
| --role | string | 消息发送者的角色，这里<br>assistant<br>表示是模型（助手）的回复 |
| --content | string | 模型生成的具体回复内容，生图请求应答图片url或图片的base64编码。<br>Base64格式：<br>data:image/${IMAGE_FORMAT};base64,${IMAGE_BASE64}<br>其中，IMAGE_FORMAT为图片格式：jpeg、png、gif等；IMAGE_BASE64为图片的 Base64 编码 |
| usage | object | 关于此次请求和响应所使用的token数量统计信息 |
| -prompt_tokens | int | 请求中所使用的token数量，即用户输入内容所占用的token数 |
| -completion_tokens | int | 模型响应所使用的token数量，即模型回复内容所占用的token数 |
| -total_tokens | int | 请求和响应总共使用的token数量，等于<br>prompt_tokens<br>与<br>completion_tokens<br>之和 |

示例如下：

```json
{
    "id": "chatcmpl-8g199l9xsC4fPyEYpLywUtI2pQOl7",
    "model": "gpt-4o",
    "object": "chat.completion",
    "created": 1705024875,
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "China Wangsu Company is ..."
            }
        }
    ],
    "usage": {
        "prompt_tokens": 14,
        "completion_tokens": 100,
        "total_tokens": 114
    }
}
```

文本+图片响应示例：

```json
{
	"id": "chatcmpl-5aa21a617f5e46c3bb57d034e2d626ed",
	"model": "gemini-2.5-flash-image",
	"object": "chat.completion",
	"created": 1765522261,
	"choices": [{
		"index": 0,
		"message": {
			"role": "assistant",
			"content": [{
				"text": "Here's a picture of a sunset for you: ",
				"type": "text"
			}, {
				"image_url": {
					"url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABAA..."
				},
				"type": "image_url"
			}],
			"reasoning_content": ""
		},
		"finish_reason": "stop"
	}],
	"usage": {
		"prompt_tokens": 7,
		"completion_tokens": 1302,
		"total_tokens": 1309,
		"completion_tokens_details": {},
		"prompt_tokens_details": {}
	}
}
```

工具调用响应示例：

```json
{
	"id": "chatcmpl-CmzA77lMCLRue8u8BegChh49VgXks",
	"model": "gpt-4o",
	"object": "chat.completion",
	"created": 1765790887,
	"choices": [{
		"index": 0,
		"message": {
			"role": "assistant",
			"tool_calls": [{
				"id": "call_wG6E8K4r63TAQEpiCoHUFFLu",
				"type": "function",
				"function": {
					"name": "get_current_weather",
					"arguments": "{\"location\":\"Boston, MA\",\"unit\":\"fahrenheit\"}"
				}
			}]
		},
		"finish_reason": "tool_calls"
	}],
	"usage": {
		"prompt_tokens": 161,
		"completion_tokens": 31,
		"total_tokens": 192,
		"completion_tokens_details": {},
		"prompt_tokens_details": {}
	}
}
```

json_schema结构化输出示例：

```json
{
	"id": "chatcmpl-CxrnEQFdaKipoMawfUaKHi7pOJASE",
	"model": "gpt-4o",
	"object": "chat.completion",
	"created": 1768384168,
	"choices": [{
		"index": 0,
		"message": {
			"role": "assistant",
			"content": "{\"final_answer\":\"x = -15/4\",\"steps\":[{\"explanation\":\"We begin with the given equation: 8x + 7 = -23.\",\"output\":\"8x + 7 = -23\"},{\"explanation\":\"We want to isolate the term with the variable 'x'. First, we'll subtract 7 from both sides of the equation to eliminate the constant on the left side.\",\"output\":\"8x + 7 - 7 = -23 - 7\"},{\"explanation\":\"Simplifying both sides gives us the equation: 8x = -30.\",\"output\":\"8x = -30\"},{\"explanation\":\"Now, we'll divide both sides by 8 to solve for 'x'.\",\"output\":\"x = -30/8\"},{\"explanation\":\"Simplifying the fraction -30/8, we divide the numerator and the denominator by their greatest common divisor, which is 2.\",\"output\":\"x = -15/4\"}]}"
		},
		"finish_reason": "stop"
	}],
	"usage": {
		"prompt_tokens": 101,
		"completion_tokens": 193,
		"total_tokens": 294,
		"completion_tokens_details": {},
		"prompt_tokens_details": {}
	}
}
```
