import os
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='smallslive-metrics-app',
    version='0.1',
    packages=['metrics'],
    include_package_data=True,
    license='BSD License',  # example license
    description='',
    long_description='',
    url='http://www.appsembler.com/',
    author='Filip Jukic',
    author_email='filip@appsembler.com',
    install_reqs=[
        'Django==1.8.3',
        'djangorestframework==3.1.3'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)