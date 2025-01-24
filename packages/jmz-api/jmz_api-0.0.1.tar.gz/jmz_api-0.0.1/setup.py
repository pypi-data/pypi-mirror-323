from setuptools import setup,find_packages,find_namespace_packages
print(find_packages())

setup(
    name='jmz_api',
    version='0.0.1',
    author='jinmingzhou',
    author_email='17816765317@163.com',
    description='这是作者开发日常写的一些工具库和平台爬虫API工具集合',
    packages=find_namespace_packages(),

)
