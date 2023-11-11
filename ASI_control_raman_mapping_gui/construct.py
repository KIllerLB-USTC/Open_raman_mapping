
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import generate_path_and_output as gpo
from pypylon import pylon
import cv2
import ASI_control as asi
import serial
import serial.tools.list_ports
import time
import threading
import gc

class App:
    def __init__(self, master,ASI_control):
        self.camera_updated_event = threading.Event()
        self.ASI = ASI_control

        self.master = master
        self.master.title("Camera Viewer")

        # Create a frame for the canvases and pack it on the left
        self.canvas_frame = tk.Frame(self.master)
        self.canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create the left canvas for drawing
        self.canvas = tk.Canvas(self.canvas_frame, width=400, height=300, bg='black')
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Create the right canvas for the camera view
        self.camera_canvas = tk.Canvas(self.canvas_frame, width=400, height=300, bg='black')
        self.camera_canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Create a frame for the buttons and pack it below the canvas frame
        self.button_frame = tk.Frame(self.master,width=600, height=400)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        self.select_draw_frame = tk.Frame(self.master,width=600, height=400)
        self.select_draw_frame.pack(side=tk.TOP, fill=tk.X)

        self.matrix_frame = tk.Frame(self.master,width=600, height=400)
        self.matrix_frame.pack(side=tk.TOP, fill=tk.X)

        self.port_list_frame = tk.Frame(self.master,width=600, height=400)
        self.port_list_frame.pack(side=tk.TOP,fill=tk.X)

        # Create buttons and pack them in the button frame
        self.fresh_button = tk.Button(self.select_draw_frame, text="fresh", command=self.refresh_selected_points)
        self.fresh_button.pack(side=tk.LEFT, padx=5)

        self.select_mode_button = tk.Button(self.select_draw_frame, text="Enable Selection Mode", command=self.toggle_select_mode)
        self.select_mode_button.pack(side=tk.LEFT, padx=5)

        self.id_select_button = tk.Button(self.select_draw_frame, text="Enable individual Selection Mode", command=self.individual_select_mode)
        self.id_select_button.pack(side=tk.LEFT, padx=5)

        self.predict_button = tk.Button(self.select_draw_frame, text="Predict", command=self.predict_points)
        self.predict_button.pack(side=tk.LEFT, padx=5)


        self.delete_selected_points_button = tk.Button(self.select_draw_frame, text="Delete Selected Points", command=self.delete_selected_points)
        self.delete_selected_points_button.pack(side=tk.LEFT, padx=5)

        self.revision_mode_button = tk.Button(self.select_draw_frame, text="Enable Revision Mode", command=self.toggle_revision_mode)
        self.revision_mode_button.pack(side=tk.LEFT, padx=5)

        self.capture_image_and_draw_button = tk.Button(self.button_frame, text="Capture Image and Draw", command=self.capture_image_and_draw)
        self.capture_image_and_draw_button.pack(side=tk.LEFT, padx=5)

        self.generate_button = tk.Button(self.button_frame, text="Generate mapping PATH", command=self.generate_path)
        self.generate_button.pack(side=tk.LEFT, padx=5)


        self.background_button = tk.Button(self.button_frame, text="Select Background Image", command=self.select_background_image)
        self.background_button.pack(side=tk.LEFT, padx=5)

        
        self.capture_image_button = tk.Button(self.button_frame, text="Capture Image", command=self.capture_image)
        self.capture_image_button.pack(side=tk.LEFT, padx=5)

        self.drive_ASI_button = tk.Button(self.matrix_frame, text="Drive ASI", command=lambda:self.threading_process(self.perform_movement_sequence))
        self.drive_ASI_button.pack(side=tk.LEFT, padx=5)

        self.matrix_size_label = tk.Label(self.matrix_frame, text="Matrix Size (x by y):")
        self.matrix_size_label.pack(side=tk.LEFT, padx=5)
        
        self.matrix_size_x_entry = tk.Entry(self.matrix_frame, width=5)
        self.matrix_size_x_entry.pack(side=tk.LEFT, padx=5)
        self.matrix_size_x_entry.insert(0, "5")  # Default value

        self.matrix_size_y_entry = tk.Entry(self.matrix_frame, width=5)
        self.matrix_size_y_entry.pack(side=tk.LEFT, padx=5)
        self.matrix_size_y_entry.insert(0, "4")  # Default value

        self.set_matrix_size_button = tk.Button(self.matrix_frame, text="Set Matrix Size", command=self.set_matrix_size)
        self.set_matrix_size_button.pack(side=tk.LEFT, padx=5)

        self.time_gap_label = tk.Label(self.matrix_frame, text="Time gap per step (s):")
        self.time_gap_label.pack(side=tk.LEFT, padx=5)
        
        self.time_gap_entry = tk.Entry(self.matrix_frame, width=5)
        self.time_gap_entry.pack(side=tk.LEFT, padx=5)
        self.time_gap_entry.insert(0, f"{self.ASI.conutdown_time}")  # Default value

        self.set_time_gap_button = tk.Button(self.matrix_frame, text="Set Time gap", command=self.set_time_gap)
        self.set_time_gap_button.pack(side=tk.LEFT, padx=5)

        self.refactor_label = tk.Label(self.matrix_frame, text="Scale factor pixel to um:")
        self.refactor_label.pack(side=tk.LEFT, padx=5)
        
        self.refactor_entry = tk.Entry(self.matrix_frame, width=5)
        self.refactor_entry.pack(side=tk.LEFT, padx=5)
        self.refactor_entry.insert(0, f"{self.ASI.refactor}")  # Default value

        self.refactor_entry_button = tk.Button(self.matrix_frame, text="Set refactor", command=self.set_refactor)
        self.refactor_entry_button.pack(side=tk.LEFT, padx=5)

        

        # Label for the port list
        self.port_list_label = tk.Label(self.port_list_frame, text="Available Ports")
        self.port_list_label.pack(side=tk.LEFT, padx=5)

        # Listbox for the port list
        self.port_listbox = ttk.Combobox(self.port_list_frame)
        self.port_listbox.pack(side=tk.LEFT, padx=5)

        # Button to refresh the port list
        self.refresh_button = tk.Button(self.port_list_frame, text="Refresh Ports", command=self.refresh_ports)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        self.confirm_button = tk.Button(self.port_list_frame, text="select", command=self.select_port)
        self.confirm_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(self.port_list_frame, text="Stop", command=self.ASI.stop_signal)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Call the function to initially populate the list
        self.refresh_ports()



        
        
        modifier = 'Command' if self.master.tk.call('tk', 'windowingsystem') == 'aqua' else 'Control'
        self.master.bind(f"<{modifier}-a>", self.select_all_points)
       
       
 
        
       
        # 创建状态栏
        self.status_bar = tk.Label(self.master, text="Connecting to camera...", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 尝试连接相机
        self.camera = None
         # 创建画布
        self.camera_canvas = self.camera_canvas
        self.camera_canvas.pack()
        try:
            self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
            self.camera.Open()
            self.status_bar.config(text="Camera connected.")
            self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            self.converter = pylon.ImageFormatConverter()
        
            # 开始更新画面
            self.update_camera()
        except Exception as e:
            self.status_bar.config(text=f"Failed to connect to camera: {e}")

        self.in_individual_select_mode = False
        self.currently_moving_point = None
        self.in_revision_mode = False
        self.currently_selected_oval = None
        self.in_select_mode = False
        self.selection_rect = None
        self.background_image = None
        self.background_image_tk = None
        self.background_image_path = None
        self.matrix_size_x = int(self.matrix_size_x_entry.get())
        self.matrix_size_y = int(self.matrix_size_y_entry.get())
        self.master.bind("<Command-d>", lambda event: self.deselect_all_points())  # For MacOS
        self.master.bind("<Control-d>", lambda event: self.deselect_all_points()) # For Windows and Linux
        self.selected_points = []
        self.currently_selected_points = []  # 用于存储当前选中的点
        self.predict_points_set=[]
        self.draw_points = []
        self.generate_path_set = []
        self.all_physical_points = list(set(self.draw_points) | set(self.predict_points_set))
        





    def draw_point(self, x, y,color="green"):
        oval = self.canvas.create_oval(x-5, y-5, x+5, y+5, fill=color)
        return oval
    
    def update_all_physical_points(self):
        self.all_physical_points = list(set(self.draw_points) | set(self.predict_points_set))

   

    def draw_the_point(self, event):
        x, y = event.x, event.y
        point_id = self.draw_point(x, y)
        self.draw_points.append((x, y, point_id))
        self.update_all_physical_points()
        print("Drawing point: ({}, {})".format(x, y))

    def sort_currently_selected_points(self):
    # Sort the list based on the third element of each tuple (the ID)
        self.currently_selected_points = sorted(self.currently_selected_points, key=lambda x: x[2])
    
    def select_point(self, event):
    # Allow individual selection if not all points are selected
        x, y = event.x, event.y
        for x,y,point_id in self.all_physical_points:
            if abs(x - event.x) <= 5 and abs(y - event.y) <= 5:
                self.canvas.itemconfig(point_id, fill="blue")
                self.currently_selected_points.append((x,y,point_id))
                print("Selected point: ({}, {})".format(x, y))
                print("Currently selected points:", self.currently_selected_points)

    def set_matrix_size(self):
        try:
            self.matrix_size_x = int(self.matrix_size_x_entry.get())
            self.matrix_size_y = int(self.matrix_size_y_entry.get())
            print(f"Matrix size set to: {self.matrix_size_x} by {self.matrix_size_y}")
        except ValueError:
            print("Please enter valid integers for matrix size.")
    def set_time_gap(self):
        try:
            self.ASI.conutdown_time = int(self.time_gap_entry.get())
            print(f"Time gap set to: {self.ASI.conutdown_time}s")
        except ValueError:
            print("Please enter valid integers for time gap.")

    def set_refactor(self):
        try:
            self.ASI.refactor = self.refactor_entry.get()
            print(f"Refactor set to: {self.ASI.refactor}")
        except ValueError:
            print("Please enter valid integers for refactor.")
    def predict_points(self):
        if self.matrix_size_x_entry.get() and self.matrix_size_y_entry.get():
            matrix_generate = tuple([self.matrix_size_x,self.matrix_size_y])
            if len(self.currently_selected_points) == 3:
                self.selected_points = self.currently_selected_points.copy()
                origin = self.selected_points[0]
                neighbor1 = self.selected_points[1]
                neighbor2 = self.selected_points[2]
                distance1 = np.linalg.norm(np.array(neighbor1) - np.array(origin))
                distance2 = np.linalg.norm(np.array(neighbor2) - np.array(origin))
                distance_use = np.average(np.abs([distance1, distance2]))
                theta1 = np.arctan2(neighbor1[1] - origin[1], neighbor1[0] - origin[0])
                theta2 = np.arctan2(neighbor2[1] - origin[1], neighbor2[0] - origin[0])
                theta_predict = theta1
                print("theta1: {}, theta2: {}".format(theta1*180/np.pi, theta2*180/np.pi))
                matrix_rotate = np.array([[np.cos(theta_predict), - np.sin(theta_predict)], [np.sin(theta_predict), np.cos(theta_predict)]])
                num_x,num_y = matrix_generate
                x_drawd = [points[0] for points in self.selected_points]
                y_drawd = [points[1] for points in self.selected_points]
                print(x_drawd, y_drawd)
                for i in range(num_x):
                    for j in range(num_y):
                        x =  i * distance1
                        y = - j * distance2
                        x, y = np.dot(matrix_rotate, np.array([x, y]))
                        x += origin[0]
                        y += origin[1]
                        print("Predicted point: ({}, {})".format(x, y))
                        if all(abs(x - xi) > 10 or abs(y - yi) > 10 for xi, yi in zip(x_drawd, y_drawd)):
                            ##这个判读需要改改，到时候想想怎么改
                            point_id = self.draw_point(x, y,'red')
                            self.predict_points_set.append((x, y, point_id))
                self.update_all_physical_points()
            else:
                print("Please select three points.")

    def refresh_selected_points(self):
        self.draw_points = []
        self.selected_points = []
        self.predict_points_set = []
        self.all_physical_points = []
        self.canvas.delete("all")
        if self.background_image_tk:
            self.canvas.config(width=self.background_image.width, height=self.background_image.height)
            self.canvas.create_image(0, 0, anchor="nw", image=self.background_image_tk)
        else:
            self.canvas.config(width=400, height=300, bg='white')
    
    # def continue_predict(self):
    #     self.selected_points= []
    #     print("Please select another three points.")


    def start_rect(self, event):
        # If there's an old rectangle, delete it
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        # Create rectangle
        self.selection_rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def expand_rect(self, event):
        self.canvas.coords(self.selection_rect, self.start_x, self.start_y, self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

    def complete_rect(self, event):
    # Check if the rectangle exists and has valid coordinates
        rect_coords = self.canvas.coords(self.selection_rect)
        if self.selection_rect and len(rect_coords) == 4:
            x1, y1, x2, y2 = rect_coords
            self.currently_selected_points= [point for point in self.all_physical_points if x1 <= point[0] <= x2 and y1 <= point[1] <= y2]
            
            # Rest of your code
            print(f"Selected points: {self.currently_selected_points}")
            self.canvas.delete(self.selection_rect)


    def individual_select_mode(self):
        self.in_individual_select_mode = not self.in_individual_select_mode
        if self.in_individual_select_mode:
            self.canvas.bind("<Button-1>", self.select_point)
            self.id_select_button.config(text="Disable Selection Mode")
        else:
            self.canvas.bind("<Button-1>", self.draw_the_point)
            self.id_select_button.config(text="Enable Selection Mode")

    def toggle_select_mode(self):
        self.in_select_mode = not self.in_select_mode
        if self.in_select_mode:
            # Bind the rectangle selection events
            self.canvas.bind("<ButtonPress-1>", self.start_rect)
            self.canvas.bind("<B1-Motion>", self.expand_rect)
            self.canvas.bind("<ButtonRelease-1>", self.complete_rect)
            self.select_mode_button.config(text="Disable Selection Mode")
        else:
            # Re-bind the point selection event and update button text
            self.canvas.bind("<Button-1>", self.draw_the_point)
            self.select_mode_button.config(text="Enable Selection Mode")

    def toggle_revision_mode(self):
        self.in_revision_mode = not self.in_revision_mode
        if self.in_revision_mode:
            self.canvas.bind("<ButtonPress-1>", self.start_moving_point)
            self.canvas.bind("<B1-Motion>", self.move_point)
            self.revision_mode_button.config(text="Disable Revision Mode")
        else:
            self.canvas.bind("<Button-1>", self.draw_the_point)
            self.revision_mode_button.config(text="Enable Revision Mode")
    def start_moving_point(self, event):
        # Find the closest point to the click
        closest_point_id = self.canvas.find_closest(event.x, event.y)[0]
        for (px, py, pid) in self.currently_selected_points:
            if pid == closest_point_id:
                self.currently_moving_point = (px, py, pid)
                break
            
    def move_point(self, event):
        if self.currently_moving_point:
            _, _, pid = self.currently_moving_point
            # Move the point to the new position
            self.canvas.coords(pid, event.x-5, event.y-5, event.x+5, event.y+5)
            # Update the point's position in the selected_points list
            index = self.selected_points.index(self.currently_moving_point)
            self.all_physical_points[index] = (event.x, event.y, pid)

    
    
    def select_all_points(self, event=None):
        # Clear any previously selected points
        self.currently_selected_points.clear()

        # Add all points to the currently selected points list and change their color
        for x, y, point_id in self.all_physical_points:
            self.canvas.itemconfig(point_id, fill="blue")
            self.currently_selected_points.append((x,y,point_id))
        self.sort_currently_selected_points()
        # Print all selected points
        print("Selected points:", [(x, y,z) for x, y,z in self.all_physical_points])


    def deselect_all_points(self):
    # Remove highlight from all selected points (optional)
        selected_ids = [point_id for _, _, point_id in self.currently_selected_points]
    
        # Remove highlight from all selected points
        for _, _, point_id in self.all_physical_points:
            if point_id in selected_ids:
                self.canvas.itemconfig(point_id, fill="green")  # Reset the color
        
        # Clear the list of currently selected points
        self.currently_selected_points = []

    def delete_selected_points(self):
        # Remove highlight from all selected points (optional)
        selected_ids = [point_id for _, _, point_id in self.currently_selected_points]
    
        # Remove highlight from all selected points
        for _, _, point_id in self.all_physical_points:
            if point_id in selected_ids:
                self.canvas.delete(point_id)
                self.draw_points = [item for item in self.draw_points if item[2] != point_id]
                self.predict_points_set = [item for item in self.predict_points_set if item[2] != point_id]
        self.update_all_physical_points()
        print("current points are:", self.all_physical_points)
    
    def update_camera(self):
        if self.camera and self.camera.IsGrabbing():
            grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            if grabResult.GrabSucceeded():
                # 图像转换为OpenCV格式
                image = self.converter.Convert(grabResult)
                img = image.GetArray()
                img_pil = Image.fromarray(img)
                # 将图像大小设置为原来的一半
                img_pil_half = img_pil.resize((img_pil.width // 2, img_pil.height // 2))
                img_pil.close()

                if hasattr(self, 'imgtk'):
                    del self.imgtk

            # 创建新的PhotoImage对象
                self.imgtk = ImageTk.PhotoImage(image=img_pil_half)
                
                # 更新画布上的图像
                self.camera_canvas.create_image(
                    self.camera_canvas.winfo_width() // 2, 
                    self.camera_canvas.winfo_height() // 2,
                    image=self.imgtk, anchor=tk.CENTER)
                # if self.all_physical_points:
                #     for point in self.all_physical_points:
                #         self.draw_point_on_camera(*point)
                # self.camera_canvas.imgtk = imgtk  # Keep a reference, prevent garbage-collection
                self.camera_updated_event.set()

            grabResult.Release()
            gc.collect()
            # 重新调用update_camera进行下一次更新
            self.master.after(100, self.update_camera)
    
    def draw_point_on_camera(self, x, y, color="red"):
            radius = 5
            self.camera_canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color)

    def select_background_image(self):
        self.background_image_path = filedialog.askopenfilename()
        if self.background_image_path:
            original_image = Image.open(self.background_image_path)
            self.background_image = original_image.resize((original_image.width//2, original_image.height//2))
            self.background_image_tk = ImageTk.PhotoImage(self.background_image)
            self.canvas.config(width=self.background_image.width, height=self.background_image.height)
            self.canvas.create_image(0, 0, anchor="nw", image=self.background_image_tk)       

    def capture_image(self):
        if self.camera and self.camera.IsGrabbing():
            grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            if grabResult.GrabSucceeded():
                # 图像转换为OpenCV格式
                image = self.converter.Convert(grabResult)
                img = image.GetArray()
                cv2.imwrite("capture.jpg", img)
                print("Capture image successfully.")
            grabResult.Release()

    def capture_image_and_draw(self):
        # self.canvas = self.camera_canvas
        if self.camera and self.camera.IsGrabbing():
            grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

            if grabResult.GrabSucceeded():
                # 图像转换为OpenCV格式
                image = self.converter.Convert(grabResult)
                img = image.GetArray()

                # 将图像转换为Tkinter格式
                
                img_pil = Image.fromarray(img)
                # 将图像大小设置为原来的一半
                img_pil_half = img_pil.resize((img_pil.width // 2, img_pil.height // 2))
                imgck = ImageTk.PhotoImage(image=img_pil_half)
                # 更新画布上的图像
                self.canvas.create_image(self.camera_canvas.winfo_width() // 2, 
                    self.camera_canvas.winfo_height() // 2,
                    image=imgck, anchor=tk.CENTER)
                self.canvas.imgck = imgck  # Keep a reference, prevent garbage-collection
            grabResult.Release()



    def generate_path(self):
        self.generate_path_set= gpo.matrix_move_to_origin(self.currently_selected_points)
        gpo.draw_the_whole_map(self.generate_path_set)

    def refresh_ports(self):
        # Clear the listbox
        self.port_listbox.delete(0, tk.END)

        # List all available ports
        ports = serial.tools.list_ports.comports()
        port_list = [f"{port.device} - {port.description}" for port in ports]
        # Set the values of the Combobox to the list of ports
        self.port_listbox['values'] = port_list
        if port_list:
            self.port_listbox.current(0) 
            
    def select_port(self):
        # Get the selected port
        selected_port = self.port_listbox.get().split(" - ")[0]
        print(selected_port)
        # Extract the port name
        # Select the port
        self.ASI.ser = serial.Serial(selected_port, 9600, timeout=1)
        print(self.ASI.ser.name)
        print("Port selected")
        self.confirm_button.config(text="Port selected")

    # def drive_ASI(self):
    #     for item in self.generate_path_set:
    #         x ,y ,id = item
    #         self.ASI.ASI_XY_move_single(x,y)
    #         self.update_camera()
      

    def threading_process(self, func, *arg):
        self.threading_process = threading.Thread(target=func, args=arg)
        self.threading_process.setDaemon(True)
        self.threading_process.start()

    # def drive_ASI(self):
    #     # 使用线程来处理移动命令
    #     t=threading.Thread(target=self.perform_movement_sequence, args=())
    #     t.setDaemon(True)
    #     t.start()
        

    def perform_movement_sequence(self):
        self.drive_ASI_button.config(state=tk.DISABLED)
        for item in self.generate_path_set:
            x, y, _ = item
            x = float(x)
            y = float(y)
           
            self.ASI.ASI_XY_move_single(x, y)
            self.master.after(10, lambda:self.threading_process(self.update_camera))
            self.camera_updated_event.wait(timeout=3)
            # 重置事件，为下一次更新做准备
            self.camera_updated_event.clear()
            # 这里不直接调用 update_camera，因为它可能会导致线程冲突
            # 而是使用 after 来安排 update_camera 的调用
            #self.master.after_cancel(self.after_id)

        # 结束后更新界面状态，例如重置按钮等
        self.master.after(50, self.update_ui_after_movement)

    def update_ui_after_movement(self):
        # 重置按钮状态
        self.ASI.ASI_XY_move_single(0,0)
        self.drive_ASI_button.config(state=tk.NORMAL)
        self.refresh_button.config(state=tk.NORMAL)
        self.confirm_button.config(state=tk.NORMAL)
        #self.stop_button.config(state=tk.DISABLED)
        self.status_bar.config(text="Movement sequence finished.")
        #self.update_camera()


root = tk.Tk()
ASIcontrol = asi.ASI_control()
app = App(root,ASIcontrol)
root.mainloop()
# def start_moving_point(self, event):

    #     # Find the closest point to the click
    #     closest_point_id = self.canvas.find_closest(event.x, event.y)[0]
    #     # Only allow moving if revision mode is active
    #     if self.in_revision_mode:
    #         for (px, py, pid) in self.selected_points:
    #             if pid == closest_point_id:
    #                 self.currently_moving_point = (px, py, pid)
    #                 self.initial_x, self.initial_y = event.x, event.y  # Save the initial click coordinates
    #                 break

    # def move_point(self, event):
    #     # If only one point is currently selected for moving
    #     if self.currently_moving_point:
    #         print("Moving point")
    #         if self.in_revision_mode and self.currently_moving_point and len(self.currently_selected_points) == 1:
    #             # Calculate the change in x and y
    #             dx = event.x - self.initial_x
    #             dy = event.y - self.initial_y

    #             # Get the current coordinates of the point
    #             _, _, point_id = self.currently_moving_point
    #             x, y, _, _ = self.canvas.coords(point_id)

    #             # Move the point by dx, dy
    #             self.canvas.coords(point_id, x + dx, y + dy, x + dx + 10, y + dy + 10)

    #             # Update the initial coordinates after the move
    #             self.initial_x, self.initial_y = event.x, event.y
    #         # If all points are selected and we are in revision mode, move all points
    #         elif self.in_revision_mode and len(self.currently_selected_points) == len(self.selected_points):
    #             # Calculate the change in x and y
    #             dx = event.x - self.initial_x
    #             dy = event.y - self.initial_y

    #             # Move all points by dx, dy
    #             for _, _, point_id in self.selected_points:
    #                 x, y, _, _ = self.canvas.coords(point_id)
    #                 self.canvas.coords(point_id, x + dx, y + dy, x + dx + 10, y + dy + 10)

    #             # Update the initial coordinates after the move
    #             self.initial_x, self.initial_y = event.x, event.y
