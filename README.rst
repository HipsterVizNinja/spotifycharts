spotifycharts
*************

``spotifycharts`` provides data scientists and music enthusiasts with the simple yet effective out-of-box solution to the problem of obtaining `spotifycharts.com <https://github.com/niltonvolpato/python-progressbar>`__ data.


Installation
############

Dependencies are listed below:

- requests
- pendulum
- pandas
- tqdm
- loguru
- beautifulsoup
- environs

``spotifycharts`` supports only Python 3.

The recommended way to install ``spotifycharts`` is to simply use pip:

.. code:: sh

    pip install spotifycharts


Usage
#####

``ChartDownloader`` class downloads ``name`` charts of ``region_names`` from ``begin_date`` to ``end_date`` on a ``periodicity`` basis with the use of ``cpu_count`` cores saving them into the ``directory_path`` and also grants the access to its corresponding attributes:

.. code:: python

    import spotifycharts as sc
    chart_downloader = sc.ChartDownloader(name='viral50',
                                          periodicity='weekly',
                                          region_names=['germany', 'france'],
                                          begin_date='2019-12-30',
                                          end_date='2020-01-05',
                                          cpu_count=2,
                                          directory_path='data')
    charts = {}
    for region_name in chart_downloader.region_names:
        charts[region_name] = chart_downloader[region_name]

``download_regions`` lists all available regions of ``name`` charts:

.. code:: python

    regions = sc.download_regions(name='top200')

``download_dates`` lists all available dates of ``name`` charts in ``region_name`` on a ``periodicity`` basis:

.. code:: python

    dates = sc.download_dates(name='top200',
                              periodicity='daily',
                              region_name='france')