from setuptools import setup, find_packages

setup(
    name="MyPkgAuto2",  # 包名称
    version="0.1.2",    # 初始版本号
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple Python package that says Hello, World!",
    long_description=open("README.md", encoding="utf-8").read() + "\n\n" + open("CHANGELOG.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/helloworld",  # 项目主页
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

