from setuptools import setup, find_packages  # Add find_packages

package_name = 'm5_udp_listener'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(),  
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='scai-lab',
    maintainer_email='icra_laptop@example.com',
    description='UDP listener package for M5StickC Plus data reception',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # Update paths to match your directory structure
            'udp_listener = m5_udp_listener.m5_listener.m5_listener:main',
            'udp_listener_multiple = m5_udp_listener.m5_listener.m5_listener_multiple:main',
        ],
    },
)