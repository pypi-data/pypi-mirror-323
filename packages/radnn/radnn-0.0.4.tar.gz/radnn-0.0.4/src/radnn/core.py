import sys
import socket
import platform
import subprocess
from datetime import datetime
import importlib.util


# ----------------------------------------------------------------------------------------------------------------------
def is_opencv_installed():
    return importlib.util.find_spec("cv2") is not None
# ----------------------------------------------------------------------------------------------------------------------




# ----------------------------------------------------------------------------------------------------------------------
def system_name() -> str:
  return MLInfrastructure.host_name(False)
# ----------------------------------------------------------------------------------------------------------------------
def now_iso():
  return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
# ----------------------------------------------------------------------------------------------------------------------
def shell_command_output(command_string):
  oOutput = subprocess.check_output(command_string, shell=True)
  oOutputLines = oOutput.decode().splitlines()

  oResult = []
  for sLine in oOutputLines:
      oResult.append(sLine)

  return oResult
# ----------------------------------------------------------------------------------------------------------------------






#TODO: macOS support

class MLInfrastructure(object):
  # ----------------------------------------------------------------------------------------------------------------------
  @classmethod
  def is_linux(cls):
    return not (cls.is_windows or cls.is_colab)
  # ----------------------------------------------------------------------------------------------------------------------
  @classmethod
  def is_windows(cls):
    sPlatform = platform.system()
    return (sPlatform == "Windows")
  # ----------------------------------------------------------------------------------------------------------------------
  @classmethod
  def is_colab(cls):
    return "google.colab" in sys.modules
  # ----------------------------------------------------------------------------------------------------------------------
  @classmethod
  def host_name(cls, is_using_ip_address=True) -> str:
    sPlatform = platform.system()
    sHostName = socket.gethostname()
    sIPAddress = socket.gethostbyname(sHostName)

    bIsColab = "google.colab" in sys.modules
    if bIsColab:
      sResult = "(colab)"
      if is_using_ip_address:
        sResult += "-" + sIPAddress
    else:
      if sPlatform == "Windows":
        sResult = "(windows)-" + sHostName
      else:
        sResult = "(linux)-" + sHostName
    return sResult
  # ----------------------------------------------------------------------------------------------------------------------
