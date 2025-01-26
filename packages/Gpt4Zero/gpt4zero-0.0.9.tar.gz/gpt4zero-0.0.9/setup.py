from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='Gpt4Zero',
    version='0.0.9',
    py_modules=['gpt4zero'],
    install_requires=[
        'requests'
    ],
    description="Gpt4Zero - python библиотека для бесплатного взаимодействия с передовыми нейросетями.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[  
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)