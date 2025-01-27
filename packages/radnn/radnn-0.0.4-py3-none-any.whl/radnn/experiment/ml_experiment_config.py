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
import re
from datetime import datetime

from radnn.system import FileSystem

# --------------------------------------------------------------------------------------
def legacy_model_code(config_dict):
  if "ModelName" in config_dict:
    sCode = config_dict["ModelName"]
    if "ModelVariation" in config_dict:
      sCode += "_" + config_dict["ModelVariation"]
    if "ExperimentNumber" in config_dict:
      sCode = sCode + "_%02d" % config_dict["ExperimentNumber"]
  else:
    raise Exception("Invalid experiment configuration. Needs at least the key 'ModelName'.")
  return sCode
# --------------------------------------------------------------------------------------
def get_experiment_code(config_dict):
  if ("Experiment.BaseName" in config_dict) and ("Experiment.Number" in config_dict):
    sBaseName = config_dict["Experiment.BaseName"]
    nNumber = int(config_dict["Experiment.Number"])
    sVariation = None
    if "Experiment.Variation" in config_dict:
      sVariation = str(config_dict["Experiment.Variation"])
    nFoldNumber = None
    if "Experiment.FoldNumber" in config_dict:
      nFoldNumber = int(config_dict["Experiment.FoldNumber"])

    sCode = f"{sBaseName}_{nNumber:02d}"
    if sVariation is not None:
      sCode += "." + sVariation
    if nFoldNumber is not None:
      sCode += f"-{nFoldNumber:02d}"
  else:
    raise Exception("Invalid experiment configuration. Needs at least two keys 'Experiment.BaseName'\n"
                  + "and `Experiment.Number`.")

  return sCode
# --------------------------------------------------------------------------------------
def get_experiment_code_ex(base_name, number, variation=None, fold_number=None):
  if (base_name is not None) and (number is not None):
    nNumber = int(number)
    sVariation = None
    if variation is not None:
      sVariation = str(variation)
    nFoldNumber = None
    if fold_number is not None:
      nFoldNumber = int(fold_number)

    sCode = f"{base_name}_{nNumber:02d}"
    if variation is not None:
      sCode += "." + sVariation
    if nFoldNumber is not None:
      sCode += f"-{nFoldNumber:02d}"
  else:
    raise Exception("Invalid experiment code parts. Needs a base name and a number.")

  return sCode
# --------------------------------------------------------------------------------------
def experiment_number_and_variation(experiment_code):
  if type(experiment_code) == int:
    nNumber = int(experiment_code)
    sVariation = None
  else:
    sParts = experiment_code.split(".")
    nNumber = int(sParts[0])
    if len(sParts) > 1:
      sVariation = sParts[1]
    else:
      sVariation = None

  return nNumber, sVariation
# --------------------------------------------------------------------------------------
def experiment_code_and_timestamp(filename):
  sName, _ = os.path.splitext(os.path.split(filename)[1])
  sParts = re.split(r"_", sName, 2)
  sISODate = f"{sParts[0]}T{sParts[1][0:2]}:{sParts[1][2:4]}:{sParts[1][4:6]}"
  sExperimentCode = sParts[2]
  dRunTimestamp = datetime.fromisoformat(sISODate)
  return sExperimentCode, dRunTimestamp
# --------------------------------------------------------------------------------------






# =========================================================================================================================
class MLExperimentConfig(dict):
  # --------------------------------------------------------------------------------------
  def __init__(self, filename=None, base_name=None, number=None, variation=None, fold_number=None, hyperparams=None):
    self["Experiment.BaseName"] = base_name
    self.filename = filename
    if self.filename is not None:
      self.load()

    if number is not None:
      self["Experiment.Number"] = number
    if variation is not None:
      self["Experiment.Variation"] = variation
    if fold_number is not None:
      self["Experiment.FoldNumber"] = fold_number

    if hyperparams is not None:
      self.assign(hyperparams)
  # --------------------------------------------------------------------------------------
  @property
  def experiment_code(self):
    return get_experiment_code(self)
  # --------------------------------------------------------------------------------------
  def load(self, filename=None, must_exist=False):
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
  def save_config(self, fs, filename_only=None):
    if isinstance(fs, FileSystem):
      fs = fs.configs

    if filename_only is None:
      filename_only = get_experiment_code(self)

    sFileName = fs.file(filename_only + ".json")
    return self.save(sFileName)

  # --------------------------------------------------------------------------------------
  def load_config(self, fs, filename_only):
    if isinstance(fs, FileSystem):
      fs = fs.configs

    sFileName = fs.file(filename_only + ".json")
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


  