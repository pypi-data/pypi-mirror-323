from setuptools import setup, find_packages

setup(
    name='aivagent',
    version='0.2.5', # 2024.8.4
    packages= ["aivagent"],
    # find_packages(
    #     include= ["aivagent"]  #指定要打包的包(含 有 __init__.py的模块)
    #     # exclude= ["aivagent.aivmmap", "aivagent.aivbot"]    # 指定排除的模块
    # ), 
    package_data={  # 包含 aivagent 目录下的所有 .pyd 文件 (如果不写,只会包含py代码文件) 2025.1
        'aivagent': ['*.pyd']
    },
    install_requires=[
        "loguru",
        "psutil"
        # 任何依赖项都在这里列出
    ],
    include_package_data=True,  # 确保包含 MANIFEST.in 中指定的文件
    author='aiv.store',
    author_email='76881573@qq.com',
    description='Aiv Agent',
    python_requires='>=3.9',
    # long_description=open('./readme.rts').read(),    #显示在 pypi.org 首页的项目介绍里 2024.6
    license='MIT',
    keywords='Aiv Agent',
    url='https://www.aiv.store'
)