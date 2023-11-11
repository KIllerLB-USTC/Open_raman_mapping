import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

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

def plot_matrix_and_path(matrix_points, path, start, end,point_spacing=0):
    plt.clf()
    marker_size = point_spacing * 4
    x, y,_ = zip(*matrix_points)
    plt.scatter(x, y, c='blue', label='Matrix Points')
    
    path_x, path_y,_ = zip(*path)
    plt.plot(path_x, path_y, c='red', label='Path')
    plt.gca().invert_yaxis()
    # 添加起始点和终点的标签和文字
    plt.scatter(start[0], start[1], c='green', marker='o',s=marker_size, label='Start')
    plt.text(start[0], start[1], 'Start', fontsize=12, ha='right')
    
    plt.scatter(end[0], end[1], c='purple', marker='*',s=marker_size, label='End')
    plt.text(end[0], end[1], 'End', fontsize=12, ha='right')
    
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.title('Matrix and Path Visualization')
    
    plt.show()

    
def draw_the_whole_map(points_list):
    path = generate_path(points_list)
    start_point = points_list[0]
    end_point = points_list[-1]
    plot_matrix_and_path(points_list,path,start_point,end_point)
    
def matrix_move_to_origin(points_list):
    substact_point = points_list[0]
    substact_point_x = substact_point[0]
    substact_point_y = substact_point[1]
    matrix_points_original = [(x-substact_point_x,y-substact_point_y,z) for x,y,z  in points_list]
    return matrix_points_original

def write_infile_map_matrix(points_list):
    with open('scanning_points.txt', 'w') as f:
        for point in points_list:
            f.write(f"{point}\n")
    
def read_list_from_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        # 去除每行末尾的换行符
        lines = [line.strip() for line in lines]
        # 将每行转换为列表元素
        newlst = [eval(line) for line in lines]
    return newlst
# if input('Imput the array here? (y/n): ') == 'y':
#     matrix_points = [(219, 544, 2), (244, 526, 4), (204, 518, 5), (183.74748624527044, 495.03817534065337, 6), (166.12122936790564, 470.5572630109801, 7), (226.42637475983892, 501.48119289154, 8), (208.80011788247415, 477.0002805618667, 9), (191.17386100510936, 452.5193682321934, 10), (269.10526327440743, 507.92421044242667, 11), (251.47900639704264, 483.4432981127533, 12), (233.85274951967784, 458.96238578308004, 13), (216.22649264231308, 434.4814734534067, 14), (294.15789491161115, 489.88631566363995, 15), (276.5316380342464, 465.40540333396666, 16), (258.90538115688156, 440.9244910042934, 17), (241.2791242795168, 416.44357867462, 18), (319.21052654881487, 471.8484208848533, 19), (301.5842696714501, 447.36750855518, 20), (283.9580127940853, 422.88659622550665, 21), (266.3317559167205, 398.40568389583336, 22)]
#     print(matrix_points)
# else:
#     matrix_points = read_list_from_file('points_use.txt')

# matrix_points_original = matrix_move_to_origin(matrix_points)
# draw_the_whole_map(matrix_points_original)

# # Ask user if they want to execute the output function
# user_input = input("Do you want to execute the output function? (y/n): ")
# if user_input == 'y':
#     write_infile_map_matrix(matrix_points_original)



