from setuptools import setup, find_packages

setup(
    name="djangoessentials",
    version="0.2.4",
    author="CoderMungan",
    author_email="codermungan@gmail.com",
    description="A lightweight repository-service pattern library for Django applications.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/CoderMungan/DjangoEssentials",
    packages=find_packages(),
    install_requires=[
        "Django>=3.2",
        "django-storages[boto3]>=1.11",
        "djangorestframework>=3.12",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
    ],
    python_requires=">=3.7",
)
