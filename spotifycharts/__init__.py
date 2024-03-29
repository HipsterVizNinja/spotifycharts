import copy
import pathlib
import multiprocessing as mp

import bs4
import requests
import pendulum
import pandas as pd
from tqdm import auto

from spotifycharts import classes
from spotifycharts import settings
from spotifycharts import exceptions
from spotifycharts.logging import logger


mp.set_start_method('fork',
                    force=True)


def download_regions(name):
    name = classes.Name(name)
    name_code = settings.NAME_CODES[name]
    url = f'{settings.SPOTIFY_CHARTS_URL}/{name_code}'
    with requests.Session() as session:
        response = session.get(url)
    regions = {}
    if response.status_code != requests.codes.OK:
        logger.warning(f'{settings.LOG_REGIONS_DOWNLOAD_WARNING} of {name} charts')
        return regions
    parser = bs4.BeautifulSoup(response.text,
                               'html.parser')
    elements = parser.select(settings.REGION_CSS)
    for element in elements:
        region_name = element.text.lower().strip()
        region_code = element.get(settings.REGION_CODE_ATTRIBUTE)
        regions[region_name] = region_code
    logger.info(f'{settings.LOG_REGIONS_DOWNLOAD_INFO} of {name} charts')
    return regions


def download_dates(name,
                   periodicity,
                   region_name):
    name = classes.Name(name)
    periodicity = classes.Periodicity(periodicity)
    region_name = classes.RegionNames(name,
                                      [region_name])[0]
    name_code = settings.NAME_CODES[name]
    periodicity_code = settings.PERIODICITY_CODES[periodicity]
    region_code = download_regions(name)[region_name]
    region_url = f'{settings.SPOTIFY_CHARTS_URL}/{name_code}/{region_code}/{periodicity_code}'
    with requests.Session() as session:
        response = session.get(region_url)
    dates = {}
    if response.status_code != requests.codes.OK:
        logger.warning(f'{settings.LOG_DATES_DOWNLOAD_WARNING} of {region_name} {name} charts on a {periodicity} basis')
        return dates
    parser = bs4.BeautifulSoup(response.text,
                               'html.parser')
    chart_error = parser.select(settings.CHART_ERROR_CSS)
    chart_lost = parser.select(settings.LOST_CHART_CSS)
    if chart_error or chart_lost:
        logger.warning(f'{settings.LOG_DATES_DOWNLOAD_WARNING} of {region_name} {name} charts on a {periodicity} basis')
        return dates
    date_elements = parser.select(settings.DATE_CSS)
    for date_element in date_elements:
        date = pendulum.from_format(date_element.text,
                                    settings.HTML_DATE_FORMAT)
        date = date.date()
        date_codes = []
        time_period = date_element.get(settings.DATE_CODE_ATTRIBUTE)
        for date_code in time_period.split(settings.URL_DATE_DELIMITER):
            date_code = pendulum.from_format(date_code,
                                             settings.URL_DATE_FORMAT)
            date_code = date_code.format(settings.FILE_DATE_FORMAT)
            date_codes.append(date_code)
        dates[date] = settings.URL_DATE_DELIMITER.join(date_codes)
    logger.info(f'{settings.LOG_DATES_DOWNLOAD_INFO} of {region_name} {name} charts on a {periodicity} basis')
    return dates


class ChartDownloader:

    def __init__(self,
                 name,
                 periodicity,
                 region_names,
                 begin_date,
                 end_date,
                 cpu_count=None,
                 directory_path=None):
        self._name = classes.Name(name)
        self._periodicity = classes.Periodicity(periodicity)
        self._region_names = classes.RegionNames(name,
                                                 region_names)
        self._begin_date = classes.BeginDate(begin_date)
        self._end_date = classes.EndDate(end_date)
        if self._begin_date > self._end_date:
            raise exceptions.ArgumentTypeError(settings.DATE_RANGE_ERROR)
        self._cpu_count = classes.CpuCount(cpu_count)
        self._directory_path = classes.DirectoryPath(directory_path)
        name_code = settings.NAME_CODES[self.name]
        periodicity_code = settings.PERIODICITY_CODES[self.periodicity]
        all_regions = download_regions(self.name)
        regions = {}
        for region_name in all_regions:
            if region_name in self.region_names:
                regions[region_name] = all_regions[region_name]
        regions_items = sorted(regions.items(),
                               key=lambda region: region[0])
        regions_items = auto.tqdm(regions_items)
        if self.name == 'top200':
            column_names = copy.deepcopy(settings.TOP200_CHART_COLUMN_NAMES)
        else:
            column_names = copy.deepcopy(settings.VIRAL50_CHART_COLUMN_NAMES)
        column_names.extend(['region_name', 'date'])
        begin_date = self.begin_date.format(settings.FILE_DATE_FORMAT)
        end_date = self.end_date.format(settings.FILE_DATE_FORMAT)
        extension = settings.FILE_EXTENSION
        for region_name, region_code in regions_items:
            file_name = f'{self.name}_{self.periodicity}_charts_from_{begin_date}_to_{end_date}.{extension}'
            directory_path = pathlib.Path(self.directory_path).joinpath(self.name,
                                                                        self.periodicity,
                                                                        region_name)
            directory_path.mkdir(parents=True,
                                 exist_ok=True)
            file_path = directory_path.joinpath(file_name)
            if file_path.exists():
                region_charts = pd.read_csv(file_path,
                                            sep=settings.FILE_DELIMITER,
                                            encoding=settings.FILE_ENCODING)
            else:
                region_charts = pd.DataFrame(columns=column_names)
            file_dates = []
            for file_date in region_charts['date'].unique():
                file_date = pendulum.instance(pd.Timestamp(file_date).to_pydatetime()).date()
                file_dates.append(file_date)
            current_time = pendulum.now().format(settings.PROGRESS_BAR_TIME_FORMAT)
            description = f'{current_time} | {region_name}'
            regions_items.set_description(description)
            all_dates = download_dates(self.name,
                                       self.periodicity,
                                       region_name)
            urls = []
            dates = []
            for date, date_code in all_dates.items():
                if self.begin_date <= date <= self.end_date and date not in file_dates:
                    url = f'{settings.SPOTIFY_CHARTS_URL}/{name_code}/{region_code}/{periodicity_code}/{date_code}'
                    urls.append(url)
                    dates.append(date)
            logger.info(f'{region_name}:{len(urls)}')
            with mp.Pool(self.cpu_count) as pool:
                downloaded_charts = pool.map(classes.Chart,
                                             urls)
            for chart, date in zip(downloaded_charts, dates):
                if not chart.empty:
                    chart['region_name'] = region_name
                    chart['date'] = date
                    chart['date'] = pd.to_datetime(chart['date'])
            if downloaded_charts:
                data = region_charts.append(downloaded_charts,
                                            sort=True)
                data.reset_index(drop=True,
                                 inplace=True)
                data.sort_values(by=['date', 'track_position'],
                                 ascending=[False, True],
                                 inplace=True)
                data = data[column_names]
                data.to_csv(file_path,
                            sep=settings.FILE_DELIMITER,
                            encoding=settings.FILE_ENCODING,
                            index=False)
        regions_items.close()

    def __getitem__(self,
                    region_name):
        if region_name not in self.region_names and self.name == 'top200':
            column_names = copy.deepcopy(settings.TOP200_CHART_COLUMN_NAMES)
            column_names.extend(['region_name', 'date'])
            return pd.DataFrame(column_names)
        elif region_name not in self.region_names and self.name == 'viral50':
            column_names = copy.deepcopy(settings.VIRAL50_CHART_COLUMN_NAMES)
            column_names.extend(['region_name', 'date'])
            return pd.DataFrame(column_names)
        begin_date = self.begin_date.format(settings.FILE_DATE_FORMAT)
        end_date = self.end_date.format(settings.FILE_DATE_FORMAT)
        extension = settings.FILE_EXTENSION
        file_name = f'{self.name}_{self.periodicity}_charts_from_{begin_date}_to_{end_date}.{extension}'
        directory_path = pathlib.Path(self.directory_path).joinpath(self.name,
                                                                    self.periodicity,
                                                                    region_name)
        file_path = directory_path.joinpath(file_name)
        charts = pd.read_csv(file_path,
                             sep=settings.FILE_DELIMITER,
                             encoding=settings.FILE_ENCODING)
        charts['date'] = pd.to_datetime(charts['date'])
        charts['track_position'] = pd.to_numeric(charts['track_position'],
                                                 downcast='unsigned')
        if self.name == 'top200':
            charts['stream_count'] = pd.to_numeric(charts['stream_count'],
                                                   downcast='unsigned')
        return charts

    @property
    def name(self):
        return self._name

    @property
    def periodicity(self):
        return self._periodicity

    @property
    def region_names(self):
        return self._region_names

    @property
    def begin_date(self):
        return self._begin_date

    @property
    def end_date(self):
        return self._end_date

    @property
    def cpu_count(self):
        return self._cpu_count

    @property
    def directory_path(self):
        return self._directory_path
