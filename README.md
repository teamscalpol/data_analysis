This repository contains code used by University of Maryland Gemstone Team SCALPOL over the course of their project.

TrackMate_macro.py: automates cell tracking in TrackMate for multiple wells in an experiment
  Input: folder containing segmented image sets for each well
  Output: track overlays of each well and folder containing track csvs for all input wells

analysis_code.ipynb: runs ANOVA statistical analysis and graphs for an experiment
  Input: file path to track csv folder generated from the macro, well numbers associated to each treatment group
  Output:
    ANOVA: averages and pairwise p-values for speed and persistence data
    Graphing: speed and persistence violin plots for control wells and treatment groups (separated by cell type)
