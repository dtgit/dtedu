#
#To avoid updating of all modules using the visualizing tools
#here all visualizing modules should be added to the __all__ list
#which are then imported by:
#from PlagDetector.Visualize import *
#
#Please also update statNames which is a dictonary used for
#referencing the statistics in the PlagVisualizer.py etc.
#


__all__ = ["dotplot", "htmlMaker", "torc", "heatmap", "patterngram", "statistics"]

try:
    import statistics
except ImportError:
    pass

#statNames = {"", ""}
