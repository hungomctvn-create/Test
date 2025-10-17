 File "/home/hungomctvn/Downloads/gui_chup_anh.py", line 179, in <module>
    main()
    ~~~~^^
  File "/home/hungomctvn/Downloads/gui_chup_anh.py", line 174, in main
    app = CameraGUI(root, save_dir="/home/hungomctvn")
  File "/home/hungomctvn/Downloads/gui_chup_anh.py", line 71, in __init__
    self.picam2.configure(self.preview_config)
    ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/picamera2/picamera2.py", line 1221, in configure
    self.configure_("preview" if camera_config is None else camera_config)
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/picamera2/picamera2.py", line 1143, in configure_
    self.check_camera_config(camera_config)
    ~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
  File "/usr/lib/python3/dist-packages/picamera2/picamera2.py", line 910, in check_camera_config
    raise RuntimeError("Colour space has incorrect type")
RuntimeError: Colour space has incorrect type

