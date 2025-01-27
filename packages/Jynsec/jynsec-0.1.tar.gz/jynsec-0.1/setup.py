from setuptools import setup, find_packages

setup(
    name='Jynsec',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'qrcode[pil]',
        'Pillow',
        'better-profanity', 
    ],
    extras_require={
        "email_support": ["smtplib"],
    },
    author='Jynoqtra',
    author_email='Jynoqtra@gmail.com',
    description='JynPopMod Python Module',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Jynoqtra/JynPopMod',
    classifiers=[  
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
    ],
)
