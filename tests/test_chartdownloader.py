import pathlib

import pytest

import spotifycharts as sc


test_samples = [('viral50', 'daily', ['global'], '2019-12-30', '2020-01-08', 1),
                ('viral50', 'weekly', ['global'], '2019-12-30', '2020-01-08', 1),
                ('viral50', 'daily', ['germany', 'france'], '2019-12-30', '2020-01-05', None),
                ('viral50', 'weekly', ['germany', 'france'], '2019-12-30', '2020-01-05', None),
                ('top200', 'daily', ['global'], '2019-12-30', '2020-01-08', 1),
                ('top200', 'weekly', ['global'], '2019-12-30', '2020-01-08', 1),
                ('top200', 'daily', ['germany', 'france'], '2019-12-30', '2020-01-05', None),
                ('top200', 'weekly', ['germany', 'france'], '2019-12-30', '2020-01-05', None)]


@pytest.mark.parametrize('name, periodicity, region_names, begin_date, end_date, cpu_count',
                         test_samples)
def test_chartdownloader(name,
                         periodicity,
                         region_names,
                         begin_date,
                         end_date,
                         cpu_count):
    tested_directory_path = pathlib.Path('tests').joinpath('charts',
                                                           'tested')
    tested = sc.ChartDownloader(name=name,
                                periodicity=periodicity,
                                region_names=region_names,
                                begin_date=begin_date,
                                end_date=end_date,
                                cpu_count=cpu_count,
                                directory_path=tested_directory_path)
    untested_directory_path = pathlib.Path('tests').joinpath('charts',
                                                             'untested')
    untested = sc.ChartDownloader(name=name,
                                  periodicity=periodicity,
                                  region_names=region_names,
                                  begin_date=begin_date,
                                  end_date=end_date,
                                  cpu_count=cpu_count,
                                  directory_path=untested_directory_path)
    assert all([tested[region_name].equals(untested[region_name])
                for region_name in tested.region_names])
