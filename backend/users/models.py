# users/models.py
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings

# ---------- 自定义 Manager ------------------------------------------------
class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email 地址不能为空")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("超级用户必须设置 is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("超级用户必须设置 is_superuser=True")

        return self.create_user(email, password, **extra_fields)


# ---------- 自定义 User ----------------------------------------------------
class CustomUser(AbstractUser):
    """
    以 Email 作为唯一登录标识，主键改 UUID。
    """

    # 移除 username 字段
    username = None

    # 唯一 Email
    email = models.EmailField(
        "email address",
        unique=True,
        error_messages={"unique": "此电子邮件地址已被注册。"},
    )

    # UUID 主键
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # 核心设置
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # createsuperuser 只要求 email & password

    # 绑定自定义 Manager
    objects = CustomUserManager()

    class Meta:
        db_table = "users"
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """
    存储用户的业务相关信息和配置
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,     # 使用 OneToOneField 与 User 模型关联
        on_delete=models.CASCADE,
        primary_key=True,             # 直接使用 user 的主键作为自己的主键，性能更好
        related_name='profile'        # 方便通过 user.profile 反向查询
    )

    # --- 订阅与计费 (直接关系到项目盈利) ---
    PLAN_CHOICES = [
        ('free', '免费版'),
        ('pro', '专业版'),
        ('enterprise', '企业版'),
    ]
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free', verbose_name="订阅计划")
    subscription_status = models.CharField(max_length=20, default='active', verbose_name="订阅状态") # e.g., active, canceled, past_due
    
    # --- 使用额度 (Quota) ---
    # 我们可以根据 plan 类型，在业务逻辑中设定不同额度的默认值
    listing_generation_quota = models.PositiveIntegerField(default=10, verbose_name="Listing生成额度")
    api_call_quota = models.PositiveIntegerField(default=1000, verbose_name="API调用额度")

    # --- 其他业务信息 ---
    company_name = models.CharField(max_length=100, blank=True, verbose_name="公司名称")
    amazon_seller_id = models.CharField(max_length=50, blank=True, verbose_name="亚马逊卖家ID")

    class Meta:
        db_table = 'user_profiles'
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'

    def __str__(self):
        return self.user.email