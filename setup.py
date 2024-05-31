from setuptools import setup, find_packages
import re

# auto-updating version code stolen from orbitize! stolen from RadVel
def get_property(prop, project):
    result = re.search(
        r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop),
        open(project + "/__init__.py").read(),
    )
    return result.group(1)

def get_requires():
    reqs = []
    for line in open("requirements.txt", "r").readlines():
        reqs.append(line)
    return reqs

setup(
    name="RAPHS",
    version=get_property("__version__", "raphs"),
    description="(R)adial velocity (A)nalysis of (P)otential (H)WO (S)tars",
    url="https://github.com/CalebHarada/RAPHS",
    author="Caleb K. Harada",
    author_email="charad@berkeley.edu",
    license="MIT",
    packages=find_packages(),
    entry_points={'console_scripts': ['raphs=raphs.cli:main']},
    keywords="Radial velocity, exoplanets, HWO",
    install_requires=get_requires(),
)