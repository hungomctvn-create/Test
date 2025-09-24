"""Copyright 2020-2022 The MediaPipe Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Setup for MediaPipe package with setuptools.
"""

import glob
import os
import platform
import posixpath
import re
import shlex
import shutil
import subprocess
import sys

import setuptools
from setuptools.command import build_ext
from setuptools.command import build_py
from setuptools.command import install

__version__ = '0.10.21'
MP_DISABLE_GPU = True  # Bổ sung: Bỏ qua GPU để tránh lỗi gl_context.cc trong môi trường ảo
IS_WINDOWS = (platform.system() == 'Windows')
IS_MAC = (platform.system() == 'Darwin')
MP_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
MP_DIR_INIT_PY = os.path.join(MP_ROOT_PATH, 'mediapipe/__init__.py')
MP_THIRD_PARTY_BUILD = os.path.join(MP_ROOT_PATH, 'third_party/BUILD')
MP_ROOT_INIT_PY = os.path.join(MP_ROOT_PATH, '__init__.py')

GPU_OPTIONS_DISBALED = ['--define=MEDIAPIPE_DISABLE_GPU=1']

GPU_OPTIONS_ENBALED = [
    '--copt=-DTFLITE_GPU_EXTRA_GLES_DEPS',
    '--copt=-DMEDIAPIPE_OMIT_EGL_WINDOW_BIT',
    '--copt=-DMESA_EGL_NO_X11_HEADERS',
    '--copt=-DEGL_NO_X11',
]
if IS_MAC:
  GPU_OPTIONS_ENBALED.append(
      '--copt=-DMEDIAPIPE_GPU_BUFFER_USE_CV_PIXEL_BUFFER'
  )

GPU_OPTIONS = GPU_OPTIONS_DISBALED  # Ghi đè để đảm bảo CPU-only

def _normalize_path(path):
  return path.replace('\\', '/') if IS_WINDOWS else path

def _get_backup_file(path):
  return path + '.backup'

def _parse_requirements(path):
  with open(os.path.join(MP_ROOT_PATH, path)) as f:
    return [
        line.rstrip()
        for line in f
        if not (line.isspace() or line.startswith('#'))
    ]

def _get_long_description():
  with open(os.path.join(MP_ROOT_PATH, 'README.md')) as f:
    long_description = f.read()
  return long_description

def _get_backup_file(path):
  return path + '.backup'

class BazelExtension(setuptools.Extension):
  """A C/C++ extension that is defined as a Bazel BUILD target."""

  def __init__(self, bazel_target):
    self.bazel_target = bazel_target
    name = self.bazel_target.replace('//', '')
    name = name.replace(':', '.')
    name = name.replace('/', '.')
    ext_path = os.path.join(MP_ROOT_PATH, name.replace('.', os.path.sep))
    setuptools.Extension.__init__(self, name, sources=[])


class BuildExtension(build_ext.build_ext):

  def run(self):
    for ext in self.extensions:
      if isinstance(ext, BazelExtension):
        self.bazel_build(ext)
    build_ext.build_ext.run(self)

  def bazel_build(self, ext):
    if not os.path.exists(self.build_temp):
      os.makedirs(self.build_temp)
    bazel_argv = [
        'bazel',
        'build',
        '-c',
        'opt',
    ] + GPU_OPTIONS + [ext.bazel_target]
    self.spawn(bazel_argv)
    ext_path = os.path.join(MP_ROOT_PATH, self.get_ext_fullpath(ext.name))
    ext_dest_dir = os.path.dirname(ext_path)
    if not os.path.exists(ext_dest_dir):
      os.makedirs(ext_dest_dir)
    shutil.copyfile(
        os.path.join(MP_ROOT_PATH, 'bazel-bin', ext.bazel_target.replace('//', '').replace(':', '/')),
        ext_path)


class BuildPy(build_py.build_py):

  def run(self):
    self.run_command('gen_protos')
    self.run_command('build_modules')
    build_py.build_py.run(self)

class GeneratePyProtos(setuptools.Command):
    """Command to generate Python protobuf files."""
    description = 'generate Python protobuf files'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        proto_files = glob.glob(os.path.join(MP_ROOT_PATH, 'mediapipe/**/*.proto'), recursive=True)
        out_dir = os.path.join(MP_ROOT_PATH, 'build', 'lib.%s-cpython-%s' % (
            platform.machine(), sys.version_info.minor))
        os.makedirs(out_dir, exist_ok=True)
        for proto_file in proto_files:
            if not proto_file.endswith('_test.proto'):
                relative_path = os.path.relpath(proto_file, MP_ROOT_PATH)
                output_file = os.path.join(out_dir, relative_path.replace('.proto', '_pb2.py'))
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                # Bổ sung flag --experimental_allow_proto3_optional để khắc phục lỗi proto3 optional
                subprocess.check_call([
                    'protoc', '-I', MP_ROOT_PATH, '--experimental_allow_proto3_optional',
                    '--python_out', out_dir, proto_file
                ])

class GenerateMetadataSchema(setuptools.Command):
    """Command to generate flatbuffer schema Python files for metadata."""
    description = 'generate flatbuffer schema Python files for metadata'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        schema_path = os.path.join(MP_ROOT_PATH, 'mediapipe/tasks/metadata/metadata_schema.fbs')
        out_path = os.path.join(MP_ROOT_PATH, 'mediapipe/tasks/python/metadata/metadata_schema_py.py')
        subprocess.check_call([
            'flatc', '--python', '-o', os.path.dirname(out_path), '-I', os.path.dirname(schema_path), schema_path
        ])

class BuildModules(setuptools.Command):
    """Command to build MediaPipe Python modules."""
    description = 'build MediaPipe Python modules'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.run_command('generate_metadata_schema')

class Install(install.install):
    """Command to install MediaPipe package."""

    def run(self):
        self.run_command('restore')
        install.install.run(self)

class Restore(setuptools.Command):
    """Command to restore backed up files."""

    description = 'restore backed up files'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for path in glob.glob(os.path.join(MP_ROOT_PATH, '*.backup')):
            shutil.move(path, path[:-7])

setuptools.setup(
    name='mediapipe',
    version=__version__,
    description='MediaPipe is a framework for building multimodal applied ML pipelines.',
    long_description=_get_long_description(),
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(
        exclude=['mediapipe.examples.desktop.*', 'mediapipe.model_maker.*']),
    install_requires=_parse_requirements('requirements.txt'),
    cmdclass={
        'build_py': BuildPy,
        'build_modules': BuildModules,
        'build_ext': BuildExtension,
        'generate_metadata_schema': GenerateMetadataSchema,
        'gen_protos': GeneratePyProtos,
        'install': Install,
        'restore': Restore,
    },
    ext_modules=[
        BazelExtension('//mediapipe/python:_framework_bindings'),
        BazelExtension(
            '//mediapipe/tasks/cc/metadata/python:_pywrap_metadata_version'),
        BazelExtension(
            '//mediapipe/tasks/python/metadata/flatbuffers_lib:_pywrap_flatbuffers'
        ),
    ],
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    license='Apache 2.0',
    keywords='mediapipe',
)