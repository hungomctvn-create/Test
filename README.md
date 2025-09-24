glxinfo | grep "OpenGL version"
python setup.py bdist_wheel --plat-name linux_x86_64 2>&1 | tee build.log
git clone https://github.com/google/mediapipe.git mediapipe
python setup.py bdist_wheel --plat-name linux_x86_64
pip install dist/mediapipe-*.whl
python greeting_robot_final.py


ygame 1.9.6
Hello from the pygame community. https://www.pygame.org/contribute.html
Traceback (most recent call last):
  File "/home/robothcc/greeting_robot_final_1.1.py", line 9, in <module>
    mp_face_detection = mp.solutions.face_detection
AttributeError: module 'mediapipe' has no attribute 'solutions'


------------------
(program exited with code: 1)
Press return to continue

python -c "import mediapipe as mp; print(mp.__version__)"
