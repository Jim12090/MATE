#!/bin/bash

# 脚本功能：从 /var/log/kern.log 中提取 2026年3月17日 09:00 至 12:40 的内核日志
# 输出到临时文件 /tmp/kern_20260317_0900-1240.log

set -e  # 遇错退出

LOG_FILE="/var/log/kern.log"
OUTPUT_FILE="/tmp/kern_20260317_0900-1240.log"

# 检查 kern.log 是否存在
if [ ! -f "$LOG_FILE" ]; then
    echo "错误: $LOG_FILE 不存在。" >&2
    exit 1
fi

# 提取指定时间段日志（Mar 17, 09:00 ~ 12:40）
awk '
$1 == "Mar" && $2 == "17" {
    split($3, t, ":")
    hour = t[1] + 0
    min  = t[2] + 0

    if ( (hour == 9 && min >= 0) ||
         (hour > 9 && hour < 12) ||
         (hour == 12 && min <= 40) ) {
        print
    }
}' "$LOG_FILE" > "$OUTPUT_FILE"

echo "✅ 日志已成功提取到: $OUTPUT_FILE"
echo "📄 共 $(wc -l < "$OUTPUT_FILE") 行。"