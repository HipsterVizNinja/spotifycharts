import pathlib

import pytest
import pandas as pd

import spotifycharts as sc


test_samples = [('viral50', 'daily', 'global'),
                ('viral50', 'weekly', 'global'),
                ('viral50', 'daily', 'france'),
                ('viral50', 'weekly', 'france'),
                ('top200', 'daily', 'global'),
                ('top200', 'weekly', 'global'),
                ('top200', 'daily', 'france'),
                ('top200', 'weekly', 'france')]


@pytest.mark.parametrize('name, periodicity, region_name',
                         test_samples)
def test_download_dates(name,
                        periodicity,
                        region_name):
    region_name = region_name.replace(' ', '_')
    file_name = f'{name}_{periodicity}_{region_name}_dates.csv'
    directory_path = pathlib.Path('tests').joinpath('test_download_dates',
                                                    'tested',
                                                    name,
                                                    periodicity)
    directory_path.mkdir(parents=True,
                         exist_ok=True)
    file_path = directory_path.joinpath(file_name)
    tested = pd.read_csv(file_path)
    tested = tested['chart_date'].tolist()
    untested = sc.download_dates(name=name,
                                 periodicity=periodicity,
                                 region_name=region_name.replace('_', ' '))
    untested = set([date.format('YYYY-MM-DD')
                    for date in untested])
    assert untested.issuperset(tested)
    untested = sorted(list(untested),
                      reverse=False)
    untested = pd.DataFrame({'chart_date': list(untested)})
    untested.to_csv(file_path,
                    index=False)
