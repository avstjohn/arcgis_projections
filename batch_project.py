import arcpy
import os
import sys
from distutils.dir_util import copy_tree

# cwd = "C:/Users/Communityscience/Desktop/Data"
cwd = os.getcwd()
arcpy.env.workspace = cwd
arcpy.env.overwriteOutput = True

logfile = open(cwd, 'w+')
logfile.write("Beginning reprojection of directory " + cwd + " and subdirectories.", "\n")

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
	for filename in files:
		extension = filename.split(".")[-1]
		# if (extension == "shp" or extension == "gdb"):
		if (extension == "shp"):
			input_files.append(root + "/" + filename)

# Run through list of files, project, and define
for file in input_files:
	spatial_ref = arcpy.Describe(file).spatialReference
	sr_name = spatial_ref.PCSName
	sr_code = spatial_ref.PCSCode

	# fc_name = file.split("/")[-1]
	output_dataset = file.split(".")[0] + "_Reprojected." + file.split(".")[-1]

	# Project to SR 2930
	logfile.write("Running Project to PCSCode " + str(output_cs_Project) + " for " + file, "\n")
	if sr_code == cs_Project or sr_code == cs_Define:
		logfile.write(file + " already in " + sr_name + ", Code = " + str(sr_code), "\n", "Skipping.", "\n")
		continue
	elif sr_name == "Unknown":
		logfile.write("Unknown SR for " + file, "\n")
		input_cs = output_cs_Project
		arcpy.Project_management(in_dataset=file, in_coor_system=input_cs, out_dataset=output_dataset, out_coor_system=output_cs_Project)
	elif sr_name == "NAD_1927_StatePlane_Wisconsin_South_FIPS_4803":
		logfile.write("Known SR for " + file + ": " + sr_name + ", Code = " + str(sr_code), "\n")
		arcpy.Project_management(in_dataset=file, out_dataset=output_dataset, out_coor_system=output_cs_Project, transform_method=gcs_transformation)
	else: # Catches any other spatial references
		logfile.write("Known SR for " + file + ": " + sr_name + ", Code = " + str(sr_code), "\n")
		arcpy.Project_management(in_dataset=file, out_dataset=output_dataset, out_coor_system=output_cs_Project)
	logfile.write("\n")

	# Define Projection from SR 2930 -> 6609
	if sr_code == cs_Define:
		continue
	else: # Catches any other spatial references
		logfile.write("Running Define Projection to PCSCode" + str(output_cs_Define) + " for " + output_dataset, "\n")
		arcpy.DefineProjection_management(in_dataset=output_dataset, coor_system=output_cs_Define)

	logfile.write("Removing original " + file)
	os.remove(file)
	logfile.write("Renaming reprojected data " + output_dataset)
	os.rename(output_dataset, file)

logfile.close()
