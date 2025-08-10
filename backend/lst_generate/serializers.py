# lst_generate/serializers.py
from rest_framework import serializers

from image_synthesis.models import (
    SynthesizedMainImage,
    SynthesizedSceneImage,
)

from .models import KeywordSeed, Listing


class KeywordSeedSerializer(serializers.ModelSerializer):
    """【子序列化器】只序列化 KeywordSeed 模型的关键信息。"""
    class Meta:
        model = KeywordSeed
        fields = ['id', 'keywords_data']


class SynthesizedMainImageSerializer(serializers.ModelSerializer):
    """【子序列化器】只序列化最终生成的主图信息。"""
    class Meta:
        model = SynthesizedMainImage
        fields = ['id', 'final_image', 'status']


class SynthesizedSceneImageSerializer(serializers.ModelSerializer):
    """【子序列化器】只序列化最终生成的场景图信息。"""
    class Meta:
        model = SynthesizedSceneImage
        fields = ['id', 'final_image', 'status', 'display_order']


class ListingDetailSerializer(serializers.ModelSerializer):
    """
    一个全面的Listing序列化器，通过处理外键关联来聚合展示一个Listing的所有信息。
    """
    
    # --- 处理正向外键关联 (Listing -> KeywordSeed) ---
    # 序列化器中的字段名 'keyword_seed' 必须与Listing模型中的字段名完全一致。
    keyword_seed = KeywordSeedSerializer(read_only=True)

    # --- 处理反向一对一关联 (Listing <- SynthesizedMainImage) ---
    # 序列化器中的字段名 'synthesized_main_image' 必须与SynthesizedMainImage模型中
    # OneToOneField定义的 related_name 完全一致。
    synthesized_main_image = SynthesizedMainImageSerializer(read_only=True)

    # --- 处理反向一对多关联 (Listing <- SynthesizedSceneImage) ---
    # 序列化器中的字段名 'synthesized_scene_images' 必须与SynthesizedSceneImage模型中
    # ForeignKey定义的 related_name 完全一致。
    # many=True 是处理“一对多”关系的关键。
    synthesized_scene_images = SynthesizedSceneImageSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        # 在fields中列出所有需要展示的字段，包括模型自身的字段和上面定义的嵌套字段
        fields = [
            'id',
            'title',
            'bullet_points',
            'description',
            'pattern_image',
            'status',
            'user',
            'keyword_seed',  # 正向外键关联
            'synthesized_main_image', # 反向一对一关联
            'synthesized_scene_images', # 反向一对多关联
            'created_at',
        ]