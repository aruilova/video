from setuptools import setup

setup(
   name='video',
   version='1.0.0',
   description='test module for opening vide file in qt gui window running opencv',
   author='Allen Ruilova',
   author_email='aruilova1@gmail.com',
   packages=['video'],  #same as name
   install_requires=['opencv2', 'PyQt5' ,"imagesize", "numpy", "pytest", "pytest-qt"], #external packages as dependencies
)