import json

log_path = r"C:\Users\llll\.gemini\antigravity-ide\brain\2a0f1800-2888-415a-947f-7bb96d1ef91a\.system_generated\logs\transcript.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            # Find subagent step outputs or tool calls related to console logs
            tool_calls = data.get("tool_calls", [])
            for tc in tool_calls:
                if tc.get("name") == "browser_subagent":
                    # Look at subagent's internal execution if logged
                    pass
            # Or check the output of console log tool calls
            if data.get("type") == "TOOL_CALL" and "capture_browser_console_logs" in str(data):
                print("Tool Call:", json.dumps(data, ensure_ascii=False)[:300])
            if data.get("type") == "TOOL_RESPONSE" and "console" in str(data.get("content", "")):
                content = data.get("content", "")
                print("Tool Response (len={}):".format(len(content)), content[:1000])
                print("-" * 80)
        except Exception as e:
            pass
