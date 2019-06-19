# go to parent directory containing folders of feature layers and classes
cd C:\Users\Communityscience\Desktop\Data

# run python script (in ArcGIS Pro virtual environment)
# arguments: [1] = spatial reference ID (PCSCode) to Project to
#            [2] = geographic coordinate transform
#            [3] = spatial reference ID (PCSCode) to Define Projection to
python ..\arcgis_projections\batch_project.py 2930 "NAD_1927_To_NAD_1983_NADCON + NAD_1983_To_HARN_Wisconsin" 6609
