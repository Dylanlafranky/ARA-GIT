#!/bin/bash

## Note: commands below assume a linux system with python 3 installed in /usr/bin/python3, and python files made executable. Files may need editing if used on a different system. 


## process recorded flower sequences

./processPhylloInfo.py cyanellaAlbaFlavescens_final_export.csv


## look for where in the flower sequences the deviations occur from the pattern predicted by the handedness of the phyllotactic spiral

./findDeviationsFromPattern.py  cyanellaAlbaFlavescens_final_export_processed.csv

## Make graphs and analyize data:
mkdir ./graphs
# Analysis runs in R; if the command below does not work, open R and type source("...") as below. 
# Script assumes the directory ./graphs exists 
R -e 'source("analyzePhyllotaxis_clean.R")'
