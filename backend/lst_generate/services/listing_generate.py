# lst_generate/services/listing_generate.py
import json
from typing import Any, Dict

from config.promts.LISTING_SYSTEM_PROMPT import LISTING_SYSTEM_PROMPT_V1
from config.promts.LISTING_USER_PROMPT import LISTING_USER_PROMPT_V1
from config.settings import openai_client


def generate_listing(keyword_seed: Dict[str, Any]) -> Dict[str, Any]:
    system_prompt = LISTING_SYSTEM_PROMPT_V1
    user_prompt = LISTING_USER_PROMPT_V1
    response = openai_client.chat.completions.create(
        model="chatgpt-4o-latest",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt.format(keyword_seed=keyword_seed)},
        ],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    keyword_seed = {
        "title_keywords": ["iphone 13 pro max", "512gb", "golden color"],
        "bullet_point_keywords": [
            {"theme": "storage and color", "keywords": ["512gb", "golden color"]},
            {"theme": "display features", "keywords": ["6.7 in super retina xdr display"]},
            {"theme": "camera features", "keywords": ["12mp ultrawide camera", "12mp wide camera", "12mp telephoto camera"]},
        ],
    }
    keyword_seed_json = json.dumps(keyword_seed)
    print(generate_listing(keyword_seed_json))