from setuptools import setup, find_packages

setup(
    name="tzsmmpay-django",
    version="1.0.0",
    description="A Django-compatible Python library for TZSMM Pay API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="TZSMM Pay",
    author_email="info@tzsmmpay.com",
    url="https://github.com/tzsmm-pay/tzsmmpay-django",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "django>=3.2"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
