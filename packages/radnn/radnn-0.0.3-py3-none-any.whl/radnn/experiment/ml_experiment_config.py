# ......................................................................................
# MIT License

# Copyright (c) 2023-2025 Pantelis I. Kaplanoglou

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
import json


# --------------------------------------------------------------------------------------
def experiment_code(config_dict):
  if ("Experiment.BaseName" in config_dict) and ("Experiment.Number" in config_dict):
    sBaseName = config_dict["Experiment.BaseName"]
    nNumber = int(config_dict["Experiment.Number"])
    sVariation = None
    if "Experiment.Variation" in config_dict:
      sVariation = config_dict["Experiment.Variation"]
    nFoldNumber = None
    if "Experiment.FoldNumber" in config_dict:
      nFoldNumber = config_dict["Experiment.FoldNumber"]

    sCode = "%s_%02d" % (sBaseName, nNumber)
    if sVariation is not None:
      sCode += ".%s" % str(sVariation)
    if nFoldNumber is not None:
      sCode += "-%02d" % int(nFoldNumber)
  else:
    raise Exception("Invalid experiment configuration. Needs at least two keys 'Experiment.BaseName'\n"
                  + "and `Experiment.Number`.")

  return sCode
# --------------------------------------------------------------------------------------





# =========================================================================================================================
class MLExperimentConfig(dict):
  # --------------------------------------------------------------------------------------
  def __init__(self, filename=None, expt_base_name=None, expt_number=None, expt_variation=None, expt_fold=None, hyperparams=None):
    self["Experiment.BaseName"] = expt_base_name
    self.filename = filename
    if filename is not None:
      self.load()

    if expt_number is not None:
      self["Experiment.Number"] = expt_number
    if expt_variation is not None:
      self["Experiment.Variation"] = expt_variation
    if expt_fold is not None:
      self["Experiment.FoldNumber"] = expt_fold

    if hyperparams is not None:
      self.assign(hyperparams)
  # --------------------------------------------------------------------------------------
  @property
  def experiment_code(self):
    return experiment_code(self)
  # --------------------------------------------------------------------------------------
  def load(self, filename, must_exist=False):
    if filename is None:
      filename = self.filename

    # reading the data from the file
    if os.path.exists(filename):
      with open(filename) as oFile:
        sConfig = oFile.read()
        self.setDefaults()
        dConfigDict = json.loads(sConfig)

      for sKey in dConfigDict.keys():
        self[sKey] = dConfigDict[sKey]
    else:
      if must_exist:
        raise Exception("Experiment configuration file %s is not found." % filename)
    return self
  # --------------------------------------------------------------------------------------
  def assign(self, config_dict):
    for sKey in config_dict.keys():
      self[sKey] = config_dict[sKey]

    if (self["Experiment.BaseName"] is None) and ("ModelName" in config_dict):
      self["Experiment.BaseName"] = config_dict["ModelName"]
    if ("DatasetName" in config_dict):
      self["Experiment.BaseName"] += "_" + config_dict["DatasetName"]
    return self
  # --------------------------------------------------------------------------------------
  def save(self, filename):
    if filename is not None:
      self.filename = filename

    sJSON = json.dumps(self, default=lambda o: o.__dict__, sort_keys=False, indent=4)
    with open(self.filename, "w") as oFile:
      oFile.write(sJSON)
      oFile.close()

    return self

  # --------------------------------------------------------------------------------------
  def save_config(self, filesystem, filename_only=None):
    if filename_only is None:
      filename_only = experiment_code(self)

    sFileName = filesystem.configs.file(filename_only + ".json")
    return self.save(sFileName)

  # --------------------------------------------------------------------------------------
  def load_config(self, filesystem, filename_only):
    sFileName = filesystem.configs.file(filename_only + ".json")
    return self.load(sFileName)
  # --------------------------------------------------------------------------------------
  def setDefaults(self):
    pass
  # --------------------------------------------------------------------------------------
  def __str__(self)->str:
    sResult = ""
    for sKey in self.keys():
      sResult += f'  {sKey}: \"{self[sKey]}\",\n'

    sResult = "{\n" + sResult + "}"
    return sResult
  # --------------------------------------------------------------------------------------------------------
  def __repr__(self)->str:
    return self.__str__()
  # --------------------------------------------------------------------------------------------------------

# =========================================================================================================================        


  