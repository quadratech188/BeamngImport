import bpy
import os
from . import beamngImport_main

from bpy.types import Operator

class beamngImport_OT_Import_New(Operator):
    bl_idname = "beamng.import"
    bl_label = "Import new model"
    bl_description = "Import a new gLTF BeamNG Export"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        beamngImport_main.getFilepath()
        beamngImport_main.loadNew(context.scene.my_tool.name, context.scene.my_tool.vehicleType, context.scene.my_tool.path, context.scene.my_tool.useCommon)

        return {"FINISHED"}

class beamngImport_OT_Reload(Operator):
    bl_idname = "beamng.reload"
    bl_label = "Reload materials"
    bl_description = "Re-apply all materials in collection"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        beamngImport_main.getFilepath()
        beamngImport_main.reload(context.scene.my_tool.reloadVehicleType, context.scene.my_tool.reloadCollection, context.scene.my_tool.reloadUseCommon)

        return {"FINISHED"}
