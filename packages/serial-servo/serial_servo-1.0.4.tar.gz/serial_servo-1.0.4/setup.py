from setuptools import setup, find_packages

# 读取 README 文件内容
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="serial_servo",
    version="1.0.4",
    description="A MicroPython library to control servo motors via UART",
    author="leeqingshui",
    author_email="1069653183@qq.com",
    url="https://github.com/leezisheng/freakstudio-micropython-libraries",
    packages=find_packages(where="serial_servo"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        # 仅使用MicroPython内置模块
    ],
    classifiers=[
        "Programming Language :: Python :: 3",     # 支持 Python 3
        "Programming Language :: Python :: 3.8",   # 支持 Python 3.8
        "License :: Other/Proprietary License",    # 使用 CC BY-NC 4.0 许可证
        "Operating System :: OS Independent",      # 操作系统无关
    ],
    # Python版本要求（适应MicroPython，v1.23.0版本支持的Python版本）
    python_requires='>=3.12',
    # 如果有MicroPython相关的依赖，可以在这里添加
    extras_require={
        # MicroPython的依赖
        'micropython': ['machine', 'time'],
    },
)
