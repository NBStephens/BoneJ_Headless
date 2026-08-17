# @CommandService cs
#@ DatasetIOService io
#@ UIService ui
#@ ConvertService convertService
# @Context ctxt

#@ String image
#@ String spacing_tif
#@ String mapChoice
#@ String table_csv
#@ String showMaps
#@ String maskArtefacts
#@String outputdir
from ij import IJ

import os


from net.imagej import ImgPlus
from net.imagej import Dataset
from net.imagej.axis import Axes
from net.imglib2.img import Img
from net.imagej import DefaultDataset
import ij.ImagePlus;
from io.scif.img import ImgOpener
from org.bonej.utilities import SharedTable
from ij import ImagePlus
from ij.io import FileSaver
#Prevents unicode error
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
#Open image from path
outputdir

# hops patch (2026-08-13): current BoneJ's ThicknessWrapper (shared by both the
# Thickness and Spacing metrics) needs `inputDataset` (net.imagej.Dataset), not
# `inputImage` (ImagePlus) — and process=True, not False, or the
# @Parameter(validater=...) on inputDataset never runs and the field stays null
# (see Area_VolumeFraction's identical fix for the mechanism). Loading through
# `io.open()` (DatasetIOService) directly drops NRRD voxel calibration (every
# axis comes back unit=None, scale=1.0) — IJ.open() reads it correctly, and
# ConvertService preserves it onto the Dataset the wrapper needs.
IJ.run("Clear BoneJ results");
IJ.open(image)
imp = IJ.getImage()
dataset = convertService.convert(imp, Dataset)

wrapper = cs.run("org.bonej.wrapperPlugins.ThicknessWrapper", True,
    ["inputDataset", dataset, "mapChoice", mapChoice, "showMaps", showMaps == "True", "maskArtefacts", maskArtefacts == "True"])
wrapperInstance = wrapper.get()
# hops patch: the output field is now `separationMap` (a Dataset), not the old
# `spacingMap` (an ImagePlus) — and it's saved via DatasetIOService (io.save),
# not the legacy IJ.save which expects an ImagePlus.
separationMap = wrapperInstance.getOutput("separationMap")
if separationMap is not None:
    io.save(separationMap, outputdir + "spacing.tif")

table = SharedTable.getTable()
# print(table)

f = open(outputdir+"table.csv", 'wb')
f.write('\n')
f.write("rowname,")

for j in range(0,len(table[0])):
	f.write(table.getRowHeader(j)+",")
		
f.write('\n')

for i in range(0,len(table)):
	f.write(table.getColumnHeader(i)+",")
	for j in range(0,len(table[i])):
		f.write(str(table[i][j])+",")
	f.write('\n')
f.close()
			
