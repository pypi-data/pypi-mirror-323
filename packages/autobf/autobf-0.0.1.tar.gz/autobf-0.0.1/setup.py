import setuptools
# 若Discription.md中有中文 須加上 encoding="utf-8"
with open("README.md", "r",encoding="utf-8") as f:
    long_description = f.read()
    
setuptools.setup(
    name = "autobf",
    version = " 0.0.1",
    author = "KuoYuanLi",
    author_email="funny4875.tn@go.edu.tw",
    description="roblox blox fruit tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ai-ky/blocks",                                         packages=setuptools.find_packages(),     
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
    )