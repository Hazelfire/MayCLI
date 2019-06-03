from setuptools import setup, find_packages

setup(
    name="may",
    version="0.1",
    py_modules=find_packages(),
    install_requires=["Click", "dateparser", "quickconfig"],
    entry_points="""
    [console_scripts]
    may=may:cli
    """,
)
