bl_info = {
    "name": "Ctools Addon",
    "author": "Brendan Fitzgerald",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "location": "View3D > Shelf > Ctools",
    "description": "Collection of tools that are useful for use in production assets",
    "warning": "",
    "doc_url": "https://github.com/c1112/bl_ctools/blob/main/README.md",
    "category": "Production",
}

import bpy
import bmesh
import random
from mathutils import Color, Vector

class CTOOLS_OT_Restpos(bpy.types.Operator):
    bl_idname = "ctools.rest"
    bl_label = "Set Rest Position"

    def execute(self, context):
        my_object = bpy.context.active_object.data
        vert_list = my_object.vertices
        color_map_collection = my_object.vertex_colors

        try:
            color_map = color_map_collection['rest']
        except:
            color_map = color_map_collection.new(name='rest')


        i = 0
        for poly in my_object.polygons:
            for idx in poly.loop_indices:
                loop = my_object.loops[idx]
                v = loop.vertex_index
                x = (vert_list[v].co.x )
                y = (vert_list[v].co.y )
                z = (vert_list[v].co.z )
                t = 0
                final = (x,y,z,t)
                color_map.data[i].color = final
                i += 1

        return {'FINISHED'}

class CTOOLS_OT_VtxClr(bpy.types.Operator):
    """Sets Vertex Color in Mesh Edit Mode"""
    bl_idname = "ctools.vtxclr"
    bl_label = "Set Vertex Color"
    btn_name : bpy.props.StringProperty()

    def execute(self, context):
        #get the objects for finding the verts
        edit_object = bpy.context.edit_object.data
        bm = bmesh.from_edit_mesh(edit_object)
        vert_list = bpy.context.active_object.data.vertices

        #setup the RGB Value based on ui input
        if(self.btn_name == "random"):
            RGBA = [random.uniform(0,1) for i in range(3)]
            RGBA.append(0)
        else:
            RGBA = clr = context.scene.mytool_color

        #get the selected faces
        selfaces = [ f for f in bm.faces if f.select]

        #selected verts and colors
        data = {}

        for poly in selfaces:
            for vrt in poly.verts:
                idx = vrt.index
                data[idx] = RGBA

        #switch modes and reaccess data
        bpy.ops.object.mode_set(mode='OBJECT')

        #get the mesh to run over
        mesh = bpy.context.active_object.data
        color_map_collection = mesh.vertex_colors

        try:
            color_map = color_map_collection['Cd']
        except:
            color_map = color_map_collection.new(name='Cd')
            #set inital color map to black
            i = 0
            for polygon in mesh.polygons:
                for idx in polygon.loop_indices:
                    color_map.data[i].color = (0,0,0,0)
                    i += 1

        #set Cd to the current active colormap
        if not color_map.active:
            color_map.active = 1

        #cycle through each polygon
        for polygon in mesh.polygons:
                #for each polygon cycle though the selected verts
                for selected_vert in data:
                    #grab that vertices associated with the current polygon
                    for i, index in enumerate(polygon.vertices):
                        #if the selected vert is found in the current polygon
                        if selected_vert == index:
                            #return the loop indices for the selected vertex
                            loop_index = polygon.loop_indices[i]
                            #use the loop index to set the vertex color
                            color_map.data[loop_index].color = data[selected_vert]


        #switch modes back to edit
        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}

################################################################################
################################################################################

class CTOOLS_PT_Mesh(bpy.types.Panel):
    """Creates a Sub-Panel in the Property Area of the 3D View"""
    bl_label = "CTools Mesh"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CTools"
    bl_context = "mesh_edit"

    def draw(self, context):
        obj = context.object
        layout = self.layout

        row = layout.row()
        row.label(text="Active object is: {}".format(obj.name))

        row = layout.row()
        row.prop(context.scene, "mytool_color")

        row = layout.row()
        usrop = row.operator(CTOOLS_OT_VtxClr.bl_idname, text="User Defined Vertex Color")
        usrop.btn_name = "user"

        row = layout.row()
        randop = row.operator(CTOOLS_OT_VtxClr.bl_idname, text="Random Vertex Color")
        randop.btn_name = "random"

class CTOOLS_PT_Object(bpy.types.Panel):
    """Creates a Sub-Panel in the Property Area of the 3D View"""
    bl_label = "CTools Object"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CTools"
    bl_context = "objectmode"

    def draw(self, context):
        obj = context.object
        layout = self.layout

        row = layout.row()
        row.operator(CTOOLS_OT_Restpos.bl_idname, text="Generate Rest Position")


def register():
    #Register Operators
    bpy.utils.register_class(CTOOLS_OT_VtxClr)
    bpy.utils.register_class(CTOOLS_OT_Restpos)
    #Register Panels
    bpy.utils.register_class(CTOOLS_PT_Mesh)
    bpy.utils.register_class(CTOOLS_PT_Object)


    #Hack for the moment. should roll this into a class
    bpy.types.Scene.mytool_color = bpy.props.FloatVectorProperty(
                 name = "Color Picker",
                 subtype = "COLOR",
                 size = 4,
                 min = 0.0,
                 max = 1.0,
                 default = (1.0,1.0,1.0,1.0))


def unregister():
    #Unregister Operators
    bpy.utils.unregister_class(CTOOLS_OT_VtxClr)
    bpy.utils.unregister_class(CTOOLS_OT_Restpos)
    #Unregister Panels
    bpy.utils.unregister_class(CTOOLS_PT_Mesh)
    bpy.utils.unregister_class(CTOOLS_PT_Object)

    del bpy.types.Scene.mytool_color

if __name__ == "__main__":
    register()
