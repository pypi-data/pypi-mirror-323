from setuptools import setup, find_packages

setup(
    name="102203058_Vaishnavi_Topsis",
    version="0.0.1",
    description="TOPSIS Python Package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Vaishnavi",
    author_email="vgera_be22@thapar.edu",
    url="https://github.com/0609Vaish/102203058_Vaishnavi_Topsis",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
    ],
    entry_points={
        "console_scripts": [
            "topsis=102203058_Vaishnavi_topsis.topsis:main",  # Ensure the `main()` function exists in topsis.py
        ],
    },
    python_requires=">=3.6",
)
