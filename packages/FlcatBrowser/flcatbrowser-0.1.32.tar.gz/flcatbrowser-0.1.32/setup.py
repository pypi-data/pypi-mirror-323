from setuptools import setup
import pathlib

# 动态加载 requirements.txt
here = pathlib.Path(__file__).parent.resolve()
requirements_path = here / "requirements.txt"

setup(
    name="FlcatBrowser",
    version="0.1.29",
    description="flcat browser",
    author="yhhit",
    author_email="827077539@qq.com",
    packages=["FlcatBrowser", "FlcatBrowser.utils", "FlcatBrowser.plugin", "FlcatBrowser._js"],
    install_requires=requirements_path.read_text().splitlines() if requirements_path.exists() else [],
)