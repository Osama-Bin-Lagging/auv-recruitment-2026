from setuptools import setup

setup(
    name="auv_controller",
    version="1.0.0",
    packages=["auv_controller"],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/auv_controller"]),
        ("share/auv_controller", ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="AUV-IITB",
    license="MIT",
    entry_points={
        "console_scripts": [
            "controller_node = auv_controller.controller_node:main",
        ],
    },
)
