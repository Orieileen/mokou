# config/promts/PATTERN_PROMPT.py

PATTERN_PROMPT_V1 = """
你是亚马逊装饰画主图生成大师，请根据以下产品标题并生成主图，忽略标题中的商标、尺寸等无关信息：生成一个图案，只要正面，不能出现任何透视、文字、数字，图案铺满整个画面，不要为图案生成额外背景、墙壁、文字、数字。
产品标题：{title_keywords}
"""
prompt_version = 1.0


PATTERN_PROMPT_V2 = """
Generate a seamless, minimalistic pattern based solely on the following keywords: {title_keywords}.
The pattern should have no text, no realistic objects.
Realistic objects.  
Use a clean, balanced composition, with high contrast and harmonious colors. Centered design, no background clutter.
"""
prompt_version = 2.0