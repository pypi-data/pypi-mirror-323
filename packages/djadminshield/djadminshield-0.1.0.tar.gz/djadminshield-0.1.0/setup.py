from setuptools import setup, find_packages

setup(
    name="djadminshield",
    version="0.1.0",
    author='Kudamage Rivindhu Venuka Geeneth',
    author_email='rivindhu98@gmail.com',
    description='A Django library to secure the admin panel by faking login pages and logging attempts.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Rivindhu/djadminshield',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[
        'PyYAML==6.0.2',
        'ua-parser==1.0.0',
        'ua-parser-builtins==0.18.0.post1',
        'user-agents==2.2.0',
        ],
    license='MIT',
)