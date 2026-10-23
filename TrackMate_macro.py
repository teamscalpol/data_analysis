import sys, os

from ij import IJ, ImagePlus, WindowManager
from ij.plugin import FolderOpener
from ij.io import FileSaver

from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate import Logger

from fiji.plugin.trackmate.detection import MaskDetectorFactory
from fiji.plugin.trackmate.tracking.jaqaman import SparseLAPTrackerFactory

from fiji.plugin.trackmate.gui.displaysettings import DisplaySettings
from fiji.plugin.trackmate.gui.displaysettings import DisplaySettingsIO
from fiji.plugin.trackmate.gui.displaysettings.DisplaySettings import TrackMateObject
from fiji.plugin.trackmate.features.track import TrackIndexAnalyzer

from fiji.plugin.trackmate.io import CSVExporter
from fiji.plugin.trackmate.visualization.table import TrackTableView
from fiji.plugin.trackmate.visualization.table import AllSpotsTableView
from java.io import File

import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
from fiji.plugin.trackmate.action import CaptureOverlayAction

reload(sys)
sys.setdefaultencoding('utf-8')

exp_direc = IJ.getDirectory("Choose Directory")

exp = os.listdir(exp_direc)
for folder in exp:
	if folder.startswith('.'):
		exp.remove(folder)

os.makedirs(exp_direc + 'Tracks/')

for well in exp:
	imp = FolderOpener.open(exp_direc + well)
	dims = imp.getDimensions()
	imp.setDimensions(dims[2], dims[4], dims[3])
	imp.show()

	model = Model()
	model.setLogger(Logger.IJ_LOGGER)
	settings = Settings(imp)

	settings.detectorFactory = MaskDetectorFactory()
	settings.detectorSettings = {
		'TARGET_CHANNEL': 1,
		'SIMPLIFY_CONTOURS': True
	}

	settings.trackerFactory = SparseLAPTrackerFactory()
	settings.trackerSettings = settings.trackerFactory.getDefaultSettings()
	
	# See https://imagej.net/plugins/trackmate/scripting/trackmate-detectors-trackers-keys#the-lap-tracker-sparselaptrackerfactory for settings
	
	# settings.trackerSettings['LINKING_MAX_DISTANCE'] = (float, pos)
	# settings.trackerSettings['LINKING_FEATURE_PENALTIES'] = (dict string->float)
	settings.trackerSettings['ALLOW_GAP_CLOSING'] = True
	settings.trackerSettings['MAX_FRAME_GAP'] = 10
	settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = 100.0
	# settings.trackerSettings['GAP_CLOSING_FEATURE_PENALTIES'] = (dict string->float)
	settings.trackerSettings['ALLOW_TRACK_MERGING'] = False
	# settings.trackerSettings['MERGING_MAX_DISTANCE'] = (boolean)
	# settings.trackerSettings['MERGING_FEATURE_PENALTIES'] = (float, pos)
	settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = False
	# settings.trackerSettings['SPLITTING_MAX_DISTANCE'] = (float, pos)
	# settings.trackerSettings['SPLITTING_FEATURE_PENALTIES'] = (dict string->float)
	# settings.trackerSettings['ALTERNATIVE_LINKING_COST_FACTOR'] = (float)
	# settings.trackerSettings['CUTOFF_PERCENTILE'] = (float, 0 to 1)
	# settings.trackerSettings['BLOCKING_VALUE'] = (float, pos)
	
	settings.addAllAnalyzers()

	trackmate = TrackMate(model, settings)

	if not trackmate.checkInput():
		sys.exit(str(trackmate.getErrorMessage()))
	
	if not trackmate.process():
		sys.exit(str(trackmate.getErrorMessage()))
	
	selectionModel = SelectionModel(model)
	ds = DisplaySettings()

	displayer = HyperStackDisplayer(model, selectionModel, imp, ds)
	displayer.render()
	displayer.refresh()
	
	overlay = CaptureOverlayAction.capture(trackmate, -1, imp.getNFrames(), Logger.IJ_LOGGER)
	FileSaver(overlay).saveAsTiff(exp_direc + well + '_overlay.tif')

	# spot_table = AllSpotsTableView(model, selectionModel, ds, imp.getTitle())
	# spot_table_csv = exp_direc + 'results/' + well + '_spots.csv'
	# spot_table.exportToCsv(spot_table_csv)
	
	track_table = TrackTableView.createTrackTable(model, ds)
	track_table_csv = File(exp_direc + 'Tracks/' + well + '_tracks.csv')
	track_table.exportToCsv(track_table_csv)

	model.getLogger().log(str(model))
	imp.close()
