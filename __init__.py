# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "BeamNG Texture Importer",
    "author" : "QuadraTech",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Import/Export"
}

import bpy

from bpy.props import PointerProperty

from . import beamngImport_main

from . beamngImport_op import beamngImport_OT_Import_New, beamngImport_OT_Reload
from . beamngImport_Gui import MyProperties, beamngImport_PT_Panel, beamngPreferences


classes = (beamngImport_OT_Import_New, beamngImport_OT_Reload, beamngImport_PT_Panel, MyProperties, beamngPreferences)

def register():
    for c in classes:
        try:
            bpy.utils.register_class(c)
            print(c)
        except:
            pass
    
    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)

    beamngImport_main.getFilepath()
    
    

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.my_tool