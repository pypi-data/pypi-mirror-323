from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    author='Daniel Baikalov',
    author_email="felix.trof@gmail.com",
    description="Email notifications are a thing of the past, send notifications to messengers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    name='beep_notifications',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[]
)
