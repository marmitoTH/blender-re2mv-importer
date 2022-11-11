import bpy
import math

from bpy.props import StringProperty
from bpy.types import Operator, Panel
from bpy_extras.io_utils import ImportHelper

bl_info = {
    "name": "Import RE2MV models (.obj) and animations (.ani)",
    "blender": (3, 3, 0),
    "category": "Import-Export"
}

class RE2MV(Panel):
    bl_label = "RE2MV Importer"
    bl_idname = "re2mv_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "RE2MV"

    def draw(self, context):
        self.layout.operator(OBJImporter.bl_idname)
        self.layout.operator(ANIImporter.bl_idname)

class OBJImporter(Operator, ImportHelper):
    bl_idname = "re2mv.obj_importer"
    bl_label = "Import OBJ"

    filter_glob: StringProperty(default="*.obj", options={"HIDDEN"})

    def execute(self, context):
        bpy.ops.import_scene.obj(filepath=self.filepath, use_split_groups=True)

        return { "FINISHED" }

class ANIImporter(Operator, ImportHelper):
    bl_idname = "re2mv.ani_importer"
    bl_label = "Import ANI"

    filter_glob: StringProperty(default="*.ani", options={"HIDDEN"})

    def execute(self, context):
        file = open(self.filepath)
        lines = file.readlines()
        parts = int(lines[0])
        objects = context.view_layer.active_layer_collection.collection.objects

        # parent all body parts
        for i in range(parts):
            int_list = [int(x) for x in lines[i + 1].split()]

            for ii in range(int_list[0]):
                child_index = int_list[ii + 1]
                objects[child_index].parent = objects[i]

        # initialize positions
        positions_start_index = parts + 1
        positions_end_index = 2 * parts + 1

        for index, i in enumerate(range(positions_start_index, positions_end_index)):
            position = [float(x) for x in lines[i].split()]

            if objects[index].parent:
                objects[index].location = [position[0], position[2], -position[1]]
            else:
                objects[index].location = position

        # initialize rotations
        reset_rotations(objects)

        # deselects all objects
        bpy.ops.object.select_all(action="DESELECT")

        # initialize animation
        frames = int(lines[positions_end_index])
        animations_start_index = positions_end_index + 1

        for i in range(frames):
            frame_start_index = animations_start_index + i * (parts + 1)
            frame_end_index = frame_start_index + parts + 1

            objects[0].location = [float(x) for x in lines[frame_start_index].split()]
            objects[0].keyframe_insert("location", frame=i)

            reset_rotations(objects)

            for index, j in enumerate(range(frame_start_index + 1, frame_end_index)):
                part_index = parts - 1 - index
                rotation = [float(x) for x in lines[j].split()]

                objects[part_index].select_set(True)
                bpy.ops.transform.rotate(value=math.radians(-rotation[0]), orient_axis="X", orient_type="GLOBAL")
                bpy.ops.transform.rotate(value=math.radians(-rotation[1]), orient_axis="Y", orient_type="GLOBAL")
                bpy.ops.transform.rotate(value=math.radians(-rotation[2]), orient_axis="Z", orient_type="GLOBAL")
                objects[part_index].select_set(False)

                objects[part_index].keyframe_insert("rotation_euler", frame=i)

        return { "FINISHED" }

def reset_rotations(object_list):
    for index, o in enumerate(object_list):
        if index == 0:
            o.rotation_euler = [math.radians(90), 0, 0]
        else:
            o.rotation_euler = [0, 0, 0]

def register():
    bpy.utils.register_class(RE2MV)
    bpy.utils.register_class(OBJImporter)
    bpy.utils.register_class(ANIImporter)

def unregister():
    bpy.utils.unregister_class(RE2MV)
    bpy.utils.unregister_class(OBJImporter)
    bpy.utils.unregister_class(ANIImporter)

if __name__ == "__main__":
    register()
