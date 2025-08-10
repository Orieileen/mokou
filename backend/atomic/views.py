# atomic/views.py

from django.http import HttpResponse

from .tasks import discover_asins_task, process_discovered_asins


def start_full_workflow(request):
    """这是最终的工作流启动入口。"""
    discover_params = {
        "url": "https://www.amazon.com/Best-Sellers-Audible-Books-Originals/zgbs/audible/ref=zg_bs_nav_audible_0",
        "parserName": "amzBestSellers",
        "zipcode": "10041",
    }
    
    process_params = {
        "parserName": "amzProductDetail",
        "zipcode": "10041",
    }

    (
        discover_asins_task.s(**discover_params) | 
        process_discovered_asins.s(process_params=process_params)
    ).apply_async()

    return HttpResponse("分布式工作流已正确启动！请检查Celery Worker日志。")