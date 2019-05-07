from setuptools import setup, find_packages

setup(name='firex_recorder',
      version="0.1",
      description='Core firex libraries',
      url='https://github.com/FireXStuff/firex-recorder',
      author='Core FireX Team',
      author_email='firex-dev@gmail.com',
      license='BSD-3-Clause',
      packages=find_packages(),
      zip_safe=True,
      entry_points={
          'console_scripts': ['firex_recorder = firex_recorder.__main__:main', ],
          'firex_tracking_service': ['recorder_launcher = firex_recorder.launcher:RecorderLauncher', ]
      },
      install_requires=[
          "firexapp",
      ],)
