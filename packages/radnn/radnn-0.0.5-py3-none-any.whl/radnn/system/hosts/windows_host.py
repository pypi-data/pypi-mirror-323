import win32api

class WindowsHost(object):
  # --------------------------------------------------------------------------------------------------------------------
  @classmethod
  def dll_info_root(self, dll_filename):
    dInfo = dict()
    ver_strings = ('Comments', 'InternalName', 'ProductName',
                   'CompanyName', 'LegalCopyright', 'ProductVersion',
                   'FileDescription', 'LegalTrademarks', 'PrivateBuild',
                   'FileVersion', 'OriginalFilename', 'SpecialBuild')
    # fname = os.environ["comspec"]
    dFileVersionInfo = win32api.GetFileVersionInfo(dll_filename, '\\')
    ## backslash as parm returns dictionary of numeric info corresponding to VS_FIXEDFILEINFO struc

    for sKey, oValue in dFileVersionInfo.items():
      dInfo[sKey] = oValue
    return dInfo
  # --------------------------------------------------------------------------------------------------------------------
  @classmethod
  def dll_info(cls, dll_filename):
    dInfo = dict()

    dFileVersionsInfo = win32api.GetFileVersionInfo(dll_filename, '\\VarFileInfo\\Translation')
    ## \VarFileInfo\Translation returns list of available (language, codepage) pairs that can be used to retreive string info
    ## any other must be of the form \StringfileInfo\%04X%04X\parm_name, middle two are language/codepage pair returned from above
    dInfo = dict()
    for sLanguageCode, sCodePage in dFileVersionsInfo:
      dInfo["lang"] = sLanguageCode
      dInfo["codepage"] = sCodePage

      #print('lang: ', lang, 'codepage:', codepage)
      oVersionStrings = ('Comments', 'InternalName', 'ProductName',
                     'CompanyName', 'LegalCopyright', 'ProductVersion',
                     'FileDescription', 'LegalTrademarks', 'PrivateBuild',
                     'FileVersion', 'OriginalFilename', 'SpecialBuild')
      for sVersionString in oVersionStrings:
        str_info = u'\\StringFileInfo\\%04X%04X\\%s' % (sLanguageCode, sCodePage, sVersionString)
        dInfo[sVersionString] = repr(win32api.GetFileVersionInfo(dll_filename, str_info))
    return dInfo
  # --------------------------------------------------------------------------------------------------------------------