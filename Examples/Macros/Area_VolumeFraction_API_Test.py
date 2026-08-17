# @CommandService cs
#@ DatasetIOService io
#@ UIService ui
#@ ConvertService convertService
# @Context ctxt

#@ String image
#@ String table_csv
#@ String outputdir

from ij import IJ
from net.imagej import Dataset
import csv

#Prevents unicode error 
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from net.imagej import ImgPlus
from net.imagej.axis import Axes
from net.imglib2.img import Img

from net.imagej import DefaultDataset
import ij.ImagePlus;
from io.scif.img import ImgOpener
from org.bonej.utilities import SharedTable
from ij import ImagePlus
import net.imagej.ImgPlus;
from ij.io import FileSaver


#Open image from path
outputdir
IJ.run("Clear BoneJ results");
# hops patch (2026-08-12, corrected 2026-08-13): current BoneJ (7.2.2, whatever
# "latest" on the update site resolves to) renamed ElementFractionWrapper's input
# from `inputImage` (ImagePlus) to `inputDataset` (net.imagej.Dataset). Also:
# process must be True, not False — inputDataset carries
# @Parameter(validater = "validateImage"), and that validator (which is also
# what populates the plugin's internal state before run()) only executes as
# part of SciJava's parameter-processing pipeline, which process=False skips
# entirely; with False the field is never actually assigned before run() reads
# it, producing a NullPointerException instead of a clean cancellation.
#
# Getting the Dataset via `io.open(image)` (DatasetIOService) directly — as the
# first pass of this patch did — loads the array correctly but silently drops
# NRRD voxel calibration: every axis comes back with unit=None, scale=1.0
# regardless of the file's spacings/units header (tried both the legacy
# "spacings"+"units" fields and the modern "space directions"+"space units"
# convention; neither is read). ElementFractionWrapper's elementSize ends up 1
# instead of the real per-voxel volume, so BV/TV (a ratio) was still correct but
# the absolute BV/TV *values* came back in raw voxel counts, not µm³ — confirmed
# by TV exactly matching the volume's total voxel count (1059*979*2018) in an
# earlier verification run.
#
# `IJ.open()` (the legacy IJ1 IO used since Fiji 1.0) reads NRRD calibration
# correctly (verified: pixelWidth/Height/Depth all pick up 25.0, unit 'µm'), and
# converting that already-calibrated ImagePlus via ConvertService preserves it
# onto the Dataset ElementFractionWrapper needs — confirmed axis-by-axis.
IJ.open(image)
imp = IJ.getImage()
dataset = convertService.convert(imp, Dataset)
wrapperBV = cs.run("org.bonej.wrapperPlugins.ElementFractionWrapper", True, ["inputDataset",dataset])
wrapperBVInstance = wrapperBV.get()

#Save results to csv file 
table =SharedTable.getTable()
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


			

			
