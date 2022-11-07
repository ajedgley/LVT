"""
	functions for editing, we'll see how useful this file is
"""

import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
import open3d as o3d
import functools
import numpy as np
from pyquaternion import Quaternion

ORIGIN = 0
SIZE = 1
ROTATION = 2
# returns created window with all its buttons and whatnot
# maybe not be futureproofed, we'll have to see how nicely it plays with the rest of the functions
def setup_control_window(scene_widget, boxes, extrinsics):
	current_boxes = boxes
	cw = gui.Application.instance.create_window("LCT", 400, 800)
	
	# shamelessly stolen from lct setup, cuz their window looks nice
	em = cw.theme.font_size
	margin = gui.Margins(0.50 * em, 0.25 * em, 0.50 * em, 0.25 * em)
	layout = gui.Vert(0, margin)

	# button for adding a new bounding box
	add_box_horiz = gui.Horiz()
	add_box_button = gui.Button("Add New Bounding Box")
	box_partial = functools.partial(add_bounding_box, widget=scene_widget) # necessary to add args to functions
	add_box_button.set_on_clicked(box_partial)
	add_box_horiz.add_child(add_box_button)


	open_box_horiz = gui.Horiz()
	open_box_button = gui.Button("Generate Boxes")
	box_partial = functools.partial(create_box_scene, scene=scene_widget, boxes=current_boxes, extrinsics=extrinsics)
	open_box_button.set_on_clicked(box_partial)
	open_box_horiz.add_child(open_box_button)

	# button for exiting annotation mode
	exit_annotation_horiz = gui.Horiz()
	exit_annotation_button = gui.Button("Exit Annotation Mode")
	exit_partial = functools.partial(exit_annotation_mode, widget=scene_widget)
	exit_annotation_button.set_on_clicked(exit_partial)
	exit_annotation_horiz.add_child(exit_annotation_button)

	# add various metrics and number thingies used to display info about the current bbox
	click_partial = functools.partial(get_point_depth, widget=scene_widget)
	scene_widget.set_on_mouse(click_partial)
	# adding all of the horiz to the vert, in order
	layout.add_child(add_box_horiz)
	layout.add_child(exit_annotation_horiz)
	layout.add_child(open_box_horiz)
	
	cw.add_child(layout)
	
	return cw
	
# function should:
# disable the current mouse functionality
# onclick, adds a bounding box at the location of click (or maybe just center screen? idk)
# highlight the current bounding box
# re-enable the mouse functionality
# return the new bounding box

def add_bounding_box(widget):
	partial = functools.partial(place_bounding_box, widget=widget)
	widget.set_on_mouse(partial)

# function should:
# close the exiting control panel
# idk, restore the state as if the program just reopened
# potential ideas:
# -just restart the program (hey, it'll probably work)
# -close control window, reopen any previously closed windows, and run update (maybe update done in lct)
def exit_annotation_mode(widget):
	print("TODO")
	widget.set_on_mouse(enable_mouse)

# onclick, places down a bounding box on the cursor, then reenables mouse functionality
def place_bounding_box(event, widget):
	if event.type == gui.MouseEvent.Type.BUTTON_DOWN:
		print("clicked!")
		
		widget.set_on_mouse(enable_mouse)
		return gui.Widget.EventCallbackResult.CONSUMED
	
	return gui.Widget.EventCallbackResult.CONSUMED

# disables current mouse functionality, ie dragging screen and stuff
def disable_mouse(event):

	return gui.Widget.EventCallbackResult.CONSUMED

# re-enables mouse functionality to their defaults
def enable_mouse(event):
	return gui.Widget.EventCallbackResult.IGNORED

def get_point_depth(event, widget):
	curr_widget = widget
	curr_event = event
	if event.type == gui.MouseEvent.Type.BUTTON_DOWN and event.is_modifier_down(gui.KeyModifier.CTRL):
		def get_depth(depth_image):
			x = event.x - widget.frame.x
			y = event.y - widget.frame.y

			depth = np.asarray(depth_image)[y, x]
			world = widget.scene.camera.unproject(
				event.x, event.y, depth, widget.frame.width, widget.frame.height)
			output = "({:.3f}, {:.3f}, {:.3f})".format(
				world[0], world[1], world[2])
			print(output)
		widget.scene.scene.render_to_depth_image(get_depth)
		return gui.Widget.EventCallbackResult.HANDLED
	return gui.Widget.EventCallbackResult.IGNORED

def create_box_scene(scene, boxes, extrinsics):
	id = 0
	cube_indices = []
	mat = rendering.MaterialRecord()
	mat.shader = "defaultLit"

	for box in boxes:
		size = [0, 0, 0]
		size[0] = box[SIZE][1]
		size[1] = box[SIZE][0]
		size[2] = box[SIZE][2]

		cube_to_add = o3d.geometry.TriangleMesh.create_box(size[0], size[1], size[2], False, False)
		cube_to_add = cube_to_add.translate(np.array([0,0,0]), False)
		cube_to_add = cube_to_add.rotate(Quaternion(box[ROTATION]).rotation_matrix, [0,0,0])
		cube_to_add = cube_to_add.translate(box[ORIGIN])


		cube_to_add = cube_to_add.rotate(Quaternion(extrinsics['rotation']).rotation_matrix, [0,0,0])
		cube_to_add = cube_to_add.translate(np.array(extrinsics['translation']))
		cube_id = "cube_" + str(id)
		cube_indices.append(cube_id)
		id += 1

		cube_to_add.compute_vertex_normals()
		scene.scene.add_geometry(cube_id, cube_to_add, mat)







