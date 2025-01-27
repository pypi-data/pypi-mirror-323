import os
from google.colab import drive
from google.colab import files
from radnn.core import MLInfrastructure

COLAB_ROOT_FOLDER = "/content/gdrive/My Drive/Colab Notebooks"

class ColabHost(object):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, colab_root=COLAB_ROOT_FOLDER, workspace_folder=None):
    self.colab_root = colab_root
    self.workspace_prefixes = None
    self.workspace_folder = workspace_folder
    self.current_folder = None

    drive.mount("/content/gdrive")
  # --------------------------------------------------------------------------------------------------------------------
  def detect_workspace(self, prefixes=None):
    self.workspace_prefixes = prefixes

    if self.workspace_prefixes is None:
      self.workspace_folder = self.colab_root
    else:
      self.workspace_folder = None
      for sProjectsFolder in os.listdir(self.colab_root):
        for sPrefix in self.workspace_prefixes:
          if sProjectsFolder.startswith(sPrefix):
            self.workspace_folder = os.path.join(self.colab_root, sProjectsFolder)
            break
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def change_dir(self, path):
    self.current_folder = path
    os.chdir(self.current_folder)
    print("Current directory is: ", os.getcwd())
  # --------------------------------------------------------------------------------------------------------------------
  def change_to_project_dir(self, project_name):
    if self.workspace_folder is not None:
      self.current_folder = os.path.join(self.workspace_folder, project_name)
    else:
      self.current_folder = os.path.join(self.colab_root, project_name)
    os.chdir(self.current_folder)
    print("Current directory is: ", os.getcwd())

    return self
  # --------------------------------------------------------------------------------------------------------
  def __str__(self)->str:
    return f"Host: {MLInfrastructure.host_name()}"
  # --------------------------------------------------------------------------------------------------------
  def __repr__(self)->str:
    return self.__str__()
  # --------------------------------------------------------------------------------------------------------
