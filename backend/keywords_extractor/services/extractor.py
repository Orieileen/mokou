# keywords_extractor/services/extractor.py

import json
import logging
from typing import Any, Dict

from config.promts.EXTRACTOR_SYSTEM_PROMPT import EXTRACTOR_SYSTEM_PROMPT_V1
from config.settings import openai_client

logger = logging.getLogger(__name__)


def extract_keywords(raw_listing: Dict[str, Any]) -> Dict[str, Any]:
    prompt = EXTRACTOR_SYSTEM_PROMPT_V1
    json_raw_listing = json.dumps(raw_listing)
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": json_raw_listing},
        ],
        response_format={"type": "json_object"},
    )
    # 最后补关键词存到数据库
    return response.choices[0].message.content


if __name__ == "__main__":
    raw_listing = {
        "title": "Apple iPhone 13 Pro Max 512GB golden color",
        "bullet_points": ["512GB golden color", "6.7 in Super Retina XDR display", "12MP ultrawide camera", "12MP wide camera", "12MP telephoto camera"],
    }
    print(extract_keywords(raw_listing))