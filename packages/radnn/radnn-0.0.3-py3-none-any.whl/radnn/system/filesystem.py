# ......................................................................................
# MIT License

# Copyright (c) 2018-2025 Pantelis I. Kaplanoglou

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ......................................................................................

import os
from radnn.core import system_name
from radnn.system.filestore import FileStore
from radnn.system.files import JSONFile




# =======================================================================================================================
class FileSystem(object):
  # --------------------------------------------------------------------------------------------------------
  def __init__(self, config_folder=None, model_folder=None, dataset_folder=None, model_group=None, must_exist=False, setup_filename=None):
    '''
    Initializes the file system settings for an experiment
    :param config_folder: The folder that contains the experiment hyperparameter files.
    :param model_folder: The main folder where the models are stored.
    :param dataset_folder: The main folder under which dataset folder are stores.
    :param model_group: A group of models under the main folder will be used instead.
    :param setup_filename: The filename of the setup file.
    :param must_exist: False: Auto-creates the directories on the file system | True: Raises an error if it does not exist.
    '''

    self.setup_filename = setup_filename
    if self.setup_filename is None:
      self.setup_filename = system_name() + ".fsys"

    if os.path.exists(self.setup_filename):
      oFile = JSONFile(self.setup_filename)
      dSetup = oFile.load()
      config_folder = dSetup["Configs"]
      model_folder = dSetup["Models"]
      dataset_folder = dSetup["Datasets"]
      if model_group is None:
        if "ModelGroup" in dSetup:
          model_group = dSetup["ModelGroup"]
    else:
      dSetup = dict()
      dSetup["Configs"] = config_folder
      dSetup["Models"] = model_folder
      dSetup["Datasets"] = dataset_folder

    if model_group is not None:
      config_folder   = os.path.join(config_folder, model_group)
      model_folder    = os.path.join(model_folder, model_group)

    # ...................... | Fields | ......................
    self.setup = dSetup
    self.configs   = FileStore(config_folder, must_exist=must_exist)
    self.models    = FileStore(model_folder, must_exist=must_exist)
    self.datasets  = FileStore(dataset_folder, must_exist=must_exist)
    # ........................................................
  # --------------------------------------------------------------------------------------------------------
  def save_setup(self):
    oFile = JSONFile(self.setup_filename)
    oFile.save(self.setup)
  # --------------------------------------------------------------------------------------------------------
  def __str__(self)->str:
    sResult = f"  ConfigsFolder: \"{self.configs.base_folder}\",\n"
    sResult += f"  ModelsFolder: \"{self.models.base_folder}\",\n"
    sResult += f"  DatasetsFolder: \"{self.datasets.base_folder}\"\n"
    sResult = "{\n" + sResult + "}"
    return sResult
  # --------------------------------------------------------------------------------------------------------
  def __repr__(self)->str:
    return self.__str__()
  # --------------------------------------------------------------------------------------------------------
# =======================================================================================================================
