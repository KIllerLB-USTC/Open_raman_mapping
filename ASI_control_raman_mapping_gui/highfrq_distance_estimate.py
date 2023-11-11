import cv2
import numpy as np
import sys
from scipy.spatial import KDTree
import matplotlib.pyplot as plt

def get_neighbors(point, matrix_points,point_spacing):
    neighbors = []
    for dx, dy in [(0, point_spacing), (point_spacing, 0), (0, -point_spacing), (-point_spacing, 0)]:
        neighbor = (point[0] + dx, point[1] + dy)
        if neighbor in matrix_points:
            neighbors.append(neighbor)
    return neighbors

def zip_circlexy(circle_list):
    return [(circle[0], circle[1]) for circle in circle_list]

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
param1 = 120
param2 = 10
minRadius = 1
maxRadius = 10

distances = []
# Create a VideoCapture object to read from the camera
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(path)
 # Read a frame from the camera
ret, frame = cap.read()

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (width, height))

while True:
    # Read a frame from the camera
    ret, frame = cap.read()
    
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

   
    # Apply Gaussian blur to reduce noise
    gray_blur = cv2.GaussianBlur(gray, (9, 9), 2)

    _, imgthresh = cv2.threshold(gray_blur, 120, 255, cv2.THRESH_BINARY_INV)

    imgcanny = cv2.Canny(imgthresh,50,50)

    # Detect circles using the Hough Circle algorithm
    circles = cv2.HoughCircles(imgcanny, cv2.HOUGH_GRADIENT, dp, minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)

    # Draw the detected circles on the frame
    if circles is not None:
        points_list = zip_circlexy(circles[0]) if len(circles) > 0 else []
        close_points_set = find_closest_points_kdtree(points_list, 125)
        print(close_points_set)
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
        for (point1, point2) in close_points_set:
            point1 = (int(point1[0]), int(point1[1]))
            point2 = (int(point2[0]), int(point2[1]))
            cv2.circle(frame, point1, 5, (255, 0, 0), -1)
            cv2.circle(frame, point2, 5, (255, 0, 0), -1)
            cv2.line(frame, point1, point2, (0, 0, 255), 2)

            distance = np.linalg.norm(np.array(point1) - np.array(point2))
            distances.append(distance)
            print(f"Distance between point1 {point1} and point2 {point2}: {distance}")
    # Display the resulting frame
    cv2.imshow("close set Detection", frame)
    out.write(frame)

    # Exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close all windows
cap.release()
out.release()
cv2.destroyAllWindows()

hist, bin_edges = np.histogram(distances, bins=10)

max_bin = np.argmax(hist)
max_bin_range = (bin_edges[max_bin], bin_edges[max_bin + 1])

print(f"Max bin: {max_bin_range}")

plt.hist(distances, bins=20, color='blue', alpha=0.7, rwidth=0.85)
plt.xlabel('Distance')
plt.ylabel('Frequency')
plt.title('Distance Histogram')
plt.grid(axis='y', alpha=0.75)
plt.show()
