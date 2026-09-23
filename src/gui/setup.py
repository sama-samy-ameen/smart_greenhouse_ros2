from setuptools import find_packages, setup

package_name = 'gui'


setup(
    name=package_name,
    version='0.0.0',

    packages=find_packages(),

    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),

        (
            'share/' + package_name,
            ['package.xml']
        ),
        ('lib/python3.12/site-packages/gui',
            ['gui/home.ui',
            'gui/data.ui',
            'gui/safety.ui',
            'gui/statistics.ui']),
        
    ],

    install_requires=[
        'setuptools',
    ],

    zip_safe=True,

    description='PyQt5 GUI for the Smart Greenhouse ROS2 system',

    license='Apache License 2.0',

    tests_require=['pytest'],

    entry_points={
        'console_scripts': [
            'gui = gui.main:main',
        ],
    },
)
