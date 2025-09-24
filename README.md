glxinfo | grep "OpenGL version"
python setup.py bdist_wheel --plat-name linux_x86_64 2>&1 | tee build.log
