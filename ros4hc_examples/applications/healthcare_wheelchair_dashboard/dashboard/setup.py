from setuptools import setup, find_packages
from glob import glob

package_name = 'dashboard'


# image assets
icons = [ i for i in glob('resource/icons/*.*')]
dash_vectors = [i for i in glob('resource/Dashboard-Vectors/*.*')]
logos = [i for i in glob('resource/logos/*.*')]




setup(
    name=package_name,
    version='1.1.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    data_files=[
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
    ('share/' + package_name + '/resource',
        icons + dash_vectors + logos),
    ('share/' + package_name + '/resource',
        ['resource/form.ui' ]),
    ('share/' + package_name, ['package.xml']),
    ('share/' + package_name, ['plugindash.xml']),
    ],
    
    install_requires=['setuptools'],
    zip_safe=True,
    author='Aaron Blasdel',
    maintainer='Dirk Thomas, Dan Lazewatsky, Michael Lautman',
    maintainer_email='dthomas@osrfoundation.org',
    keywords=['ROS'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    description=(
        'A Python GUI plugin for introspecting available ROS message types.' +
        'Note that the msgs available through this plugin is the ones that are stored ' +
        'on your machine, not on the ROS core your rqt instance connects to.'
    ),
    license='BSD',
    entry_points={
        'console_scripts': [
            'dashboard = ' + package_name + '.main:main',
        ],
    },
)
