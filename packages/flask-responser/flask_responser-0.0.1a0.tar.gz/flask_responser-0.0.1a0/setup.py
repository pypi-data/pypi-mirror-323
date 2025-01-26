from setuptools import setup, find_packages

setup(
    name="flask_responser",  # 包名称，需唯一
    version="0.0.1alpha",    # 版本号
    author="alex_zhou",
    author_email="alex@ycps.org.cn",
    description="一种新的方式来生成结构化的 JSON 响应，支持开发模式、自定义数据和消息，提升前后端交互的效率与一致性。",
    long_description=open("/root/projects/flask_response/readme").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),  # 自动找到包含 __init__.py 的目录
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=["flask"],  # 列出依赖项，如 ['numpy', 'requests']
)
