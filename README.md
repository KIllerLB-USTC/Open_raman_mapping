# Software Functions and Elements


![[ASI_control_raman_mapping_gui/1.gif]]
## Window:
- **A**: Canvas for Mapping Points Drawing and Preview.
- **B**: Real-time Camera Preview, compatible with all Basler Cameras and Camera systems that support the Pylon API.

## Path Drawing and Generation: 
- **Function 1**: Capture Window B to Window A, allowing users to draw a path on Window A.
- **Function 2**: Generate a mapping path for users to preview. The stage movement will follow this generated path.
- **Function 3**: Set a background image for Window A for debugging or testing purposes.
- **Function 4**: Store the image in Window A while preserving the path information.
- **Function 5**: Refresh Window A to draw the next path.

## Mapping Points Modification (Revision):
- **Function 6**: Enable rectangle select box to choose mapping points.
- **Function 7**: Enable users to choose mapping points one by one.
- **Function 8**: Predict the mapping matrix. Users can select three points (original point, first point in the width direction, and first point in the height direction) to predict the mapping matrix. The matrix size can be adjusted using buttons and boxes.
- **Function 9**: Delete selected points.
- **Function 10**: Enable Envision mode. Users can use the mouse to relocate (move) the selected points.

## Stage Movement Control (Move the stage along the generated mapping path):

- **Function 15**: Choose and connect to the stage control server port. List all available ports on the current computer, select a port manually, and confirm the selection by clicking "select." If you can't find the desired port, reconnect the port and click "Refresh ports."
- **Function 13**: Set the hold-on time between each scanning (default: 2 seconds). After finishing the move to one point, the system will wait for 2 seconds before moving to the next one. The speed from one spot to the next can also be adjusted.
- **Function 14**: Set the scale, which represents the transformation factor from pixels to real-world physical length. In our case, the factor is 9.8 pixels/um.
- **Message Box 16**: Displays the status for the camera and stage control.

