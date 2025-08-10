# core/models.py
from django.db import models
import uuid
# Create your models here.

# ---------- 类目 ------------------------------------------------------
class ActiveCategoryManager(models.Manager):
    """仅返回 is_active=True 的类目，用于前端下拉 / GPT 生成"""

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Category(models.Model):
    """商品大类：壁画、服装、电子等"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=30, unique=True, db_index=True, help_text="类目编码")
    name = models.CharField(max_length=100, help_text="用于在前端和后台展示给用户的名称")
    is_active = models.BooleanField(default=True, help_text="取消勾选后，此分类将不会出现在前端下拉选项中")

    objects = models.Manager()  # 全量
    active_objects = ActiveCategoryManager()  # 仅激活

    class Meta:
        ordering = ["code"]
        verbose_name = "商品类目"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
