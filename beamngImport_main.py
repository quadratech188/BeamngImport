"""

TODO

- Figure out specular values for Materials 1.5

- Figure out what specularPower does

- Figure out default specular value

- Find UV maps by order

- Work out autocompleting file structure (can throw errors in some cases: go to the material it couldn't read, and append vehicles/(vehicle name)/)

- Work out alphas for materials with both colorMap and diffuseColor
    (currently diffuseColor overrides colorMap)

- Add support for different versions of same texture

- Iterate based on objects

- Sort out alpha for Materials v1.0


"""
import json
import bpy
import os
import pprint
from pathlib import Path

from . import beamngImport_Gui



baseColorMultipliers = ["ambientOcclusionMap", "baseColorMap", "colorMap"]

nonColorMaps = ["normalMap"]

bsdfConnections = {0 : ["colorPaletteMap_sprt", "diffuseColor", "baseColorFactor", "baseColorMap", "colorMap", "ambientOcclusionMap"],
                   6 : ["colorPaletteMap_sprt", "metallicMap", "metallicFactor"],
                   7 : ["specularPower_sprt", "specularMap"],
                   9 : ["colorPaletteMap_sprt", "roughnessMap", "roughnessFactor"],
                   14 : ["colorPaletteMap_sprt", "clearCoatMap", "clearCoatFactor"],
                   15 : ["colorPaletteMap_sprt", "clearCoatRoughnessFactor"],
                   19 : ["emissiveMap", "emissiveFactor"],
                   20: ["emissive_sprt"],
                   21 : ["alpha_sprt"],
                   22 : ["normal_sprt"]}

collapse = True

failedTextures = []
ddsTextures = []
failedJsons = []

addonPath = os.path.dirname(__file__)

def getFilepath():
    global filepathBase
    filepathBase = bpy.context.preferences.addons[__package__].preferences.filepath[:-1]
    print(filepathBase)

# Load colour setup

def loadSkinApplier(name):
    path = addonPath + "/node tree.blend"

    with bpy.data.libraries.load(path) as (data_from, data_to):
        data_to.node_groups = data_from.node_groups

    global skinApplier
    skinApplier = data_to.node_groups[0]
    skinApplier.name = name

def getSkinApplier(name):
    applierName = name + " Skin Applier"
    global skinApplier
    skinApplier = bpy.data.node_groups[applierName]


      


def preparePath(filepath):
    
    if type(filepath) != str:
        return filepath
    
    if filepath.startswith("@"):
        return None
    
    
    if filepath.startswith("vehicles/"):
        filepath = "/" + filepath
        
    if filepath.endswith(".dds"):
        filepath = filepath[:-4]
        filepath = filepath + ".png"

    path = os.path.normpath(filepath)
    splitPath = path.split(os.sep)
    
    if len(splitPath) == 1:
        splitPath = ("", "vehicles", "common", splitPath[0])
        
        filepath = "/vehicles/common/" + splitPath[0]
    
    vehicleFolder = splitPath[2]

    if os.path.isfile(filepathBase + filepath):
        fullFilepath = filepathBase + filepath

    elif os.path.isfile(filepathBase + "/vehicles/" + vehicleFolder + filepath):
        fullFilepath = filepathBase + "/vehicles/" + vehicleFolder + filepath

    else:
        print("Couldn't find file: " + filepath)
        fullFilepath = None
        if filepath.endswith(".png"):
            
            # Does .dds exist?
            
            filepath = filepath[:-4] + ".dds"
            
            if os.path.isfile(filepathBase + filepath):
                fullFilepath = filepathBase + filepath
                if fullFilepath not in ddsTextures:
                    ddsTextures.append(fullFilepath)

            elif os.path.isfile(filepathBase + "/vehicles/" + vehicleFolder + filepath):
                fullFilepath = filepathBase + "/vehicles/" + vehicleFolder + filepath
                if fullFilepath not in ddsTextures:
                    ddsTextures.append(fullFilepath)
            
            else:
                if filepath not in failedTextures:
                    failedTextures.append(filepath)

        else:
            failedJsons.append(filepath)
        
        return None
            
    
    
    return fullFilepath


def prepareImage(filepath):
    for image in bpy.data.images:
        
        # Is there already an image with the filepath?
        
        if filepath == image.filepath:
            imageInput = image
            
            return imageInput
    
    imageInput = bpy.data.images.load(filepath)
    
    return imageInput

def createGeneral(tree, name, type, location, hide=collapse):
    nodes = tree.nodes
    
    # Make value node
    
    node = nodes.new(type)
    node.location = location
    node.name = name
    node.label = name
    
    # Collapse nodes
    
    node.hide = hide
    
    return node
    

def createTexture(tree, layer, name, filename, location):
    
    # Make image texture node
    
    textureNode = createGeneral(tree, name, "ShaderNodeTexImage", location)
    
    # Try to apply texture
    
    if filename != None:
        
        textureNode.image = prepareImage(filename)
        
        print("Loaded " + filename + " as " + name)
        
        # Set color space
    
        if name in nonColorMaps:
            textureNode.image.colorspace_settings.name = "Non-Color"
            
        else:
            textureNode.image.colorspace_settings.name = "sRGB"
        
    # Find UV map    
    
    textureUV = name + "UseUV"
    
    if name == "roughnessMap":
        textureUV2 = name + "UV1"
        
    elif name == "baseColorMap" or name == "colorMap":
        textureUV2 = "diffuseMapUseUV"
    
    else:
        textureUV2 = None
    
    if textureUV2 in layer:
        textureUV = textureUV2    
         
    if textureUV in layer:
        
        uvMap = createGeneral(tree, textureUV, "ShaderNodeUVMap", (location[0] - 180, location[1]))
        
        # BeamNG orders UV's by order, I can't do that yet
                        
        uvName = "UVMap"
        if layer[textureUV]:
            uvName += ".00" + str(layer[textureUV])
        
        
        try:
            uvMap.uv_map = uvName
            
        except:
            print("Couldn't find UV Map order " + layer[textureUV] + ", Reverting to default")
            
            try:
                uvMap.uv_map = "UVMap"
            
            except:
                print("There is something terribly wrong with the UVs!")
        
        tree.links.new(uvMap.outputs[0], textureNode.inputs[0])
        
    # Return node
    
    return textureNode


def createMix(tree, name, type, location):
    
    # Make mix node
    
    mixNode = createGeneral(tree, name, "ShaderNodeMixRGB", location)
    
    # Set blend type
    
    mixNode.blend_type = type
    
    # Defualt factor to 1
    
    mixNode.inputs[0].default_value = 1
    
    # Default colors to 1
    
    mixNode.inputs[1].default_value = (1, 1, 1, 1)
    mixNode.inputs[2].default_value = (1, 1, 1, 1)
    
    return mixNode
    
def replaceMaterials(objects, oldMaterial, newMaterial):
    
    for obj in objects:
        old = bpy.data.materials[oldMaterial]
        new = bpy.data.materials[newMaterial]
        # Iterate over the material slots and replace the material
        for s in obj.material_slots:
            if s.material.name == oldMaterial:
                s.material = new



def makeLayer(tree, name, layer, location, materialName):
    nodes = tree.nodes
    
    # Make skin data
    
    if "colorPaletteMap" in layer:
        
        skinData = createGeneral(tree, name + " Skin Map", "ShaderNodeGroup", (location[0] - 3000, location[1] - 400), False)
        
        skinData.node_tree = skinApplier
        
        skin = createTexture(tree, layer, "colorPaletteMap", layer["colorPaletteMap"], (location[0] - 3300, location[1] - 400))
        
        tree.links.new(skin.outputs[0], skinData.inputs[0])
        
    # Make BSDF
    
    bsdf = createGeneral(tree, name, "ShaderNodeBsdfPrincipled", location, False)
    
    # Reset all attributes
    
    for input in bsdf.inputs:
        try:
            input.default_value = 0
        except:
            pass
    
    bsdf.inputs["Alpha"].default_value = 1
    bsdf.inputs["Specular"].default_value = 0
    
    # For every attribute...
    
    for connection in bsdfConnections:
        input = bsdf.inputs[connection]
        output = None
        textureList = bsdfConnections[connection]
        texturesLocation = (location[0] - 600 * len(textureList) - 200, location[1] - 80 - 22 * connection)
        # Make a chain
        
        multiplier = None
        
        sprtOutput = input
        
        for i in range(len(textureList)):
            textureName = textureList[i]
            
            # If it exists
            
            if textureName in layer:
                
                lastMultiplier = multiplier
                
                nodeLocation = (texturesLocation[0] + 600 * i, texturesLocation[1])
                # If it's a map
                
                if textureName.endswith("Map"):
                    node = createTexture(tree, layer, textureName, layer[textureName], nodeLocation)
                    
                    # Does it have a dedicated UV Map?
                                
                elif textureName.endswith("Factor"):
                    if textureName == "baseColorFactor" or textureName == "emissiveFactor":
                        node = createGeneral(tree, textureName, "ShaderNodeRGB", nodeLocation)
                    else:
                        node = createGeneral(tree, textureName, "ShaderNodeValue", nodeLocation)
                    
                    if textureName == "emissiveFactor":
                        layer[textureName].append(1) # Add alpha
                    
                    node.outputs[0].default_value = layer[textureName]
                        
                
                
                elif textureName.endswith("Color"):
                    node = createGeneral(tree, textureName, "ShaderNodeRGB", nodeLocation)
                    node.outputs[0].default_value = layer[textureName]
                    
                # Multiply the textures
                
                multiplier = createMix(tree, "Multiply", "MULTIPLY", (nodeLocation[0] + 300, nodeLocation[1]))
                
                tree.links.new(node.outputs[0], multiplier.inputs[1])
                
                if lastMultiplier != None:
                    tree.links.new(lastMultiplier.outputs[0], multiplier.inputs[2])
                    
                else:
                    sprtOutput = multiplier.inputs[2]
                    
                output = multiplier
                    
                    
        if textureList[0].endswith("_sprt"):
            
            textureName = textureList[0]
                
            if textureName == "colorPaletteMap_sprt":
                
                if "colorPaletteMap" in layer:
                
                    reroutePos = (location[0] - 2500, texturesLocation[1] - 35)
                    
                    reroute = nodes.new("NodeReroute")
                    
                    reroute.location = reroutePos
                
                    if connection == 0:
                        connectNode = skinData.outputs[0]
                
                    if connection == 6:
                        connectNode = skinData.outputs[1]
                        
                    if connection == 9:
                        connectNode = skinData.outputs[2]
                        
                    if connection == 14:
                        connectNode = skinData.outputs[3]
                        
                    if connection == 15:
                        connectNode = skinData.outputs[4]
                     
                    tree.links.new(connectNode, reroute.inputs[0])
                    
                    tree.links.new(reroute.outputs[0], sprtOutput)
            
            if textureName == "specularPower_sprt":
                pass
            
            if textureName == "alpha_sprt":
                if "specularMap" in layer:
                    colorMap = createTexture(tree, layer, "specularMap(Alpha)", layer["specularMap"], texturesLocation)
                    tree.links.new(colorMap.outputs[1], sprtOutput)

                """
                if "colorMap" in layer:
                    colorMap = createTexture(tree, layer, "colorMap(Alpha)", layer["colorMap"], texturesLocation)
                    tree.links.new(colorMap.outputs[1], sprtOutput)
                    
                
                if "diffuseColor" in layer:
                    alpha = createGeneral(tree, "diffuseColor(Alpha)", "ShaderNodeValue", texturesLocation)
                    alpha.outputs[0].default_value = layer["diffuseColor"][3]
                    tree.links.new(alpha.outputs[0], sprtOutput)
                """
                
            
            if textureName == "normal_sprt":
                
                if "normalMap" in layer:
                    
                    # There is no blue channel(usually), Add one ourselves
                    
                    normalMap = createTexture(tree, layer, "normalMap", layer["normalMap"], (texturesLocation[0] - 200, texturesLocation[1]))
                    
                    separateRGB = nodes.new("ShaderNodeSeparateRGB")
                    separateRGB.location = texturesLocation[0]+100, texturesLocation[1]
                    
                    combineRGB = nodes.new("ShaderNodeCombineRGB")
                    combineRGB.location = texturesLocation[0] + 300, texturesLocation[1]
                    
                    normalApplier = nodes.new("ShaderNodeNormalMap")
                    normalApplier.location = texturesLocation[0] + 500, texturesLocation[1]
                    
                    tree.links.new(normalMap.outputs[0], separateRGB.inputs[0])
                    tree.links.new(separateRGB.outputs[0], combineRGB.inputs[0])
                    tree.links.new(separateRGB.outputs[1], combineRGB.inputs[1])
                    combineRGB.inputs[2].default_value = 1
                    tree.links.new(combineRGB.outputs[0], normalApplier.inputs[1])
                    tree.links.new(normalApplier.outputs[0], sprtOutput)
                    
                    # Clear coat normal
                    
                    tree.links.new(normalApplier.outputs[0], bsdf.inputs[23])
                    
                    normalUVName = "UVMap"
                    
                    if "normalMapUseUV" in layer:
                        
                        if layer["normalMapUseUV"]:
                            normalUVName += ".00" + str(layer["normalMapUseUV"])
                    
                    normalApplier.uv_map = normalUVName
            
            if textureName == "emissive_sprt":
                
                sprtOutput.default_value = 1
            
        # Connect to BSDF
        if output != None:
            tree.links.new(output.outputs[0], input)
            
    return bsdf
    
    
                
            
            
            
            
        
class BeamNGTexture:
    def __init__(self, vehicle, material, textures):
        self.textureName = material.name
        self.material = material
        self.layers = textures
        self.vehicle = vehicle
        
    def apply(self):
        
        # Set up material

        self.material.use_nodes = True
        tree = self.material.node_tree
        nodes = tree.nodes
        
        # Clear Material
        
        nodes.clear()
        
        # Remove empty layers
        
        self.layers = list(filter(None, self.layers))
        
        layerMixer = None    
    
        for i in range(len(self.layers)):
            layer = self.layers[i]
            
            for texture in layer:
                layer[texture] = preparePath(layer[texture])
            
            lastLayerMixer = layerMixer
            
            position = (4000 * i, 0)
            
            
            
            bsdf = makeLayer(tree, "Layer " + str(i), layer, position, self.textureName)
            
            # Mix layers according to opacityMap
            
            layerMixer = createGeneral(tree, "LayerMixer " + str(i-1) + str(i), "ShaderNodeMixShader", (position[0] + 300, position[1] + 100))
            
            tree.links.new(bsdf.outputs[0], layerMixer.inputs[2])
            
            # Opacity Factors are opacityMap, colorMap, and 1 (in that order)
            
            if i != 0:
                tree.links.new(lastLayerMixer.outputs[0], layerMixer.inputs[1])
                
            if i == 0 and "colorMap" not in layer:
                transparentBSDF = createGeneral(tree, "Transparent BSDF", "ShaderNodeBsdfTransparent", (position[0] + 100, position[1] + 100))
                tree.links.new(transparentBSDF.outputs[0], layerMixer.inputs[1])
                
            if "opacityMap" in layer:
                opacityMap = createTexture(tree, layer, "opacityMap", layer["opacityMap"], (position[0], position[1] + 130))
                tree.links.new(opacityMap.outputs[0], layerMixer.inputs[0])
            
            elif "colorMap" in layer and i != 0:
                colorMap = createTexture(tree, layer, "colorMap", layer["colorMap"], (position[0], position[1] + 130))
                tree.links.new(colorMap.outputs[1], layerMixer.inputs[0])
            
            else:
                layerMixer.inputs[0].default_value = 1
                
        # Don't render faces with wrong normals (This is used by some BeamNG models)
                
        normalMixer = createGeneral(tree, "Normal selector", "ShaderNodeMixShader", (position[0] + 500, position[1] + 100))
        
        geometryNode = createGeneral(tree, "Geometry", "ShaderNodeNewGeometry", (position[0] + 300, position[1] + 400), False)
        
        transparentNormalBSDF = createGeneral(tree, "Transparent Normal BSDF", "ShaderNodeBsdfTransparent", (position[0] + 300, position[1]))
        
        output = createGeneral(tree, "Output", "ShaderNodeOutputMaterial", (position[0] + 700, position[1] + 100))
        
        tree.links.new(geometryNode.outputs["Backfacing"], normalMixer.inputs[0])
        
        tree.links.new(layerMixer.outputs[0], normalMixer.inputs[1])
        
        tree.links.new(transparentNormalBSDF.outputs[0], normalMixer.inputs[2])
        
        tree.links.new(normalMixer.outputs[0], output.inputs[0])
                
                
def searchJSON(file, prefix, firstLoaded, appendToFailed):   
    
    try:
        with open(file) as f: 
            jsonContents=json.load(f)
            
    except:
        if appendToFailed:
            failedJsons.append(file)
        return False
    
    loadedTextures = []
    
    for material in jsonContents:
        materialBlueprint = jsonContents[material]
        materialName = materialBlueprint["name"]


        for mat in bpy.data.materials:
            if materialName == mat.name and firstLoaded:
                loadedTextures.append((mat, materialBlueprint, "NEW"))

            if prefix + materialName == mat.name:
                loadedTextures.append((mat, materialBlueprint, "NORMAL"))

            if "beamng_common." + materialName == mat.name:
                loadedTextures.append((mat, materialBlueprint, "COMMON"))
         
    return loadedTextures
       
    
    
def loadTextures(vehicle, vehicleName, useCommon, firstLoaded, objects):
    
    vehicleFiles = [preparePath("/vehicles/" + vehicle + "/main.materials.json"),
                preparePath("/vehicles/" + vehicle + "/skin.materials.json")]
    
    usedFiles = []
    
    commonFiles = []
    for (dirpath, dirnames, filenames) in os.walk(filepathBase + "/vehicles/common"):
        commonFiles += [os.path.join(dirpath, file) for file in filenames]
    
    for file in commonFiles:
        if file.endswith(".materials.json"):
            usedFiles.append(file)
            
    comprehensiveList = []
    
    for file in vehicleFiles:
        requiredMaterials = searchJSON(file, vehicleName + ".", firstLoaded, False)

        if requiredMaterials == False:
            continue

        for mat in requiredMaterials:
            comprehensiveList.append(mat)

    for file in usedFiles:
        requiredMaterials = searchJSON(file, vehicleName + ".", firstLoaded, True)

        if requiredMaterials == False:
            continue

        for mat in requiredMaterials:
            comprehensiveList.append(mat)

    for i in comprehensiveList:
        material = i[0]
        blueprint = i[1]
        type = i[2]

        removeLater = False
        load = True

        if type == "NEW":
            
            if useCommon:

                # Does it already exist

                if "beamng_common." + material.name in bpy.data.materials:
                    replaceMaterials(objects, material.name, "beamng_common." + material.name)

                    bpy.data.materials.remove(material)

                    continue

                # If it contains a skin

                skin = False

                for layer in blueprint["Stages"]:
                    if "colorPaletteMap" in layer:
                        skin = True

                if skin:
                    material.name = vehicleName + "." + material.name

                else:
                    material.name = "beamng_common." + material.name
            
            else:
                
                material.name = vehicleName + "." + material.name

        elif type == "NORMAL":
            if useCommon:
                # If it contains a skin

                skin = False

                for layer in blueprint["Stages"]:
                    if "colorPaletteMap" in layer:
                        skin = True
                if skin:
                    pass

                else:
                    if "beamng_common." + blueprint["name"] in bpy.data.materials:
                        oldMaterial = material
                        material = bpy.data.materials["beamng_common." + blueprint["name"]]
                        replaceMaterials(objects, oldMaterial.name, material.name)
                        removeLater = True
                        load = False
                

        elif type == "COMMON":
            if not useCommon:
                oldMaterial = material
                material = bpy.data.materials.new(name=vehicleName + "." + blueprint["name"])
                replaceMaterials(objects, oldMaterial.name, material.name)

            else:
                load = False

        
        print(material.name)

        if load:
            materialClass = BeamNGTexture(vehicleName, material, blueprint["Stages"])

            materialClass.apply()

        if removeLater:
            bpy.data.materials.remove(oldMaterial)
        


    
   
    if failedTextures != []:
    
        print("Failed to load these textures:")
   
    for texture in failedTextures:
        print(texture + "\n")
        
        
    if ddsTextures != []:
        print("These textures are still .dds:")
    
    for texture in ddsTextures:
        print(texture + "\n")
        
    print("Failed to read these JSON files:")
   
    for file in failedJsons:
        print(file + "\n")
        
        
    

    



def loadNew(name, vehicle, filepath, useCommon):
    
    # Find imported objects/images
    
    pastObjects = []
    pastImages = []
    loadedObjects = []
    
    for object in bpy.data.objects:
        pastObjects.append(object.name)
        
    for image in bpy.data.images:
        pastImages.append(image.name)
    
    try:
        bpy.ops.import_scene.gltf(filepath=filepath)
    
    except:
        pass
    
    # Find loaded objects
    
    for object in bpy.data.objects:
        if object.name not in pastObjects:
            loadedObjects.append(object)

    # Delete loaded images    
            
    for image in bpy.data.images:
        if image.name not in pastImages:
            bpy.data.images.remove(image)
            
    # Move objects into Collection        
            
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    
    for object in loadedObjects:
        
        for coll in object.users_collection:
            
            # Unlink the object
            
            coll.objects.unlink(object)
        
        collection.objects.link(object)
    
    # Make new skinApplier

    loadSkinApplier(name + " Skin Applier")

    # Load textures        
    
    loadTextures(vehicle, name, useCommon, True, loadedObjects)



def reload(vehicletype, collection, useCommon):
    
    getSkinApplier(collection.name)

    loadTextures(vehicletype, collection.name, useCommon, False, collection.objects)


