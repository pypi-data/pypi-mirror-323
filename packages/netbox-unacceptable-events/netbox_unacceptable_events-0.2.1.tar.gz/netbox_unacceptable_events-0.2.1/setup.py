from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='netbox_unacceptable_events',
    version='0.2.1',
    description='Netbox plugin. Assign devices and virtual machines and application systems to information security unacceptable events',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[],
    download_url='https://pypi.org/project/netbox-unacceptable-events/',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    keywords=['netbox', 'netbox-plugin'],
    author='Oleg Senchenko',
    author_email='senchenkoob@mail.ru',
    maintainer='Oleg Senchenko',
    maintainer_email='senchenkoob@mail.ru',
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
