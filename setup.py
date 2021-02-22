from setuptools import setup

packages = \
['spotifycharts']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0',
 'environs>=9.3.1,<10.0.0',
 'loguru>=0.5.3,<0.6.0',
 'pandas>=1.2.2,<2.0.0',
 'pendulum>=2.1.2,<3.0.0',
 'requests>=2.25.1,<3.0.0',
 'tqdm>=4.57.0,<5.0.0']

setup_kwargs = {
    'name': 'spotifycharts',
    'version': '2021.2.22',
    'description': 'The easy-to-use package for downloading Spotify charts with Python.',
    'long_description': "spotifycharts\n*************\n\n``spotifycharts`` provides data scientists and music enthusiasts with the simple yet effective out-of-box solution to the problem of obtaining `spotifycharts.com <https://github.com/niltonvolpato/python-progressbar>`__ data.\n\n\nInstallation\n############\n\nDependencies are listed below:\n\n- requests\n- pendulum\n- pandas\n- tqdm\n- loguru\n- beautifulsoup\n- environs\n\n``spotifycharts`` supports only Python 3.\n\nThe recommended way to install ``spotifycharts`` is to simply use pip:\n\n.. code:: sh\n\n    pip install spotifycharts\n\n\nUsage\n#####\n\n``ChartDownloader`` class downloads ``name`` charts of ``region_names`` from ``begin_date`` to ``end_date`` on a ``periodicity`` basis with the use of ``cpu_count`` cores saving them into the ``directory_path`` and also grants the access to its corresponding attributes:\n\n.. code:: python\n\n    import spotifycharts as sc\n    chart_downloader = sc.ChartDownloader(name='viral50',\n                                          periodicity='weekly',\n                                          region_names=['germany', 'france'],\n                                          begin_date='2019-12-30',\n                                          end_date='2020-01-05',\n                                          cpu_count=2,\n                                          directory_path='data')\n    charts = {}\n    for region_name in chart_downloader.region_names:\n        charts[region_name] = chart_downloader[region_name]\n\n``download_regions`` lists all available regions of ``name`` charts:\n\n.. code:: python\n\n    import spotifycharts as sc\n    regions = sc.download_regions(name='top200')\n\n``download_dates`` lists all available dates of ``name`` charts in ``region_name`` on a ``periodicity`` basis:\n\n.. code:: python\n\n    import spotifycharts as sc\n    dates = sc.download_dates(name='top200',\n                              periodicity='daily',\n                              region_name='france')",
    'author': 'Arthur Meltonyan',
    'author_email': 'arthur.meltonyan@gmail.com',
    'maintainer': 'Arthur Meltonyan',
    'maintainer_email': 'arthur.meltonyan@gmail.com',
    'url': 'https://github.com/arthurmeltonyan/spotifycharts',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
