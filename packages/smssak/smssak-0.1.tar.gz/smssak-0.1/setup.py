from setuptools import setup

setup(
    name='smssak',
    version='0.1',
    packages=['smssak'],
    install_requires=['requests'],
    license="MIT",
    license_files=["LICENSE"], # Use this instead of 'license-file'
    description='A package to send and verify OTPs using smssak service.',
    author='Smassak',
    author_email='akreb.corp@gmail.com',
    # url='https://github.com/yourusername/otp_service',
)