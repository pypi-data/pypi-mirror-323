from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
  name='handler_reviews_lib',
  version='1.1.2',
  author='1mlnmyfavoriteinteger',
  author_email='romansergeev7680@gmail.com',
  description='This is the module for work with handlers of reviews by templates or GPT',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='',
  packages=find_packages(),
  install_requires=['requests>=2.25.1', 'openai>=1.40.3',
                    'httpx>=0.28.1', 'tiktoken>=0.7.0',
                    'pydantic>=2.8.2','setuptools>=72.1.0'],
  classifiers=[
    'Programming Language :: Python :: 3.12',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='reviews, handler',
  project_urls={
    'GitHub': 'https://github.com/Azakaim'
  },
  python_requires='>=3.6'
)
