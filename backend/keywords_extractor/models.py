import uuid
from django.db import models
from django.conf import settings # 推荐使用settings.AUTH_USER_MODEL
# 假设您的Category模型在另外一个叫 'products' 的app中
# from products.models import Category 
# from scraper.models import RawListing

# --- 前置说明 ---
# 为了让此代码段能独立运行，我们先定义依赖的外部模型。
# 在您的真实项目中，请删除下面的Category和RawListing定义，
# 并使用正确的import语句（如上面的注释所示）。


# --- KeywordSeed 模型定义 ---

class KeywordSeed(models.Model):
    """
    关键词种子模型。
    这是AI从原始Listing中提取、分析和结构化后得到的核心数据资产。
    它不仅是生成新Listing的直接输入，也是未来进行数据分析、
    广告优化和关键词趋势跟踪的基础。
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="用于API交互的唯一标识符")
    
    # 核心关联字段
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name="所属用户",
        help_text="实现用户数据的逻辑隔离"
    )
    name = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name="种子名称",
        help_text="为这组关键词起一个易于识别的名称，如 '现代简约风蓝色壁画 - B08H93Z3W5'"
    )
    category = models.ForeignKey(
        'core.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="产品类目",
        help_text="关联到具体的产品类目，便于分类管理和分析"
    )
    source_raw_listing = models.ForeignKey(
        'scraper.RawListing',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="来源原始Listing",
        help_text="追溯该关键词种子是从哪个原始Listing提取的"
    )

    # 核心数据字段
    keywords_data = models.JSONField(
        default=dict,
        verbose_name="结构化关键词数据",
        help_text="由AI提取并结构化的JSON数据，包含分类、搜索量等信息"
    )

    # 标准审计字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "关键词种子"
        verbose_name_plural = "关键词种子库"
        # 确保每个用户下的种子名称是唯一的，这是一个可选的约束
        # unique_together = ['user', 'name']

    def __str__(self):
        return self.name or f"Seed {self.id}"

    def save(self, *args, **kwargs):
        # 如果在创建时没有提供name，自动生成一个
        if not self.name and self.source_raw_listing:
            self.name = f"{self.source_raw_listing.asin}_{self.created_at.strftime('%Y-%m-%d')}"
        super().save(*args, **kwargs)

    # --- Helper Properties (可选，但推荐) ---
    @property
    def title_keywords(self):
        """快速获取标题关键词列表"""
        return self.keywords_data.get('title_keywords', [])

    @property
    def bp_keywords(self):
        """快速获取五点描述关键词列表"""
        return self.keywords_data.get('bp_keywords', [])

    @property
    def review_summary(self):
        """快速获取review summary"""
        return self.source_raw_listing.review_summary