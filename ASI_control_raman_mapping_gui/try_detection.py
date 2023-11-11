import cv2
import numpy as np

# 加载视频文件
video_capture = cv2.VideoCapture('deal.mp4')

while True:
    ret, frame = video_capture.read()
    
    if not ret:
        break

    # 将帧转换为灰度图像
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 对灰度图像进行二值化处理，根据实际情况调整阈值
    _, binary_frame = cv2.threshold(gray_frame, 100, 255, cv2.THRESH_BINARY)
    
    # 寻找轮廓
    contours, _ = cv2.findContours(binary_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 初始化目标列表
    targets = []
    
    for contour in contours:
        # 根据轮廓面积筛选目标
        if cv2.contourArea(contour) > 50:
            # 计算目标轮廓的最小包围矩形
            rect = cv2.minAreaRect(contour)
            
            # 提取矩形的信息
            center, size, angle = rect
            width, height = size
            
            # 计算绝对坐标，偏转角度和长度
            absolute_x = int(center[0])
            absolute_y = int(center[1])
            rotation_angle = angle
            length = max(width, height)
            
            # 添加目标到列表
            targets.append({
                'center': (absolute_x, absolute_y),
                'angle': rotation_angle,
                'length': length
            })
    
    # 在原始帧上绘制矩形和信息
    for target in targets:
        absolute_x, absolute_y = target['center']
        rotation_angle = target['angle']
        length = target['length']
        
        # 绘制矩形
        rect_points = cv2.boxPoints(((absolute_x, absolute_y), (length, length), rotation_angle))
        rect_points = np.int0(rect_points)
        cv2.drawContours(frame, [rect_points], 0, (0, 255, 0), 2)
        
        # 输出识别的点信息
        print(f'Point: ({absolute_x}, {absolute_y}), Angle: {rotation_angle}, Length: {length}')
    
    # 显示帧
    cv2.imshow('Video', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放视频捕获和关闭窗口
video_capture.release()
cv2.destroyAllWindows()
