from .fileobject import  FileObject
from .jsonfile import JSONFile
from .picklefile import PickleFile
from .textfile import TextFile
from .csvfile import CSVFile

from core import is_opencv_installed
if (is_opencv_installed()):
  from .imgfile import PNGFile
