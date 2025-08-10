from django.contrib import admin
from django.utils.html import format_html

from .models import (
    MainImageTemplate,
    SceneImageTemplate,
    SynthesizedMainImage,
    SynthesizedSceneImage,
)

# 场景图模板
@admin.register(SceneImageTemplate)
class SceneImageTemplateAdmin(admin.ModelAdmin):
    # 在列表页显示的字段
    list_display = ('name', 'category', 'aspect_ratio', 'is_active', 'template_type')
    
    # 在右侧显示的筛选器
    list_filter = ('category', 'aspect_ratio', 'is_active')
    
    # 顶部显示的搜索框，可按名称搜索
    search_fields = ('name',)
    
    # 【性能优化】一次性加载关联的category，避免N+1查询问题
    list_select_related = ('category',)
    
    # 在编辑页对字段进行分组，使界面更清晰
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'category', 'aspect_ratio', 'is_active')
        }),
        ('图像与坐标', {
            'fields': ('background_image', 'target_vertices')
        }),
        ('排序', {
            'fields': ('template_type',)
        }),
    )

# 合成的场景图
@admin.register(SynthesizedSceneImage)
class SynthesizedSceneImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_listing', 'scene_template', 'status', 'created_at', 'image_preview')
    list_filter = ('status', 'scene_template__category', 'scene_template__aspect_ratio') # 可以按模板的属性进行筛选
    search_fields = ('source_listing__id',) # 按Listing ID搜索
    list_select_related = ('source_listing', 'scene_template')
    
    # 【数据保护】这些字段都是程序生成的，设为只读以防止误操作
    readonly_fields = ('source_listing', 'scene_template', 'display_order', 
                       'final_image', 'status', 'created_at', 'updated_at', 'image_preview')

    # 在编辑页添加图片预览功能
    def image_preview(self, obj):
        if obj.final_image:
            return format_html('<a href="{0}" target="_blank"><img src="{0}" width="150" /></a>', obj.final_image.url)
        return "无图片"
    image_preview.short_description = '图片预览'

    def has_add_permission(self, request):
        # 禁止在后台手动添加合成图片记录
        return False

# 主图模板
@admin.register(MainImageTemplate)
class MainImageTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'aspect_ratio', 'is_active')
    list_filter = ('category', 'aspect_ratio', 'is_active')
    search_fields = ('name',)
    list_select_related = ('category',)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'category', 'aspect_ratio', 'is_active')
        }),
        ('图像与坐标', {
            'fields': ('template_image', 'target_vertices')
        }),
    )

# 合成的场景图
@admin.register(SynthesizedMainImage)
class SynthesizedMainImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_listing', 'main_template', 'status', 'created_at', 'image_preview')
    list_filter = ('status', 'main_template__category')
    search_fields = ('source_listing__id',)
    list_select_related = ('source_listing', 'main_template')
    
    readonly_fields = ('source_listing', 'main_template', 'final_image', 
                       'status', 'created_at', 'updated_at', 'image_preview')

    def image_preview(self, obj):
        if obj.final_image:
            return format_html('<a href="{0}" target="_blank"><img src="{0}" width="150" /></a>', obj.final_image.url)
        return "无图片"
    image_preview.short_description = '图片预览'

    def has_add_permission(self, request):
        # 禁止在后台手动添加合成主图记录
        return False