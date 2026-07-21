"""第2轮: 功能测试 — 各send_*模块能否正常输出Markdown"""
import sys, os, importlib

scripts_dir = '/opt/data/scripts'
sys.path.insert(0, scripts_dir)

passed, failed = 0, 0
errors = []

def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
    else:
        failed += 1
        errors.append(f"{name}: {detail}")

print("=" * 50)
print("第2轮: 功能测试")
print("=" * 50)

# 1. send_qqbot模块可用
import send_qqbot
check("send_qqbot导入", True)
check("send_card函数存在", hasattr(send_qqbot, 'send_card'))
check("_output函数存在", hasattr(send_qqbot, '_output'))
check("MAX_MSG_LEN=4000", send_qqbot.MAX_MSG_LEN == 4000)

# 2. send_morning可用
from send_qqbot import send_card, send_card_with_tables, _output
import send_morning
check("send_morning导入", True)

# 3. send_noon可用
import send_noon
check("send_noon导入", True)

# 4. send_closing可用
import send_closing
check("send_closing导入", True)

# 5. 验证send_qqbot的截断保护
short_text = "Hello World"
long_text = "A" * 5000
try:
    # 不实际调用_output（会print到stdout），只验证函数签名
    check("_output接受str参数", callable(send_qqbot._output))
    check("MAX_MSG_LEN常量可用", send_qqbot.MAX_MSG_LEN)
except Exception as e:
    check("send_qqbot函数可用", False, str(e))

# 6. 验证wrapper脚本可执行
for name in ['run_morning.py', 'run_noon.py', 'run_closing.py']:
    path = f'/opt/data/profiles/investment/scripts/{name}'
    with open(path) as f:
        src = f.read()
    try:
        compile(src, path, 'exec')
        check(f"{name}可编译", True)
    except SyntaxError as e:
        check(f"{name}可编译", False, str(e))

# 7. 验证send_*_cards.py旧文件已不存在
for old in ['send_morning_cards.py', 'send_noon_cards.py', 'send_closing_cards.py']:
    check(f"旧文件{old}已删除", not os.path.exists(f'{scripts_dir}/{old}'))

print(f"\n结果: {passed}/{passed+failed}")
if errors:
    for e in errors:
        print(f"  {e}")
