import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Chinese2025",
    version="0.0.1",
    author="李岚霏",
    author_email="haizhimenhao@outlook.com",
    description="一个关于中文的集合库，未来会加入更多内容",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yesandnoandperhaps/Chinese2025",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Free for non-commercial use",  # 自定义的分类描述
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    license="MIT (Non-commercial) or Contact Author for Commercial Use",  # 许可证描述
    package_data={
        "Chinese2025": ["reconstructions_list.sqlite"],  # 确保数据库文件打包
    },
    include_package_data=True,
)
