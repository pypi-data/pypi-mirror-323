#!/usr/bin/env python3
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_version():
    return 7 #import os
    import re
    import subprocess
    dot_git = os.path.join(os.path.dirname(__file__), '.git')
    changelog = os.path.join(os.path.dirname(__file__), 'debian/changelog')
    if os.path.exists(dot_git):
        cmd = ['git', 'rev-list', 'HEAD', '--count']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        rev = int(stdout)
        return u'%s' % rev
    elif os.path.exists(changelog):
        f = open(changelog)
        head = f.read().strip().split('\n')[0]
        f.close()
        rev = re.compile('\d+\.\d+\.(\d+)').findall(head)
        if rev:
            return "%s" % rev[0]
    return 'unknown'


setup(
    name="pandora-upload",
    version="1.0.%s" % get_version(),
    description="pandora-upload is a commandline uploader for pan.do/ra",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="j",
    author_email="j@mailb.org",
    url="https://code.0x2620.org/0x2620/pandora-upload",
    license="GPLv3",
    packages=['pandora_upload'],
    entry_points={
        'console_scripts': [
            'pandora-upload=pandora_upload:main'
        ]
    },
    install_requires=[
        'ox >= 3',
        'lxml',
    ],
    keywords=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License (GPL)',
    ],
)
