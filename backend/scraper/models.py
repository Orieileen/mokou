# scraper/models.py
import uuid

from django.conf import settings  # 用于关联User模型
from django.db import models
from django.utils.translation import gettext_lazy as _


class RawListing(models.Model):
    """
    存储通过爬虫抓取或运营导入的原始、未经处理的ASIN Listing文案。
    这张表是所有AI生成内容的源头，只做数据备份，不直接面向前端展示。
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # 关键外部关联
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='raw_listings',
        verbose_name="所属用户"
    )
    category = models.ForeignKey(
        'core.Category', # 关联到我们刚刚完成的core.Category模型
        on_delete=models.PROTECT,
        related_name='raw_listings',
        verbose_name="归属类目"
    )

    # 核心数据字段
    asin = models.CharField(_("ASIN"), max_length=20, db_index=True)
    source = models.CharField(_("数据来源"), max_length=50, default='amazon_us', help_text="例如: amazon_us, amazon_jp(哪个平台_哪个站点)")
    
    # 爬取到的原始文案
    # 使用 TextField 是因为五点描述等内容可能很长
    title = models.TextField(_("原始标题"), blank=True)
    bullet_points = models.JSONField(_("原始五点"), default=list, blank=True, help_text="存储原始的五点描述列表")

    # 爬取到的review summary
    review_summary = models.TextField(_("review summary"), blank=True)

    # 时间戳
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "原始Listing"
        verbose_name_plural = verbose_name
        # 确保同一个用户对于同一个ASIN只应有一条原始记录，防止重复爬取同一asin
        unique_together = ('user', 'asin')

    def __str__(self):
        return f"{self.asin} - {self.user.username}"