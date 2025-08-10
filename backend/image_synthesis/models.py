# image_synthesis/models.py

from django.core.validators import MinValueValidator  # 导入验证器
from django.db import models


# 场景图模板模型
class SceneImageTemplate(models.Model):
    """
    专门用于存储【场景图】的模板。
    """
    ASPECT_RATIO_CHOICES = [
        ('1:1', '1:1'),
        ('3:2', '3:2'),
        ('2:3', '2:3'),
        ('4:3', '4:3'),
        ('3:4', '3:4'),
        ('2:1', '2:1'),
        ('1:2', '1:2'),
    ]
    # 关联产品大类 (壁画, 服装, etc.)
    # 假设您的Category模型在 'core' app 中
    category = models.ForeignKey('core.Category', on_delete=models.CASCADE)

    aspect_ratio = models.CharField(
        max_length=10,
        choices=ASPECT_RATIO_CHOICES,
        help_text="画框的宽高比",
        db_index=True  # 为该字段添加数据库索引，以优化查询速度
    )

    name = models.CharField(
        max_length=255, 
        help_text="模板的描述性名称, e.g., '客厅沙发背景墙-现代风'"
    )

    # 模板类型字段，只用于排序
    template_type = models.PositiveSmallIntegerField(
        default=1, 
        help_text="场景图的展示顺序 (例如 1-5)，数字越小越靠前。",
        validators=[
            MinValueValidator(1) # 【关键约束】确保这个值必须大于等于1，从根本上杜绝了“0=主图”的可能性。
        ]
    )

    background_image = models.ImageField(
        upload_to='scene_templates/',
        help_text="用作背景的场景图片"
    )

    target_vertices = models.JSONField(
        help_text="目标区域四顶点坐标 [x1, y1, x2, y2, x3, y3, x4, y4]"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="是否启用此模板"
    )

    def __str__(self):
        return f"[场景图] {self.category.name} - {self.name}"

    class Meta:
        # 建议为模型指定一个更易读的名称，方便在后台显示
        verbose_name = "场景图模板"
        verbose_name_plural = "场景图模板"


# 合成的场景图模型
class SynthesizedSceneImage(models.Model):
    """
    存储由 SceneImageTemplate 生成的最终【场景图】。
    """
    # 反向关联到具体的Listing
    # 假设您的Listing模型在 'lst_generate' app 中
    source_listing = models.ForeignKey(
        'lst_generate.Listing', 
        related_name='synthesized_scene_images', # 关联名称也更明确
        on_delete=models.CASCADE
    )

    # 外键指向 SceneImageTemplate 模型
    scene_template = models.ForeignKey(
        SceneImageTemplate, 
        on_delete=models.PROTECT,
        help_text="引用了哪个场景图模板生成"
    )

    # 图片在亚马逊中的顺序，只表示场景图的顺序
    display_order = models.PositiveSmallIntegerField(
        default=1,
        help_text="场景图的展示顺序，由模板的template_type决定"
    )

    final_image = models.ImageField(upload_to='synthesized_images/scenes/%Y/%m/%d/') # 建议增加scenes子目录

    # 状态追踪，用于Celery任务管理
    STATUS_CHOICES = [
        ('PENDING', '待处理'),
        ('PROCESSING', '处理中'),
        ('COMPLETED', '已完成'),
        ('FAILED', '处理失败'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order'] # 按顺序排列
        verbose_name = "合成的场景图"
        verbose_name_plural = "合成的场景图"

    def __str__(self):
        return f"scene image for {self.source_listing.id} (display: {self.display_order})"


# 主图模板模型
class MainImageTemplate(models.Model):
    """
    专门用于存储【主图】的模板。
    它包含一张背景图（如带阴影的白底产品）和用于透视变换的顶点坐标。
    """
    ASPECT_RATIO_CHOICES = [
        ('1:1', '1:1'),
        ('3:2', '3:2'),
        ('2:3', '2:3'),
        ('4:3', '4:3'),
        ('3:4', '3:4'),
        ('2:1', '2:1'),
        ('1:2', '1:2'),
    ]

    # 关联产品大类
    category = models.ForeignKey(
        'core.Category', # 确保指向您的Category模型
        on_delete=models.CASCADE
    )

    aspect_ratio = models.CharField(
        max_length=10,
        choices=ASPECT_RATIO_CHOICES,
        help_text="画框的宽高比",
        db_index=True  # 为该字段添加数据库索引，以优化查询速度
    )

    name = models.CharField(
        max_length=255, 
        help_text="白底图模板的描述性名称, e.g., '3:2/2:1/...'"
    )

    # 主图的背景/模板图片
    template_image = models.ImageField(
        upload_to='main_image_templates/',
        help_text="请上传带阴影/光泽等的白底产品图作为模板"
    )

    # 【核心】用于透视变换的顶点坐标
    # 我们使用JSONField来灵活存储6个或更多顶点
    target_vertices = models.JSONField(
        help_text="目标区域八顶点坐标 [x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6, x7, y7, x8, y8]"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="是否启用此主图模板"
    )

    def __str__(self):
        return f"[主图] {self.category.name} - {self.name}"

    class Meta:
        verbose_name = "主图模板"
        verbose_name_plural = "主图模板"


# 合成的主图模型
class SynthesizedMainImage(models.Model):
    """
    存储由 MainImageTemplate 和 pattern_image 生成的最终【主图】。
    """
    # 关联到具体的Listing
    source_listing = models.OneToOneField(
        'lst_generate.Listing', # 确保指向您的Listing模型
        related_name='synthesized_main_image', # 使用OneToOne确保一个Listing只有一个主图
        on_delete=models.CASCADE
    )

    # 引用了哪个主图模板生成
    main_template = models.ForeignKey(
        MainImageTemplate, 
        on_delete=models.PROTECT,
        help_text="引用了哪个主图模板生成"
    )

    # 最终生成的图片文件
    final_image = models.ImageField(
        upload_to='synthesized_images/main/%Y/%m/%d/'
    )

    # 状态追踪，用于Celery任务管理
    STATUS_CHOICES = [
        ('PENDING', '待处理'),
        ('PROCESSING', '处理中'),
        ('COMPLETED', '已完成'),
        ('FAILED', '处理失败'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PENDING'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"主图 for {self.source_listing.id}"

    class Meta:
        verbose_name = "合成的主图"
        verbose_name_plural = "合成的主图"