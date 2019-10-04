from setuptools import setup, find_packages

setup(
    name="may",
    version="0.1",
    py_modules=find_packages(),
    install_requires=[
        "Click",
        "dateparser",
        "quickconfig",
        "docsep @ git+ssh://git@github.com/Hazelfire/docsep@master",
        "jinja2"
    ],
    entry_points="""
    [console_scripts]
    may=may:cli
    """,
)
