from setuptools import setup, find_packages # 导入setuptools打包工具

setup(
    name='piper_sdk',
    version='0.1.9',    # 包版本号，便于维护版本
    packages=find_packages(include=['piper_sdk', 'piper_sdk.*']),
    include_package_data=True,
    package_data={
        '': ['LICENSE','*.sh','*.MD'],  # 指定包含的文件
        'piper_sdk/asserts': ['*'],  # 包括 asserts 文件夹下的所有文件
    },
    install_requires=[
        'python-can>=3.3.4',
    ],
    entry_points={
    },
    author='RosenYin',  # 作者
    author_email='yinruocheng321@gmail.com',
    description='A sdk to control piper',   #包的简述
    # url="https://github.com/agilexrobotics/piper_sdk",
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',    #对python的最低版本要求,18.04及以上
)

