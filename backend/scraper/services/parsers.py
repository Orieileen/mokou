# scraper/seivices/parsers.py

import json
import logging
import re
from typing import Any, Dict, List


logger = logging.getLogger(__name__)


# 获取asin_list (返回1个列表,根据不同parserName,列表内返回不同数量terms)
def get_asin_list(response: Dict[str, Any]) -> List[str]:
    try:
        asin_list = [item.get("id") for item in json.loads(
            json.loads(response.get("data").get("json")[0]).get("data").get("recsList")
        )]
    except (AttributeError, IndexError, TypeError, json.JSONDecodeError) as e:
        logger.error(f"错误: 无法从response中解析asin_list。数据结构可能不正确。{e}")
        raise RuntimeError(f"无法从response中解析asin_list。数据结构可能不正确。{e}")
    return asin_list


def get_title_and_bp(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    解析response中的listing数据，返回title和bullet_points
    """
    try:
        node = json.loads(response.get("data").get("json")[0]).get("data").get("results")[0]
        title = node["title"].strip().strip('"') # 移除前后空格和可能存在的引号
        # 获取原始描述文本并去除首尾空白字符
        bp_raw = node["description"].strip()
        # 按正则两个及以上空格拆分 bullet points，过滤掉空字符串 re.split()返回列表
        bullets = [s for s in re.split(r"\s{2,}", bp_raw) if s]

        # 返回title和bullet_points
        raw_listing = {
            "title": title,
            "bullet_points": bullets,
        }

    except (AttributeError, IndexError, TypeError, json.JSONDecodeError) as e:
        logger.error(f"错误: 无法从Raw_listing中解析title & bullet_points。数据结构可能不正确。{e}")
        raise RuntimeError(f"无法从Raw_listing中解析title & bullet_points。数据结构可能不正确。{e}")

    return raw_listing


def get_review_summaries(response: Dict[str, Any]) -> Dict[str, Any]:
    pass


def get_next_page(response: Dict[str, Any]) -> str:
    try:
        next_page = f"https://www.amazon.com{json.loads(json.loads(response).get('data').get('json')[0]).get('data').get('nextPage')}"
    except (AttributeError, IndexError, TypeError, json.JSONDecodeError) as e:
        logger.error(f"错误: 无法从response中解析nextPage。数据结构可能不正确。{e}")
        raise RuntimeError(f"无法从response中解析nextPage。数据结构可能不正确。{e}")
    return next_page