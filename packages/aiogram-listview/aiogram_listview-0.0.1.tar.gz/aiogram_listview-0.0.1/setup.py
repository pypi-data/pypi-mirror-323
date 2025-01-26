from setuptools import setup, find_packages

setup(
    name="aiogram_listview",
    version="0.0.1",
    description="txt",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    url="https://github.com/JustKovalchuk/AiogramListView",
    author="JustKovalchuk",
    author_email="kovalchuk.oleksandr.dev@gmail.com",
    install_requires=[
        "aiogram >= 3.17.0"
    ],
    extra_require={
        "dev": ["twine>4.0.2"]
    },
    python_requires=">=3.12"
)