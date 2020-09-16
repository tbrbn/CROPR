bl_info = {
    "name": "Import Blueprints",
    "author": "Thibaut Bourbon",
    "version": (1, 0),
    "blender": (2, 83, 4),
    "location": "File > Import > Blueprints",
    "description": "Import blueprints and place them accordingly",
    "warning": "Pictures names should finish by _front, _side, _top, and _rear before the .extension",
    "doc_url": "",
    "category": "Add Image Reference",
}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
import bpy
import math, mathutils
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty
from bpy.types import Operator, OperatorFileListElement



def read_some_data(context, directory, files, *use_some_setting):
    print("Scanning and placing the blueprints")
    bp_front, bp_side, bp_left, bp_right, bp_top, bp_bottom, bp_rear = "","","","","","",""
    for i in files:
        if "_front." in i.name:
            bp_front = directory+i.name
        if "_side." in i.name:
            bp_side = directory+i.name
        if "_left." in i.name:
            bp_left = directory+i.name
        if "_right." in i.name:
            bp_right = directory+i.name
        if "_top." in i.name:
            bp_top = directory+i.name
        if "_bottom." in i.name:
            bp_bottom = directory+i.name
        if "_rear." in i.name:
            bp_rear = directory+i.name
    place_the_imported_images(bp_front, bp_side, bp_left, bp_right, bp_top, bp_bottom, bp_rear)
    return {'FINISHED'}


def place_the_imported_images(bp_front, bp_side, bp_left, bp_right, bp_top, bp_bottom, bp_rear):
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            matrix = area.spaces[0].region_3d.view_matrix
            ctx = {"area": area}
            if bp_front is not '':
                bpy.ops.view3d.view_axis(ctx, type="FRONT")
                bpy.ops.object.load_reference_image(filepath=bp_front)
                # Lines below to delete once the view_align stuff is fixed
                bpy.ops.transform.rotate(value=-math.pi/2,orient_axis='X')
                ###
                front_w = bpy.data.images[bp_front.split("\\")[-1]].size[0]
                front_h = bpy.data.images[bp_front.split("\\")[-1]].size[1]
                if front_h > front_w:
                    s = front_h/front_w
                    bpy.ops.transform.resize(value=(s,s,s))
                    bpy.ops.transform.translate(value=(0,-20,0))
                else:
                    bpy.ops.transform.translate(value=(0,-6,0))
                bpy.context.object.empty_image_side = 'FRONT'
                bpy.context.object.use_empty_image_alpha = True
                bpy.context.object.color[3] = 0.5
            else:
                front_w = 1
                front_h =1
            if bp_side is not '':
                bpy.ops.view3d.view_axis(ctx, type="RIGHT")
                bpy.ops.object.load_reference_image(filepath=bp_side)
                # Lines below to delete once the view_align stuff is fixed
                bpy.ops.transform.rotate(value=3*math.pi/2,orient_axis='X')
                bpy.ops.transform.rotate(value=3*math.pi/2,orient_axis='Z')
                ###
                side_w = bpy.data.images[bp_side.split("\\")[-1]].size[0]
                side_h = bpy.data.images[bp_side.split("\\")[-1]].size[1]
                s = max(side_w/front_w,front_w/side_w)
                bpy.ops.transform.resize(value = (s,s,s))
                bpy.ops.transform.translate(value = (-4,0,0) )
                bpy.context.object.empty_image_side = 'FRONT'
                bpy.context.object.use_empty_image_alpha = True
                bpy.context.object.color[3] = 0.5
            if bp_top is not '':
                bpy.ops.view3d.view_axis(ctx, type="TOP")
                bpy.ops.object.load_reference_image(filepath=bp_top)
                # Lines below to delete once the view_align stuff is fixed
                bpy.ops.transform.rotate(value=3*math.pi/2,orient_axis='Z')
                ###
                top_w = bpy.data.images[bp_top.split("\\")[-1]].size[0]
                top_h = bpy.data.images[bp_top.split("\\")[-1]].size[1]
                s = max(top_w/front_w,front_w/top_w)
                bpy.ops.transform.resize(value = (s,s,s) )
                bpy.ops.transform.translate(value = (0,0,-2) )
                bpy.context.object.empty_image_side = 'FRONT'
                bpy.context.object.use_empty_image_alpha = True
                bpy.context.object.color[3] = 0.5
            if bp_rear is not '':
                bpy.ops.view3d.view_axis(ctx, type="BACK")
                bpy.ops.object.load_reference_image(filepath=bp_rear)
                # Lines below to delete once the view_align stuff is fixed
                bpy.ops.transform.rotate(value=3*math.pi/2,orient_axis='X')
                ###
                rear_w = bpy.data.images[bp_rear.split("\\")[-1]].size[0]
                rear_h = bpy.data.images[bp_rear.split("\\")[-1]].size[1]
                if rear_h > rear_w:
                    s = rear_h/rear_w
                    bpy.ops.transform.resize(value=(s,s,s))
                    bpy.ops.transform.translate(value=(0,15,0))
                else:
                    bpy.ops.transform.translate(value=(0,6,0))
                bpy.context.object.empty_image_side = 'BACK'
                bpy.context.object.use_empty_image_alpha = True
                bpy.context.object.color[3] = 0.5
            area.spaces[0].region_3d.view_matrix = mathutils.Matrix(matrix)

class ImportSomeData(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import blueprints"


    # ImportHelper mixin class uses this
    filename_ext = ".png"

    filter_glob: StringProperty(
        default="*.png",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    
    files: CollectionProperty(
        name="File Path",
        type=OperatorFileListElement,
    )
    
    directory: StringProperty(
        subtype='DIR_PATH',
    )
    
    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    #use_setting: BoolProperty(
    #    name="More t",
    #    description="",
    #    default=False,
    #)

    #type: EnumProperty(
    #    name="Example Enum",
    #    description="Choose between two items",
    #    items=(
    #        ('OPT_A', "First Option", "Description one"),
    #        ('OPT_B', "Second Option", "Description two"),
    #    ),
    #    default='OPT_A',
    #)

    def execute(self, context):
        return read_some_data(context, self.directory, self.files)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportSomeData.bl_idname, text="Blueprints")


def register():
    bpy.utils.register_class(ImportSomeData)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportSomeData)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
    # test call
    bpy.ops.import_test.some_data('INVOKE_DEFAULT')
