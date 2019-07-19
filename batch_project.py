import arcpy
import os
import sys
##from distutils.dir_util import copy_tree

# cwd = "C:/Users/Communityscience/Desktop/Data"
cwd = os.getcwd()
arcpy.env.workspace = cwd
arcpy.env.overwriteOutput = True

logfile = open(cwd + "\\log.txt", 'w+')
logfile.write("Beginning reprojection of directory " + cwd + " and subdirectories." + "\n")

# coordinate system (spatial reference ID) to Project to (e.g., 2930)
cs_Project = int(sys.argv[1])
output_cs_Project = arcpy.SpatialReference(cs_Project).factoryCode

# geographic coordinate system transformation law
# e.g., "NAD_1927_To_NAD_1983_NADCON + NAD_1983_To_HARN_Wisconsin"
gcs_transformation = sys.argv[2]

# coordinate system to Define to (e.g., 6609)
cs_Define = int(sys.argv[3])
output_cs_Define = arcpy.SpatialReference(cs_Define).factoryCode

# Walk through directories and grab files to be projected
input_files = []
for root, dirs, files in os.walk(cwd):
	for filename in files:
		extension = filename.split(".")[-1]
		if (extension == "gdb"):
			print(filename)
		if (extension == "shp"):
			input_files.append(root + "/" + filename)

# Need handling of geodatabases, .asc, .adf, .tif

# Run through list of files, project, and define
for file in input_files:
	spatial_ref = arcpy.Describe(file).spatialReference
	sr_name = spatial_ref.PCSName
	sr_code = spatial_ref.PCSCode

	output_dataset = file.split(".")[0] + "_Reprojected." + file.split(".")[-1]

	# Project to SR 2930
	logfile.write("\n" + "Running Project to PCSCode " + str(output_cs_Project) + " for " + file + "\n")
	if sr_code == cs_Project or sr_code == cs_Define:
		logfile.write(file + " already in " + sr_name + ", Code = " + str(sr_code) + "\n")
		logfile.write("Skipping." + "\n")
		continue
	elif sr_name == "Unknown":
		logfile.write("Unknown SR for " + file + "\n")
		input_unknown_cs = output_cs_Project
		arcpy.Project_management(in_dataset=file, in_coor_system=input_unknown_cs, out_dataset=output_dataset, out_coor_system=output_cs_Project)
	elif sr_name == "NAD_1927_StatePlane_Wisconsin_South_FIPS_4803":
		logfile.write("Known SR for " + file + ": " + sr_name + ", Code = " + str(sr_code) + "\n")
		arcpy.Project_management(in_dataset=file, out_dataset=output_dataset, out_coor_system=output_cs_Project, transform_method=gcs_transformation)
	else: # Catches any other known spatial references
		logfile.write("Known SR for " + file + ": " + sr_name + ", Code = " + str(sr_code) + "\n")
		arcpy.Project_management(in_dataset=file, in_coor_system=output_cs_Project, out_dataset=output_dataset, out_coor_system=output_cs_Project)

	# Define Projection from SR 2930 -> 6609
	if sr_code == cs_Define:
		continue
	else: # Catches any other spatial references
		logfile.write("Running Define Projection to PCSCode " + str(output_cs_Define) + " for " + output_dataset + "\n")
		arcpy.DefineProjection_management(in_dataset=output_dataset, coor_system=output_cs_Define)

	extensions = ['.cpg', '.dbf', '.prj', '.sbn', '.sbx', '.shp', '.shx', '.shp.xml']
	original_files = [file.split('.')[0] + ext for ext in extensions]
	for data in original_files:
		if os.path.exists(data) == False:
			logfile.write("File " + data + " does not exist.")
			logfile.write("No deletion. Skipping.")
			continue
		else:
			logfile.write("Removing original data: " + data + "\n")
			os.remove(data)

	new_files = [output_dataset.split('.')[0] + ext for ext in extensions]
	#new_files.append(output_dataset.split('.')[0] + ".cpg")
	for data in new_files:
		logfile.write("Renaming reprojected data: " + data + "\n")
		renamed = data.split('_Reprojected')[0] + data.split('_Reprojected')[-1]
		os.rename(data, renamed)

logfile.close()
