from setuptools import setup, find_packages

setup(
    name='GetInformationUserID',
    version='0.1',  
    packages=find_packages(),
    description='Получение информации по айди подьзователя, для вывода в основной код Telethon.',
    author='Puxxalwl',
    author_email='ruslan544mc@gmail.com',
    install_requires=["Telethon"],
    classifiers=[ 
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    license='MIT',
)