import sys
import arcpy
import os

cwd = sys.argv[1]
arcpy.env.workspace = cwd
# arcpy.env.overwriteOutput = True

output_dir = cwd + "/Reprojected"
cs_Project = int(sys.argv[2])
output_cs_Project = arcpy.SpatialReference(cs_Project)
transformation = sys.argv[3]

cs_Define = int(sys.argv[4])
output_cs_Define = arcpy.SpatialReference(cs_Define)

# Walk through directories and grab files to be projected
input_files = []
for root, dirs, files in os.walk(cwd):
	for name in files:
		extension = name.split(".")[-1]
		if (extension == "shp" or extension == "gdb"):
			input_files.append(name)

# Run through list of files, project, and define
for file in input_files:
	spatial_ref = arcpy.Describe(file).spatialReference
	print(file, spatial_ref.name, spatial_ref.PCSName, spatial_ref.PCSCode)

	# Project to spatial reference 2930
	if spatial_ref.PCSCode == 2930 or spatial_ref.PCSCode == 6609:
		# print(file + " already in " + spatial_ref.PCSName)
		# print("Skipping")
		continue
	elif spatial_ref.name == "Unknown":
		# print("Unknown SR for " + file)
		input_cs = output_cs_2930
		arcpy.Project_management(in_dataset=file,
								in_coor_system=input_cs,
								out_dataset=output_dir + "/" + file,
								out_coor_system=output_cs_2930)
	elif spatial_ref.name == "NAD_1927_StatePlane_Wisconsin_South_FIPS_4803":
		# print("Known SR for " + file + ": " + spatial_ref.name)
		arcpy.Project_management(in_dataset=file,
								out_dataset=output_dir + "/" + file,
								out_coor_system=output_cs_2930,
								transform_method=transformation)
	else: # Catches any other spatial references
		# print("Known SR for " + file + ": " + spatial_ref.name + ", Code = " + str(spatial_ref.PCSCode))
		arcpy.Project_management(in_dataset=file,
								out_dataset=output_dir + "/" + file,
								out_coor_system=output_cs_2930)

	# Define projection from SR 2930 -> 6609
	if spatial_ref.PCSCode == 6609:
		continue
	else: # Catches any other spatial references
		arcpy.DefineProjection_management(in_dataset=file,
                                        coor_system=output_cs_6609)