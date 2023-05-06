
from bpy.types import Panel, PropertyGroup, Collection, AddonPreferences

from bpy.props import StringProperty, BoolProperty, PointerProperty

class beamngPreferences(AddonPreferences):
    bl_idname = __package__

    filepath: StringProperty(
        name="Filepath",
        subtype='DIR_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="File path for your vehicles folder")
        layout.label(text="    ex) E:/BeamNG content/0.26 where E:/BeamNG content/0.26/vehicles is the vehicle folder")
        layout.prop(self, "filepath")

class MyProperties(PropertyGroup):

    
    path : StringProperty(
        name="",
        description="Path to Directory",
        default='*.glb;*.gltf',
        maxlen=1024,
        subtype="FILE_PATH"
    )

    name: StringProperty(
        name="",
        description="Name of imported objects",
        default=""
    )

    useCommon: BoolProperty(
        name="",
        description="Use common materials for identical materials (Doesn't influence skins/colours)",
        default=True
    )

    vehicleType: StringProperty(
        name="",
        description="Types of loadable vehicles",
        default=""
    )

    reloadCollection: PointerProperty(
        type=Collection,
        name="",
        description="Collection to apply the materials in"
    )

    reloadVehicleType: StringProperty(
        name="",
        description="Types of reloadable vehicles",
        default=""
    )

    reloadUseCommon: BoolProperty(
        name="",
        description="Use common materials for identical materials, will generate new materials if needed",
        default=True
    )




class beamngImport_PT_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Import/Reapply BeamNG Textures"
    bl_category = "BeamNG Import"

    def draw(self, context):

        layout = self.layout

        layout.label(text="Import")

        row = layout.row()
        col = row.column()

        box = col.box().column()

        box.label(text="Model Filepath")

        box.prop(context.scene.my_tool, "path", text="")

        box.label(text="Name")

        box.prop(context.scene.my_tool, "name", text="")

        box.label(text="Vehicle type")

        box.prop(context.scene.my_tool, "vehicleType", text="")

        box.label(text="Share identical Materials")

        box.prop(context.scene.my_tool, "useCommon", text="")

        box.operator("beamng.import", text = "Import New Model")

        col.label(text="Reload")

        box = col.box().column()

        box.label(text="Select Collection")

        box.prop(context.scene.my_tool, "reloadCollection", text="")
        
        box.label(text="Vehicle type")

        box.prop(context.scene.my_tool, "reloadVehicleType", text="")

        box.label(text="Share identical Materials")

        box.prop(context.scene.my_tool, "reloadUseCommon", text="")

        box.operator("beamng.reload", text = "Reload")
        
        

