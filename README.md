
# BeamNGImport
This is a simple Blender addon that reads the materials files of BeamNG cars and applies them automatically. It also does some slight organization of the materials and the meshes.
# How to Use
First of all, Locate the "vehicles" folder of your game files and extract the ZIP file of the vehicle you wish to export, and the "common" file.
Then, convert all the .dds files to .png (Blender doesn't support dds).

You then select the folder the files are in in the Addon Preferences Menu. (Details in the Menu)

Press the 'Import new model' button.

![addonDemo](https://user-images.githubusercontent.com/117572566/200167853-6d29c51d-87c2-4b20-85cb-e01124698e98.png)

Model Filepath: The filepath of the .gltf export

Name: Self-explanatory, No duplicates

Vehicle Type: the internal name of the vehicle, name of the folder

Share Identical Materials: Use the same material whenever possible, NOT FULLY IMPLEMENTED YET

When you press 'Import new model', all the meshes will be put into a collection.

Select Collection: The collection that holds the vehicle meshes
