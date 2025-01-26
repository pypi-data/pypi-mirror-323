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
  sPlatform = platform.system()
  sHostName = socket.gethostname()
  #sIPAddress = socket.gethostbyname(sHostName)

  bIsColab = "google.colab" in sys.modules
  if bIsColab:
    sResult = "(colab)" #+ sIPAddress
  else:
    if sPlatform == "Windows":
      sResult = "(windows)-" + sHostName
    else:
      sResult = "(linux)-" + sHostName
  return sResult
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