import os
from setuptools import setup, find_packages

# Đọc nội dung README.md
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="C_healthy",
    version="0.2.2",
    description="A library for calculating body index include: [BMI, BMR, TDEE, HDSD, WHR, LBM, BFP, BBW, IBW, MA, FFMI, RFM, VFR, BSA, VO2MAX, HSI, MMI, BFM]",
    author="Nguyen Truong Chinh",
    author_email="chinhcuber@gmail.com",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["BMI", "BMR", "TDEE", "HDSD", "WHR", "LBM", "BFP", "BBW", "IBW", "MA", "FFMI", "RFM", "VFR", "BSA", "VO2MAX", "HSI", "MMI", "BFM"],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
