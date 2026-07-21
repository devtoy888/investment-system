"""Reusable Unicode sparkline generator for QQ/text-only channels.

8-level block characters: ▁▂▃▄▅▆▇█ (index 0-7)
Flat line when all values equal: ▄▄▄▄▄
"""

SPARK_CHARS = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']


def sparkline_8pt(values: list[float]) -> str:
    """Convert float list to 8-level Unicode sparkline bar.

    Args:
        values: Sequence of floats to visualize.

    Returns:
        Sparkline string like '▁▂▇▇█'. Returns '▄' * len(values) if all equal.
        Returns '' if values is empty.
    """
    if not values:
        return ''
    mn, mx = min(values), max(values)
    if mx == mn:
        return '▄' * len(values)
    rng = mx - mn
    return ''.join(
        SPARK_CHARS[min(int((v - mn) / rng * 7), 7)] for v in values
    )


def sparkline_with_summary(gname: str, values: list[float]) -> str:
    """Generate sparkline + range + direction line for a group trend.

    Args:
        gname: Group name like '黄金', '科技/AI'
        values: 5-day change percentages

    Returns:
        Formatted string: '| 分组 | 走势 | 本周幅度 |'
    """
    spark = sparkline_8pt(values)
    if not values:
        return f'| {gname} | — | 尚无趋势数据 |'

    first, last = values[0], values[-1]
    if last > first * 1.1 and last < 0:
        direction = '📈 跌幅收窄'
    elif last < first and last < 0:
        direction = '📉 跌幅扩大'
    elif last > first and last > 0:
        direction = '📈 持续上行'
    elif last < first and last > 0:
        direction = '📉 涨幅收窄'
    else:
        direction = '➖ 震荡'

    return (
        f'| {gname} | {spark} | '
        f'{min(values):+.1f}% → {max(values):+.1f}% {direction} |'
    )
