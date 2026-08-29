This DrosophilamelanogasterLongTimescaleData2022readme.txt file was generated on 20230919 by Grace C. McKenzie-Smith

-------------------
GENERAL INFORMATION
-------------------

Title of Dataset: DrosophilamelanogasterLongTimescaleData2022

Author Information (Name, ORCID, Institution, Address, Email)

	Principal Investigator: Joshua W. Shaevitz, 0000-0001-8809-4723, Princeton University, shaevitz@princeton.edu
	Co-first author: Grace C. McKenzie-Smith, 0000-0001-8428-0043, Princeton University, gracecm@princeton.edu
	Co-first author: Scott W. Wolf, 0000-0003-4397-1395, Princeton University, swwolf@princeton.edu
	Associate author: Julien F. Ayroles, 0000-0001-8729-0511, Princeton University, jayroles@princeton.edu

Date of data collection (single date, range, approximate date):
We collected recordings for approximately week-long stretches, with starting dates (in UTC) of:
2023-02-17
2023-03-13
2023-03-26
2023-04-18

Geographic location of data collection:
Princeton, New Jersey, Mercer County, USA

Information about funding sources or sponsorship that supported the collection of the data:
This work was supported in part by the NSF through the Center for the Physics of Biological Function (PHY-1734030). SWW is supported by the NSF Graduate Research Fellowship Program (DGE-2039656). GCM-S is supported by the Paul F. Glenn Laboratories For Aging Research at Princeton University. JFA is funded by grants from the NIH: National Institute of Environmental Health Sciences (R01-ES029929) and National Institute of General Medical Sciences (R35GM124881). We also acknowledge that the work reported in this paper was substantially performed using the Princeton Research Computing resources at Princeton University, which is a consortium of groups led by the Princeton Institute for Computational Science and Engineering (PICSciE) and the Office of Information Technology’s Research Computing group.

--------------------------
SHARING/ACCESS INFORMATION
-------------------------- 

Licenses/restrictions placed on the data, or limitations of reuse:
CC-BY 4.0
Recommended citation for the data:
McKenzie-Smith, G., Ayroles, J., Shaevitz, J., & Wolf, S. (2023). Drosophila melanogaster Long Timescale Data 2022 [Data set]. Princeton University. https://doi.org/10.34770/1SAB-8845

Citation for and links to publications that cite or use the data:
https://doi.org/10.48550/arXiv.2309.04044

Links to other publicly accessible locations of the data:

Links/relationships to ancillary or related data sets: 


--------------------
DATA & FILE OVERVIEW
--------------------

There are 47 hdf5 numerical data files and 47 corresponding Matroska video files. Each file follows the naming convention of date(YYYYMMDD)_cam#_flid#, specifying the date data taking began, the specific camera recording, and the unique ID number for each of the 47 flies. Video files have _video at the end. For example, fly number 1 was recorded with camera 1 beginning 2022-02-17, so the data and video files for that fly are 20220217_cam1_flid1.h5 and 20220217_cam1_flid1_video.mkv in the "final_data" and "videos" folders, respectively.

The hdf5 files contain postural and behavioral data for individual flies over the course of lifetime behavior recordings.

The video files contain the corresponding videos of the individual flies.


--------------------------
METHODOLOGICAL INFORMATION
--------------------------

Description of methods used for collection/generation of data: 
Videos of flies were recorded continuously using FLIR BFS-U3-32S4M-C cameras under 880nm infrared illumination. Videos were acquired, compressed, and saved using campy (https://github.com/Wolfffff/campy), initially developed by Kyle Seversson.
Postural data was extracted from videos using SLEAP (https://sleap.ai)
Postural data was classified into discrete behaviors using MotionMapperPy (https://github.com/bermanlabemory/motionmapperpy)
For full methodological information, see associated paper "Capturing continuous, long timescale behavioral changes in Drosophila melanogaster postural data"


--------------------------
DATA-SPECIFIC INFORMATION <Create sections for each datafile or set, as appropriate>
--------------------------

Each hdf5 file has attributes that define:
start data and time in UTC
lights on time in UTC
lights off time in UTC
video quadrant (each recording captured 4 flies at a time, but data and videos are for individual flies)
camera number
frames per second
the (x,y) coordinates within the corresponding video file for the center of the arena

Each hdf5 file contains datasets:
behavior_names, defining the behavior indices in the 'behaviors' dataset
behaviors, a 1 dimensional array with values for each timepoint which gives discrete numerical indices to describe the behavior for each timepoint
node_names, defining the indices of the tracked body parts in the 'tracks' dataset
on_edge, a 1 dimensional array with values for each timepoint which provides a binary flag for timepoints where the flies are classified as on the edge, with values of 1 indicating on edge points and 0 indicating off edge
relative_humidity, a 1 dimensional array with values for each timepoint provides the relative humidity value for each timepoint
temperature, a 1 dimensional array with values for each timepoint provides the temperature in degrees Celsius for each timepoint
tracks, a timexbodypartxcoord variable that provides the x and y coordinates of each tracked body part for each time point. NaNs indicate times when the body part was occluded/untracked