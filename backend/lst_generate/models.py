# lst_generate/models.py
import uuid
from django.db import models
from django.conf import settings # 用于关联 User 模型
# 假设您的模型位于以下应用中
# from categories.models import Category
# from keywords.models import KeywordSeed

class Listing(models.Model):
    """
    存储由 AI 生成的、图文并茂的亚马逊 Listing。
    这是系统的核心产出，是所有后续操作（如图片合成、发布）的基础。
    """
    
    # --- 核心关系与归属 ---
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="用于API交互和内部引用的唯一ID")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="listings",
        help_text="数据归属的用户，实现逻辑隔离"
    )
    keyword_seed = models.ForeignKey( # 使用Listing.object.get().keyword_seed可以获取到keyword_seed
        'keywords_extractor.KeywordSeed',
        on_delete=models.SET_NULL, # 关键：即使种子被删，Listing也应保留
        null=True, 
        blank=True, 
        related_name="generated_listings", # 反向关联到 KeywordSeed 模型，使用KeywordSeed.object.get().generated_listings.all() 获取所有生成的Listing，其中generated_listings是related_name的名称
        help_text="追溯生成此Listing所用的关键词种子"
    )
    category = models.ForeignKey(
        'core.Category',
        on_delete=models.PROTECT, # 防止意外删除正在使用的分类
        related_name="listings",
        help_text="此Listing所属的产品大类，用于驱动图片合成模板选择"
    )

    # --- AI 生成的核心内容 ---
    title = models.CharField(max_length=255, help_text="new_title")
    bullet_points = models.JSONField(default=list, help_text="new_bullet_points(JSON)")
    description = models.TextField(blank=True, help_text="new_product_description")
    pattern_image = models.ImageField(
        upload_to='patterns/%Y/%m/%d/', 
        help_text="pattern_image"
    )

    # --- 状态与工作流管理 ---
    class ListingStatus(models.TextChoices):
        DRAFT = 'DRAFT', '草稿'
        PENDING_SYNTHESIS = 'PENDING_SYNTHESIS', '待图片合成'
        READY_TO_PUBLISH = 'READY_TO_PUBLISH', '待发布'
        PUBLISHED = 'PUBLISHED', '已发布'
        ARCHIVED = 'ARCHIVED', '已归档'

    status = models.CharField(
        max_length=20,
        choices=ListingStatus.choices,
        default=ListingStatus.PENDING_SYNTHESIS, # 默认创建后就进入待合成状态
        db_index=True,
        help_text="驱动Celery工作流的核心状态字段"
    )

    # --- 扩展与优化功能字段 (为未来做准备) ---
    quality_score = models.IntegerField(null=True, blank=True, help_text="Listing质量的AI评分")
    optimization_suggestions = models.JSONField(default=list, blank=True, help_text="AI提供的优化建议")
    version = models.PositiveIntegerField(default=1, help_text="版本号，用于支持重新生成或A/B测试")
    amazon_asin = models.CharField(max_length=20, blank=True, null=True, unique=True, help_text="成功发布到亚马逊后回填的ASIN")


    # --- 时间戳 ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "AI 生成的 Listing"
        verbose_name_plural = verbose_name
        db_table = "ai_listings" # 自定义数据库表名，更清晰

    def __str__(self):
        return f"{self.title[:50]}... ({self.get_status_display()})"