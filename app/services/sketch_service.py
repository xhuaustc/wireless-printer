import cv2
import numpy as np
import os

class SketchService:
    @staticmethod
    def convert_to_sketch(image_path, output_path, threshold1=50, threshold2=150, blur_size=5):
        """
        将图片转换为简笔画效果
        
        Args:
            image_path (str): 输入图片路径
            output_path (str): 输出图片路径
            threshold1 (int): Canny边缘检测的低阈值
            threshold2 (int): Canny边缘检测的高阈值
            blur_size (int): 高斯模糊的核大小
        """
        try:
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("无法读取图片")

            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 应用高斯模糊来减少噪声
            blurred = cv2.GaussianBlur(gray, (blur_size, blur_size), 0)
            
            # 使用Canny算法检测边缘
            edges = cv2.Canny(blurred, threshold1, threshold2)
            
            # 对边缘进行膨胀，使线条更粗
            kernel = np.ones((2, 2), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=1)
            
            # 创建白色背景
            sketch = np.ones_like(gray) * 255  # 修改为单通道图像
            
            # 将边缘绘制为黑色
            sketch[edges != 0] = 0
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存结果
            success = cv2.imwrite(output_path, sketch)
            if not success:
                raise ValueError("保存图片失败")
            return True
            
        except Exception as e:
            print(f"转换简笔画时出错: {str(e)}")
            return False

    @staticmethod
    def convert_to_sketch_artistic(image_path, output_path):
        """
        将图片转换为更艺术的简笔画效果
        
        Args:
            image_path (str): 输入图片路径
            output_path (str): 输出图片路径
        """
        try:
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("无法读取图片")

            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 反转图像
            inverted = cv2.bitwise_not(gray)
            
            # 应用高斯模糊
            blurred = cv2.GaussianBlur(inverted, (21, 21), 0)
            
            # 反转模糊后的图像
            inverted_blurred = cv2.bitwise_not(blurred)
            
            # 创建素描效果
            sketch = cv2.divide(gray, inverted_blurred, scale=256.0)
            
            # 增强对比度
            sketch = cv2.convertScaleAbs(sketch, alpha=1.2, beta=10)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存结果
            success = cv2.imwrite(output_path, sketch)
            if not success:
                raise ValueError("保存图片失败")
            return True
            
        except Exception as e:
            print(f"转换艺术简笔画时出错: {str(e)}")
            return False 