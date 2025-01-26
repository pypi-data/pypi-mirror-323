from radnn import FileSystem

TEST_NUM = 1

if TEST_NUM == 1:
  oSys = FileSystem("MLConfig", "MLModels", "MLData", "DNN")
  oSys.save_setup()
elif TEST_NUM == 2:
  oSys = FileSystem()
  print(oSys)
elif TEST_NUM == 3:
  oSys = FileSystem(setup_filename="test.fsys")
  print(oSys)


