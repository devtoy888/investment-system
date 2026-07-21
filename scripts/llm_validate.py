#!/usr/bin/env python3
"""
LLM分析质量验证框架 v2 — 修复了thinking模式兼容性和解析问题
"""

import sys, os, json, time, re
from pathlib import Path
from datetime import date, datetime

sys.path.insert(0, '/opt/data/scripts')
from llm_analysis import (
    call_deepseek, generate_closing_analysis, generate_morning_analysis,
    generate_noon_analysis, generate_decision_analysis, generate_weekly_analysis,
    _read_cache, SUMMARY_DIR, LLM_CACHE_DIR
)

DATA_DIR = Path("/opt/data/fund_system_data")
VALIDATION_DIR = Path("/opt/data/fund_system_data/llm_validation")
VALIDATION_DIR.mkdir(parents=True, exist_ok=True)


def call_evaluate(report_type: str, analysis_text: str) -> dict:
    """调用DeepSeek评估分析质量 — 使用简单prompt避免thinking模式干扰"""
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
    if not DEEPSEEK_API_KEY:
        return {"error": "API密钥未设置"}
    
    prompt = f"""评估以下{report_type}分析报告的质量，输出JSON格式评分（不要额外文字）：

{{
  "data_accuracy": <1-10整数>,
  "logic_consistency": <1-10整数>,
  "practicality": <1-10整数>,
  "conciseness": <1-10整数>,
  "risk_awareness": <1-10整数>,
  "total_score": <平均分>,
  "comment": "<简短评语>",
  "improvement": "<改进建议>"
}}

报告内容：
{analysis_text}"""
    
    import requests
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'deepseek-v4-flash',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 800,
        'temperature': 0.1,
        'stream': False
    }
    
    try:
        resp = requests.post(
            'https://api.deepseek.com/chat/completions',
            headers=headers, json=payload, timeout=90
        )
        resp.raise_for_status()
        data = resp.json()
        content = data['choices'][0]['message']['content']
        
        # 尝试从内容中提取JSON
        # 先找```json ... ```包裹的JSON
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(1))
        else:
            # 直接尝试解析
            parsed = json.loads(content)
        
        # 确保所有必需字段存在
        required = ["data_accuracy", "logic_consistency", "practicality", "conciseness", "risk_awareness"]
        if not all(k in parsed for k in required):
            # 尝试用模型重新生成，包容thinking模式
            return {"error": f"JSON字段不完整: {list(parsed.keys())}"}
        
        return {
            "scores": {
                "A": int(parsed.get("data_accuracy", 0)),
                "B": int(parsed.get("logic_consistency", 0)),
                "C": int(parsed.get("practicality", 0)),
                "D": int(parsed.get("conciseness", 0)),
                "E": int(parsed.get("risk_awareness", 0)),
            },
            "total": float(parsed.get("total_score", 0)),
            "comment": parsed.get("comment", ""),
            "improvement": parsed.get("improvement", ""),
            "raw": content[:300]
        }
    except json.JSONDecodeError as e:
        # JSON解析失败，返回原始内容供调试
        return {"error": f"JSON解析失败: {e}. Raw: {content[:300]}"}
    except Exception as e:
        return {"error": f"评估失败: {type(e).__name__}: {str(e)[:200]}"}


def run_single_validation(report_type: str) -> dict:
    """对单一报告类型做一次完整验证"""
    generators = {
        "closing": generate_closing_analysis,
        "morning": generate_morning_analysis,
        "noon": generate_noon_analysis,
        "decision": generate_decision_analysis,
        "weekly": generate_weekly_analysis,
    }
    
    gen = generators.get(report_type)
    if not gen:
        return {"error": f"未知类型: {report_type}"}
    
    # 从缓存读取
    analysis = _read_cache(report_type)
    if not analysis:
        analysis = gen(use_cache=False)
    
    if not analysis:
        return {"error": f"{report_type} 分析生成失败"}
    
    # 评估
    evaluation = call_evaluate(report_type, analysis)
    
    result = {
        "report_type": report_type,
        "date": date.today().isoformat(),
        "timestamp": datetime.now().isoformat(),
        "analysis_text": analysis,
        "analysis_length": len(analysis),
        "evaluation": evaluation,
        "passed": evaluation.get("total", 0) >= 6.0 if "total" in evaluation else False,
    }
    
    return result


def run_full_validation(round_num: int = 1) -> dict:
    """运行全报告类型验证"""
    report_types = ["closing", "morning", "noon", "decision", "weekly"]
    results = []
    
    for rt in report_types:
        print(f"\n{'='*50}")
        print(f"验证 {rt}...")
        print(f"{'='*50}")
        
        result = run_single_validation(rt)
        results.append(result)
        
        if "error" not in result:
            scores = result.get("evaluation", {}).get("scores", {})
            total = result.get("evaluation", {}).get("total", 0)
            print(f"  ✅ 分析长度: {result['analysis_length']} 字符")
            print(f"  📊 评分: 数据准确性={scores.get('A','?')} 逻辑一致性={scores.get('B','?')} "
                  f"实用性={scores.get('C','?')} 简洁性={scores.get('D','?')} 风险意识={scores.get('E','?')}")
            print(f"  🏆 总分: {total}/10")
            print(f"  💬 评语: {result['evaluation'].get('comment','')[:80]}")
        else:
            print(f"  ❌ {result['error']}")
    
    # 综合统计
    valid_results = [r for r in results if "error" not in r and r["evaluation"].get("total", 0) > 0]
    avg_score = sum(r["evaluation"]["total"] for r in valid_results) / len(valid_results) if valid_results else 0
    
    summary = {
        "round": round_num,
        "date": date.today().isoformat(),
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "avg_score": round(avg_score, 2),
        "pass_count": sum(1 for r in valid_results if r.get("passed")),
        "total_count": len(report_types),
    }
    
    return summary


def format_validation_md(summary: dict) -> str:
    """将验证结果格式化为Markdown报告"""
    lines = []
    lines.append(f"# LLM分析质量验证报告 — 第{summary['round']}轮")
    lines.append(f"")
    lines.append(f"**日期**: {summary['date']}")
    lines.append(f"**时间**: {summary['timestamp']}")
    lines.append(f"**模型**: DeepSeek V4 Flash")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## 综合统计")
    lines.append(f"")
    lines.append(f"| 指标 | 值 |")
    lines.append(f"|:----|:---:|")
    lines.append(f"| 平均分 | {summary['avg_score']}/10 |")
    lines.append(f"| 通过 | {summary['pass_count']}/{summary['total_count']} |")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")
    
    for r in summary["results"]:
        if "error" in r:
            lines.append(f"## ❌ {r['report_type']} — {r['error']}")
            lines.append(f"")
            continue
        
        scores = r.get("evaluation", {}).get("scores", {})
        total = r.get("evaluation", {}).get("total", 0)
        
        if not scores:
            lines.append(f"## ⚠️ {r['report_type']} — 评估数据不完整")
            lines.append(f"")
            continue
        
        lines.append(f"## 📊 {r['report_type']}")
        lines.append(f"")
        lines.append(f"| 维度 | 分数 |")
        lines.append(f"|:---|:---:|")
        lines.append(f"| A. 数据准确性 | {scores.get('A','?')}/10 |")
        lines.append(f"| B. 逻辑一致性 | {scores.get('B','?')}/10 |")
        lines.append(f"| C. 实用性 | {scores.get('C','?')}/10 |")
        lines.append(f"| D. 简洁性 | {scores.get('D','?')}/10 |")
        lines.append(f"| E. 风险意识 | {scores.get('E','?')}/10 |")
        lines.append(f"| **总分** | **{total}/10** |")
        lines.append(f"")
        lines.append(f"**长度**: {r['analysis_length']} 字符")
        lines.append(f"")
        lines.append(f"**评语**: {r['evaluation'].get('comment','')}")
        if r['evaluation'].get('improvement'):
            lines.append(f"")
            lines.append(f"**改进建议**: {r['evaluation']['improvement']}")
        lines.append(f"")
        lines.append(f"### 分析原文")
        lines.append(f"")
        lines.append(f"> {r['analysis_text'].replace(chr(10), chr(10)+'> ')}")
        lines.append(f"")
    
    lines.append(f"---")
    lines.append(f"*由 LLM分析质量验证框架 v2 自动生成*")
    
    return "\n".join(lines)


def save_and_upload(summary: dict):
    """保存并上传验证结果"""
    sys.path.insert(0, '/opt/data')
    from r2_uploader import R2Uploader
    uploader = R2Uploader()
    
    # JSON
    json_path = VALIDATION_DIR / f"validation_round{summary['round']}_{summary['date']}.json"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    
    # MD
    md_content = format_validation_md(summary)
    md_path = VALIDATION_DIR / f"validation_round{summary['round']}_{summary['date']}.md"
    md_path.write_text(md_content, encoding='utf-8')
    
    # HTML（内嵌markdown，避免R2 CORS跨域问题）
    md_escaped = md_content.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LLM分析验证报告 - 第{summary['round']}轮</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         max-width: 800px; margin: 0 auto; padding: 20px;
         background: #0d1117; color: #c9d1d9; line-height: 1.6; }}
  table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
  th, td {{ border: 1px solid #30363d; padding: 8px 12px; text-align: left; }}
  th {{ background: #161b22; }}
  code {{ background: #161b22; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
  pre {{ background: #161b22; padding: 15px; border-radius: 6px; overflow-x: auto; }}
  h1, h2, h3 {{ color: #58a6ff; }}
  a {{ color: #58a6ff; }}
  blockquote {{ border-left: 3px solid #30363d; margin: 10px 0; padding: 0 15px; color: #8b949e; }}
</style>
</head>
<body>
<div id="content">加载中...</div>
<script>
const mdContent = `{md_escaped}`;
document.getElementById('content').innerHTML = marked.parse(mdContent);
</script>
</body>
</html>"""
    html_path = md_path.with_suffix('.html')
    html_path.write_text(html_content, encoding='utf-8')
    
    print(f"\n✅ 验证结果已保存:")
    print(f"  📄 JSON: {json_path}")
    print(f"  📝 MD:   {md_path}")
    print(f"  🌐 HTML: {html_path}")
    
    # 上传R2
    r2_base = "fund-system/llm-validation"
    urls = []
    
    for f in [md_path, html_path, json_path]:
        fname = f.name
        if f.suffix == '.json':
            ct = 'application/json; charset=utf-8'
        elif f.suffix == '.md':
            ct = 'text/markdown; charset=utf-8'
        else:
            ct = 'text/html; charset=utf-8'
        
        try:
            url = uploader.upload_file(str(f), f'{r2_base}/{fname}', ct)
            print(f"  ☁️ R2: {r2_base}/{fname}")
            urls.append(url)
        except Exception as e:
            print(f"  ⚠️ R2上传失败({fname}): {e}")
    
    return urls[0] if urls else ""


if __name__ == "__main__":
    round_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    print(f"🔥 LLM分析质量验证 — 第{round_num}轮")
    print(f"{'='*50}")
    
    # 1. 运行验证
    summary = run_full_validation(round_num)
    
    # 2. 保存+上传
    url = save_and_upload(summary)
    
    # 3. 打印总结
    print(f"\n{'='*50}")
    print(f"📊 第{round_num}轮验证完成")
    print(f"   平均分: {summary['avg_score']}/10")
    print(f"   通过率: {summary['pass_count']}/{summary['total_count']}")
    print(f"   URL: {url}")
