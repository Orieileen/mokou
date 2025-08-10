# lst_generate/services/pattern_generate.py
import json
from typing import Any, Dict
import base64

from config.promts.PATTERN_PROMPT import PATTERN_PROMPT_V2
from config.settings import openai_client


def generate_pattern(keyword_seed: Dict[str, Any]) -> Dict[str, Any]:
    title_keywords = json.loads(keyword_seed)["title_keywords"]
    prompt = PATTERN_PROMPT_V2.format(title_keywords=title_keywords)
    print(prompt)

    response = openai_client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        n=1,
        size="1024x1024",
        response_format="url",
    )
    return response.data[0].url
    # return base64.b64decode(response.data[0].b64_json)


if __name__ == "__main__":
    keyword_seed = {
        "title_keywords": ["iphone 17", "512gb", "golden color"],
        "bullet_point_keywords": [
            {"theme": "storage and color", "keywords": ["512gb", "golden color"]},
            {"theme": "display features", "keywords": ["6.7 in super retina xdr display"]},
            {"theme": "camera features", "keywords": ["12mp ultrawide camera", "12mp wide camera", "12mp telephoto camera"]},
        ],
    }
    keyword_seed_json = json.dumps(keyword_seed)
    print(generate_pattern(keyword_seed_json))