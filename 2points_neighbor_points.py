import cv2
import numpy as np
import sys
from scipy.spatial import KDTree

def zip_circlexy(circle_list):
    return [(int(circle[0]), int(circle[1])) for circle in circle_list]

def find_closest_points_kdtree(matrix_points, threshold_distance):
    matrix_points = np.array(matrix_points)
    kdtree = KDTree(matrix_points)
    
    closest_points = []
    
    for i, point in enumerate(matrix_points):
        # 查询距离小于或等于阈值的最近点
        neighbor_indices = kdtree.query_ball_point(point, threshold_distance)
        
        for j in neighbor_indices:
            if i != j:  # 避免与自己比较
                closest_points.append((tuple(point), tuple(matrix_points[j])))
    
    return closest_points

path = sys.argv[1]

# Define the Hough Circle parameters
dp = 1
minDist = 8
param1 = 100
param2 = 10
minRadius = 3
maxRadius = 10

# Create a VideoCapture object to read from the camera
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(path)
ret, frame = cap.read()
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output1.mp4', fourcc, 20.0, (width, height))
distances = []  # 用于存储距离的列表
frame_count = 0

while frame_count < 200:
    # Read a frame from the camera
    ret, frame = cap.read()
    
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    gray_blur = cv2.GaussianBlur(gray, (9, 9), 2)

    _, imgthresh = cv2.threshold(gray_blur, 120, 255, cv2.THRESH_BINARY_INV)

    imgcanny = cv2.Canny(imgthresh, 50, 50)

    # Detect circles using the Hough Circle algorithm
    circles = cv2.HoughCircles(imgcanny, cv2.HOUGH_GRADIENT, dp, minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
    cv2.putText(frame, "Learning the distance between points", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 4)
    # Draw the detected circles on the frame
    if circles is not None:
        points_list = zip_circlexy(circles[0]) if len(circles) > 0 else []
        close_points_set = find_closest_points_kdtree(points_list, 130)
        
        # Calculate distances and store them in the distances list
        for (point1, point2) in close_points_set:

            point1 = (int(point1[0]), int(point1[1]))
            point2 = (int(point2[0]), int(point2[1]))
            cv2.circle(frame, point1, 5, (255, 0, 0), -1)
            cv2.circle(frame, point2, 5, (255, 0, 0), -1)
            cv2.line(frame, point1, point2, (0, 0, 255), 2)

            distance = np.linalg.norm(np.array(point1) - np.array(point2))
            distances.append(distance)

        for (x, y, r) in circles[0]:
            center = (int(x), int(y))  # 转换为整数坐标
            cv2.circle(frame, center, int(r), (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow("Hough Circle Detection", frame)
    out.write(frame)
    frame_count += 1

    # Exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close all windows
cap.release()
cv2.destroyAllWindows()

# Calculate the histogram of distances for the first 100 frames
hist, bin_edges = np.histogram(distances, bins=20)

# Find the bin with the highest frequency
max_bin = np.argmax(hist)
max_bin_range = (bin_edges[max_bin], bin_edges[max_bin + 1])

print(f"Most frequent distance range: {max_bin_range}")

# Create a VideoCapture object to read from the camera again
cap = cv2.VideoCapture(path)

# Find points within the most frequent distance range and with at least two neighbors in that range
neighbor_threshold = 2  # Minimum number of neighbors within the range

# Find points within the most frequent distance range
lower_bound = max_bin_range[0]  # Lower bound of the most frequent range
upper_bound = max_bin_range[1]  # Upper bound of the most frequent range


centerpoint_2neighbor = []

while True:
    # Read a frame from the camera
    ret, frame = cap.read()
    
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    gray_blur = cv2.GaussianBlur(gray, (9, 9), 2)

    _, imgthresh = cv2.threshold(gray_blur, 120, 255, cv2.THRESH_BINARY_INV)

    imgcanny = cv2.Canny(imgthresh, 50, 50)

    # Detect circles using the Hough Circle algorithm
    circles = cv2.HoughCircles(imgcanny, cv2.HOUGH_GRADIENT, dp, minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
    cv2.putText(frame, "centerpoint_2neighbor_Matrix detection", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 4)
    # Find points within the specified distance range
    if circles is not None:
        points_list = zip_circlexy(circles[0]) if len(circles) > 0 else []
        
        for (x, y, r) in circles[0]:
            center = (int(x), int(y))  # 转换为整数坐标
            
            # 寻找指定范围内的近邻点
            close_neighbors = [point for point in points_list if lower_bound <= np.linalg.norm(np.array(point) - np.array(center)) <= upper_bound]
            
            if len(close_neighbors) >= neighbor_threshold:
                cv2.circle(frame, center, int(r), (10, 255, 0), 4)  # Draw in red for points with at least 2 close neighbors
                print(f"Point {center} has at least {len(close_neighbors)} close neighbors")
                with open('center.txt', 'a') as f:
                    f.write(f"Point {center} has at least {len(close_neighbors)} close neighbors")
                
    # Display the resulting frame
    cv2.imshow("Filtered Points", frame)
    out.write(frame)
    # Exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close all windows
out.release()
cap.release()
cv2.destroyAllWindows()