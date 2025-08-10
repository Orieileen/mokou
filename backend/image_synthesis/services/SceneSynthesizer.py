# image_synthesis/services/SceneSynthesizer.py
import logging

import cv2
import numpy as np
from django.core.files.base import ContentFile
from django.db.models import ImageField

from lst_generate.models import Listing
from image_synthesis.models import SceneTemplate, SynthesizedImage

logger = logging.getLogger(__name__)

class SceneSynthesizer:
    def __init__(self, listing_id: int):
        try:
            self.listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            raise ValueError(f"ID为 {listing_id} 的Listing不存在。")
        
        if not self.listing.pattern_image:
            raise ValueError(f"Listing {listing_id} 没有关联的源图案 (pattern_image)。")

    def synthesize_all_scenes(self, aspect_ratio: str, num_scene: int = 4):
        """
        主调用函数：为该Listing生成【指定数量】的场景图。
        :param num_scene: 需要生成的场景图数量，默认为4。
        """
        category = self.listing.category
        # --- 第一步：随机获取N张场景图模板 (template_type > 0) ---
        templates_to_process = list(SceneTemplate.objects.filter(
            category=category,
            aspect_ratio=aspect_ratio,
            is_active=True,
            template_type__gt=0  # __gt 表示 "greater than" (大于)
        ).order_by('?').distinct()[:num_scene])
        # .order_by('?') 在某些数据库（如PostgreSQL）上性能较好，但在大型表上可能较慢。如果性能是大问题，可以考虑其他随机选取策略。
        if not templates_to_process:
            raise ValueError(f"没有找到任何为品类 '{category.name}' 设置的、宽高比为 '{aspect_ratio}' 的、可用的场景图模板。")

        # --- 第二步：开始处理选定的模板列表 ---
        logger.info(f"为Listing {self.listing.id} 选定了 {len(templates_to_process)} 个模板进行处理...")
        
        pattern_img = self._read_image_from_field(self.listing.pattern_image)

        for template in templates_to_process:
            self.synthesize_single_image(template, pattern_img)

        logger.info("所有选定模板处理完毕。")

    def synthesize_single_image(self, template: SceneTemplate, pattern_img: np.ndarray):
        """为单个模板生成一张合成图"""
        logger.info(f"Synthesizing for Listing {self.listing.id} with Template {template.name}...")
        
        # 1. 读取背景图
        background_img = self._read_image_from_field(template.background_image)

        # 2. 定义源和目标坐标
        h, w = pattern_img.shape[:2]
        src_points = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32)
        vertices = template.target_vertices
        if not isinstance(vertices, list) or len(vertices) != 8:
            raise ValueError("顶点坐标必须是一个包含8个元素的列表。")
        dst_points = np.array(vertices.reshape(4, 2), dtype=np.float32)

        # 3. 计算透视变换矩阵并应用
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        warped_pattern = cv2.warpPerspective(pattern_img, matrix, (background_img.shape[1], background_img.shape[0]))

        # 4. 创建蒙版并合成
        # (这是一个简化的合成，实际可能需要处理透明度)
        mask = cv2.cvtColor(warped_pattern, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)
        
        # 将背景中对应区域挖空
        background_masked = cv2.bitwise_and(background_img, background_img, mask=cv2.bitwise_not(mask))
        
        # 将变换后的图案与背景合并
        final_img = cv2.add(background_masked, warped_pattern)
        
        # 5. 保存结果到模型
        self._save_image_to_model(final_img, template)
        logger.info(f"Synthesis complete for Listing {self.listing.id} with Template {template.name}.")

    def _read_image_from_field(self, image_field: ImageField):
        """读取ImageField图像并转换为OpenCV格式"""
        with image_field.open('rb') as f:
            image_data = f.read()
            image_array = np.frombuffer(image_data, np.uint8)
            # 将ndarray转换为BGR格式图像
            return cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    def _save_image_to_model(self, image_array: np.ndarray, template: SceneTemplate):
        """将OpenCV图像保存到SynthesizedImage模型"""
        # 使用OpenCV将numpy数组格式的图像编码为JPEG格式
        # 参数说明：
        #'.jpg'：指定输出格式为JPEG
        #image_array：待编码的OpenCV图像（numpy数组）
        #[cv2.IMWRITE_JPEG_QUALITY, 90]：设置JPEG压缩质量为90（0-100，数值越高质量越好，文件越大）
        # 返回值：
        #success：布尔值，表示编码是否成功
        #buffer：编码后的图像数据（numpy一维数组二进制，需buffer.tobytes()转为bytes得到可以写入磁盘或存入 Django ImageField 的图片二进制内容）
        success, buffer = cv2.imencode('.jpg', image_array, [cv2.IMWRITE_JPEG_QUALITY, 90])
        if not success:
            raise IOError("Could not encode image to JPEG.")

        # 创建Django ContentFile
        # buffer.tobytes(): cv2.imencode 返回的 buffer 是一个NumPy数组，.tobytes() 方法将其转换成一个标准的Python bytes 对象。
        # content_file = ContentFile(...): 这是Django提供的一个神奇工具。它接收一个 bytes 对象和一个 name，然后将它们“伪装”成一个文件对象。这个 content_file 变量现在可以像一个从用户表单上传的文件一样被Django处理。
        file_name = f'listing_{self.listing.id}_template_{template.id}.jpg'
        content_file = ContentFile(buffer.tobytes(), name=file_name)

        # 创建并保存模型实例
        SynthesizedImage.objects.create(
            source_listing=self.listing,
            scene_template=template,
            display_order=template.template_type,
            final_image=content_file,
        )