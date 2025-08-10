# image_synthesis/services/MainSynthesizer.py

import logging
import cv2
import numpy as np
from django.core.files.base import ContentFile
from django.db.models import ImageField

from lst_generate.models import Listing
from image_synthesis.models import MainImageTemplate, SynthesizedMainImage

logger = logging.getLogger(__name__)

class MainSynthesizer:
    def __init__(self, listing_id: int):
        try:
            self.listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            raise ValueError(f"ID为 {listing_id} 的Listing不存在。")
        
        if not self.listing.pattern_image:
            raise ValueError(f"Listing {listing_id} 没有关联的源图案 (pattern_image)。")

    def synthesize_main_image(self, template_name: str, left_ratio: float = 0.1, shadow_strength: float = 0.4):
        """
        主调用函数：为该Listing合成唯一的主图。
        根据指定的template_name来精确查找并使用一个主图模板。

        :param template_name: 必须提供要使用的主图模板的精确名称 (e.g., "1:1", "2:3")。
        :param left_ratio: 左侧包裹的分割比例。
        :param shadow_strength: 侧面阴影的强度。
        """
        logger.info(f"开始为Listing {self.listing.id} 合成主图，要求使用模板: '{template_name}'...")
        category = self.listing.category

        # 1. 根据模板名称精确查找主图模板
        main_template = MainImageTemplate.objects.filter(
            category=category,
            is_active=True,
            name=template_name  # <-- 使用传入的名称进行精确过滤
        ).first()

        if not main_template:
            error_msg = f"错误：找不到任何为品类 '{category.name}' 设置的、名称为 '{template_name}' 的、可用的主图模板。"
            logger.error(error_msg)
            raise MainImageTemplate.DoesNotExist(error_msg)

        # 2. 从数据库模板中获取背景图和顶点坐标
        template_img = self._read_image_from_field(main_template.template_image)
        template_h, template_w = template_img.shape[:2]
        
        # 动态获取顶点坐标
        vertices = main_template.target_vertices
        if not isinstance(vertices, list) or len(vertices) != 16:
            raise ValueError("顶点坐标必须是一个包含16个元素的列表。")
        front_dst_points = np.array(vertices.reshape(8, 2)[:4], dtype=np.float32)
        left_dst_points = np.array(vertices.reshape(8, 2)[4:], dtype=np.float32)

        # 3. 从Listing中获取源图案
        pattern_img = self._read_image_from_field(self.listing.pattern_image)

        # 4. 切分图案
        left_part, right_part = self._split_pattern(pattern_img, left_ratio)
        
        # 5. 应用透视变换
        right_transformed, right_mask = self._apply_perspective(right_part, front_dst_points, (template_w, template_h))
        left_transformed, left_mask = self._apply_perspective(left_part, left_dst_points, (template_w, template_h))

        # 6. 混合图案到模板
        result = self._blend_image(template_img, right_transformed, right_mask)
        result = self._blend_image(result, left_transformed, left_mask)

        # 7. 添加阴影
        result = self._apply_shadow(result, left_dst_points, strength=shadow_strength)
        
        # 8. 保存结果到模型
        self._save_image_to_model(result, main_template)
        
        logger.info(f"Listing {self.listing.id} 的主图合成完成！")

    # --- 以下为辅助方法 ---

    def _split_pattern(self, pattern: np.ndarray, left_ratio: float):
        # ... 此方法保持不变 ...
        h, w = pattern.shape[:2]
        split_x = int(w * left_ratio)
        left_part = pattern[:, :split_x]
        right_part = pattern[:, split_x:]
        return left_part, right_part

    def _apply_perspective(self, image: np.ndarray, dst_points: np.ndarray, template_size: tuple) -> tuple:
        # ... 此方法保持不变 ...
        h, w = image.shape[:2]
        template_w, template_h = template_size
        src_points = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype=np.float32)
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        transformed = cv2.warpPerspective(image, matrix, (template_w, template_h))
        mask = np.zeros((template_h, template_w), dtype=np.uint8)
        cv2.fillPoly(mask, [dst_points.astype(np.int32)], 255)
        return transformed, mask

    def _blend_image(self, template: np.ndarray, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        # ... 此方法保持不变 ...
        result = template.copy()
        result[mask == 255] = image[mask == 255]
        return result

    def _apply_shadow(self, image: np.ndarray, shadow_points: np.ndarray, strength: float) -> np.ndarray:
        # ... 此方法保持不变 ...
        shadow_mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.fillPoly(shadow_mask, [shadow_points.astype(np.int32)], 255)
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv_image)
        v_float = v.astype(np.float32)
        v_float[shadow_mask == 255] *= (1 - strength)
        v_final = np.clip(v_float, 0, 255).astype(np.uint8)
        final_hsv = cv2.merge([h, s, v_final])
        return cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

    def _read_image_from_field(self, image_field: ImageField) -> np.ndarray:
        """【风格对齐】从Django ImageField读取图像为OpenCV格式。"""
        with image_field.open('rb') as f:
            image_data = f.read()
        image_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"无法从ImageField解码图片: {image_field.name}")
        return image

    def _save_image_to_model(self, image_array: np.ndarray, template: MainImageTemplate):
        """【风格对齐】将OpenCV图像保存到SynthesizedMainImage模型。"""
        success, buffer = cv2.imencode('.jpg', image_array, [cv2.IMWRITE_JPEG_QUALITY, 90])
        if not success:
            raise IOError("Could not encode image to JPEG.")
        
        file_name = f'listing_{self.listing.id}_main_image.jpg'
        content_file = ContentFile(buffer.tobytes(), name=file_name)

        # 使用 get_or_create 确保一个Listing只有一个主图记录，更加健壮
        SynthesizedMainImage.objects.update_or_create(
            source_listing=self.listing,
            defaults={
                'main_template': template,
                'final_image': content_file,
            }
        )