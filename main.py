import pendulum
import pandas as pd
import fastapi
from fastapi import status

import spotifycharts as sc
from spotifycharts import exceptions


downloader = fastapi.APIRouter()


@downloader.get('/regions/{name}',
                status_code=status.HTTP_200_OK)
def download_regions(name):
    try:
        regions = sc.download_regions(name=name)
        regions = {'name': name,
                   'region_names': [*regions]}
        return regions
    except exceptions.ArgumentTypeError as exception:
        raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=str(exception))


@downloader.get('/dates/{name}/{periodicity}/{region_name}',
                status_code=status.HTTP_200_OK)
def download_regions(name,
                     periodicity,
                     region_name):
    try:
        region_name = region_name.replace('_', ' ')
        dates = sc.download_dates(name=name,
                                  periodicity=periodicity,
                                  region_name=region_name)
        dates = {'name': name,
                 'periodicity': periodicity,
                 'region_name': region_name,
                 'dates': [*dates]}
        return dates
    except exceptions.ArgumentTypeError as exception:
        raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=str(exception))


@downloader.get('/charts/{name}/{periodicity}/{region_name}/{begin_date}--{end_date}',
                status_code=status.HTTP_200_OK)
def download_charts(name,
                    periodicity,
                    region_name,
                    begin_date,
                    end_date):
    try:
        region_name = region_name.replace('_', ' ')
        chart_downloader = sc.ChartDownloader(name=name,
                                              periodicity=periodicity,
                                              region_names=[region_name],
                                              begin_date=begin_date,
                                              end_date=end_date,
                                              directory_path='charts')
        charts = chart_downloader[region_name].drop(columns=['region_name'])
        response = {'name': name,
                    'periodicity': periodicity,
                    'region_name': region_name,
                    'charts': []}
        for date, chart in charts.groupby('date',
                                          as_index=True):
            date = pendulum.instance(pd.Timestamp(date).to_pydatetime()).format('YYYY-MM-DD')
            chart = chart.drop(columns=['date']).to_dict(orient='records')
            response['charts'].append({'date': date,
                                       'chart': chart})
        return response
    except exceptions.ArgumentTypeError as exception:
        raise fastapi.HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=str(exception))


api = fastapi.FastAPI()
api.include_router(downloader)
