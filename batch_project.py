import arcpy
import os
import sys
from distutils.dir_util import copy_tree

# cwd = "C:/Users/Communityscience/Desktop/Data"
cwd = os.getcwd()
arcpy.env.workspace = cwd
arcpy.env.overwriteOutput = True

output_dir = cwd + "/Reprojected"

# coordinate system (spatial reference ID) to Project to (e.g., 2930)
cs_Project = int(sys.argv[1])
output_cs_Project = arcpy.SpatialReference(cs_Project)

# geographic coordinate system transformation law
# e.g., "NAD_1927_To_NAD_1983_NADCON + NAD_1983_To_HARN_Wisconsin"
gcs_transformation = sys.argv[2]

# coordinate system to Define to (e.g., 6609)
cs_Define = int(sys.argv[3])
output_cs_Define = arcpy.SpatialReference(cs_Define)

# Walk through directories and grab files to be projected
input_files = []
for root, dirs, files in os.walk(cwd):
	for name in files:
		extension = name.split(".")[-1]
		if (extension == "shp" or extension == "gdb"):
			input_files.append(root + "/" + name)

# Run through list of files, project, and define
for file in input_files:
	spatial_ref = arcpy.Describe(file).spatialReference
	sr_name = spatial_ref.PCSName
	sr_code = spatial_ref.PCSCode

	fc_name = file.split("/")[-1]

	# Project to SR 2930
	if sr_code == cs_Project or sr_code == cs_Define:
		print(file + " already in " + sr_name + ", Code = " + str(sr_code), "\n", "Skipping.", "\n")
		continue
	elif sr_name == "Unknown":
		print("Unknown SR for " + file, "\n")
		input_cs = output_cs_Project
		arcpy.Project_management(in_dataset=file,
                                in_coor_system=input_cs,
								out_dataset=output_dir + "/" + fc_name,
								out_coor_system=output_cs_Project)
	elif sr_name == "NAD_1927_StatePlane_Wisconsin_South_FIPS_4803":
		print("Known SR for " + file + ": " + sr_name + ", Code = " + str(sr_code), "\n")
		arcpy.Project_management(in_dataset=file,
								out_dataset=output_dir + "/" + fc_name,
								out_coor_system=output_cs_Project,
								transform_method=gcs_transformation)
	else: # Catches any other spatial references
		print("Known SR for " + file + ": " + sr_name + ", Code = " + str(sr_code), "\n")
		arcpy.Project_management(in_dataset=file,
								out_dataset=output_dir + "/" + fc_name,
								out_coor_system=output_cs_Project)

	# Define Projection from SR 2930 -> 6609
	if sr_code == cs_Define:
		continue
	else: # Catches any other spatial references
		arcpy.DefineProjection_management(in_dataset=output_dir + "/" + fc_name,
										coor_system=output_cs_Define)

# Toy example 
# Better way is probably to write layer to same directory with "_reprojected" appended
# Go through and delete old layers
# Remove "_reprojected" from name

# Copy reprojected layers from output directory back to input directory
source = output_dir
destination = cwd + "/copy"
copy_tree(source, destination)
