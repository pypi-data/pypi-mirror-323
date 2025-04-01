from setuptools import setup, find_packages

setup(
    name="thispackagedoesnotexist",
    version="0.1.3",
    packages=find_packages(),
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=[
        "customtkinter",
        "requests",
        "WMI",
        "PyAudio",
        "PyAutoGUI",
        "pillow",
        "opencv-python",
        "psutil",
        "websockets",
    ],
)
