from setuptools import setup, find_packages

setup(
    name="june_code_pudding",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'dash',
        'pandas',
        'plotly',
        'numpy',
        'scikit-learn',
        'seaborn',
        'deezer-python',
        'librosa',
        'gunicorn'
    ]
) 