from setuptools import setup

setup(
    name="auv_sim",
    version="1.0.0",
    packages=["auv_sim"],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/auv_sim"]),
        ("share/auv_sim", ["package.xml"]),
        ("share/auv_sim/launch", ["launch/pinger.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="AUV-IITB",
    license="MIT",
    entry_points={"console_scripts": ["sim_node = auv_sim.sim_node:main"]},
)
