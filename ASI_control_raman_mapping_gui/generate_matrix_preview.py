import numpy as np
import matplotlib.pyplot as plt

def generate_matrix(size, spacing):
    rows, cols = size
    x = np.arange(0, rows * spacing, spacing)
    y = np.arange(0, cols * spacing, spacing)
    X, Y = np.meshgrid(x, y)
    matrix_points = list(zip(X.ravel(), Y.ravel()))
    return matrix_points

def generate_path(matrix_points):
    # 这里你可以实现路径生成算法，例如最短路径算法
    # 这里我简单地按顺序访问点
    path = matrix_points.copy()
    return path

def plot_matrix_and_path(matrix_points, path):
    x, y = zip(*matrix_points)
    plt.scatter(x, y, c='blue', label='Matrix Points')
    
    path_x, path_y = zip(*path)
    plt.plot(path_x, path_y, c='red', label='Path')
    
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.title('Matrix and Path Visualization')
    
    plt.show()

# 设置矩阵大小和点间距
matrix_size = (5, 5)
point_spacing = 2.0

# 生成矩阵点
matrix_points = generate_matrix(matrix_size, point_spacing)

# 生成路径
path = generate_path(matrix_points)

# 绘制矩阵和路径
plot_matrix_and_path(matrix_points, path)
