# atomic/tasks.py

import logging
import os

from celery import group, shared_task

from scraper.services.parsers import get_asin_list, get_title_and_bp
from scraper.services.scraper_client import ScraperClient


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _get_scraper_client() -> ScraperClient:
    """内部辅助函数，获取已登录的客户端。"""
    client = ScraperClient()
    client.login(os.getenv("SCRAPER_EMAIL"), os.getenv("SCRAPER_PASSWORD"))
    return client


@shared_task(bind=True, max_retries=3, default_retry_delay=120, name="atomic.discover_asins_task")
def discover_asins_task(self, url: str, parserName: str, zipcode: str) -> list[str]:
    """只做一件事：从入口URL获取ASIN列表。"""
    logger.info(f"开始从URL发现ASIN: {url}")
    try:
        client = _get_scraper_client()
        response = client.scrape(url, parserName, zipcode)
        asin_list = get_asin_list(response)
        logger.info(f"成功发现 {len(asin_list)} 个ASIN。")
        return asin_list
    except Exception as e:
        logger.error(f"发现ASIN时失败: {e}")
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60, name="atomic.process_one_asin_task")
def process_one_asin_task(self, asin: str, parserName: str, zipcode: str):
    """只做一件事：处理单个ASIN，获取其详细信息。"""
    logger.info(f"开始处理单个ASIN: {asin}")
    try:
        client = _get_scraper_client()
        url = f"https://www.amazon.com/dp/{asin}"
        response = client.scrape(url=url, parserName=parserName, zipcode=zipcode)
        title_and_bp = get_title_and_bp(response)
        logger.info(f"ASIN {asin} 处理成功: {title_and_bp}")
        # 在这里，您可以将结果存入数据库或触发AI生成等下一步任务
        return {"asin": asin, "data": title_and_bp}
    except Exception as e:
        logger.error(f"处理ASIN {asin} 失败: {e}")
        raise self.retry(exc=e)


@shared_task(name="atomic.process_discovered_asins")
def process_discovered_asins(asin_list: list[str], process_params: dict):
    """接收ASIN列表，并为它们启动并行的“工人”任务组。"""
    if not asin_list:
        logger.warning("发现的ASIN列表为空，工作流结束。")
        return

    # 使用 group 创建一个任务组，实现并行处理
    job_group = group(
        process_one_asin_task.s(asin=asin, **process_params)
        for asin in asin_list
    )
    job_group.apply_async()
    logger.info(f"已为 {len(asin_list)} 个ASIN成功启动并行处理任务组。")