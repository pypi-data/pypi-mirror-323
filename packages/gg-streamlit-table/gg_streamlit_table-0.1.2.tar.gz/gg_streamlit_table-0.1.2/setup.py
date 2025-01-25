"""
This is a setup file for the gg-streamlit-table package.
"""

import setuptools

setuptools.setup(
    name="gg-streamlit-table",
    version="0.1.2",
    author="Gaurang Kulkarni",
    author_email="gaurangak@example.com",
    description="A custom table component for Streamlit with actions and styling",
    long_description="""# Streamlit Custom Table
    A custom table component for Streamlit with actions, styling, and Material icons.""",
    long_description_content_type="text/markdown",
    url="https://github.com/gaurangak/gg-streamlit-table",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
        "gg_streamlit_table": [
            "template/my_component/frontend/build/*",
            "template/my_component/frontend/build/**/*",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "streamlit>=1.0.0",
        "pandas>=1.0.0",
    ],
)
