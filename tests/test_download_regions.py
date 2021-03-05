import pathlib

import pytest
import pandas as pd

import spotifycharts as sc


test_samples = ['viral50',
                'top200']


@pytest.mark.parametrize('name',
                         test_samples)
def test_download_regions(name):
    file_name = f'{name}_regions.csv'
    directory_path = pathlib.Path('tests').joinpath('regions',
                                                    'tested',
                                                    name)
    directory_path.mkdir(parents=True,
                         exist_ok=True)
    file_path = directory_path.joinpath(file_name)
    tested = pd.read_csv(file_path)
    tested = tested['region_name'].tolist()
    untested = sc.download_regions(name=name)
    untested = set(untested.keys())
    assert untested.issuperset(tested)
    untested = sorted(list(untested),
                      reverse=False)
    untested = pd.DataFrame({'region_name': untested})
    untested.to_csv(file_path,
                    index=False)
