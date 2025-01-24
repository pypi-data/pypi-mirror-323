import requests
from datetime import date, timedelta
from typing import Optional, Union

class SchApi:
    __url: str
    __method: str

    def __init__(self, url: str = 'http://shspu.ru/sch_api/index.php', method: str = 'get'):
        if method.lower() not in ['get', 'post']:
            exit(0)
        self.__url = url
        self.__method = method

    @staticmethod
    def __get_monday(day: date) -> date:
        return day - timedelta(days=day.weekday(), weeks=0)

    def __send_request(self, params: dict) -> Union[dict,Exception]:
        try:
            req: requests.Response = requests.request(method=self.__method,url=self.__url, params=params)
        except Exception as e:
            return {'error':e}
        result = req.json()
        result = result['result'] if result['ok'] else {'error':result['error'][0]}
        return result

    def groups_get(self) -> dict:
        return self.__send_request(params={'method': 'groups.get'})

    def groups_test(self, group_name: str) -> dict:
        return self.__send_request(params={'method': 'groups.test', 'groupName': group_name})

    def teachers_get(self) -> dict:
        return self.__send_request(params={'method': 'teachers.get'})

    def pairs_get(self, day: date, week:bool, **kwargs) -> dict:
        params: dict = kwargs
        params.update({'method': 'pairs.get', 'date': day, 'week': week})
        return self.__pairs_universal_get(params=params)

    def pairs_confirmable_get(self, day: date, week:bool, **kwargs) -> dict:
        params: dict = kwargs
        params.update({'method': 'pairs.confirmableGet', 'date': day, 'week': week})
        return self.__pairs_universal_get(params=params)

    def __pairs_universal_get(self, params: dict) -> dict:
        params['date'] = self.__get_monday(params['date']) if params['week'] else params['date']
        params['week'] = int(params['week'])
        return self.__send_request(params=params)

    def pairs_bulk_get(self, day: date, group_name:Optional[list[str]]=None, query:Optional[list[str]]=None) -> dict:
        if query is None:
            query = []
        if group_name is None:
            group_name = []
        if len(query)+len(group_name)>=100:
            return {'error':'Общее количество целей поиска любого типа не должно превышать 100'}
        params: dict = {'method': 'pairs.bulkGet','date':day, 'groupName[]':group_name, 'query[]':query}
        return self.__send_request(params=params)

    def pairs_confirmable_bulk_get(self, day: date, group_name: Optional[list[str]] = None, query: Optional[list[str]] = None) -> dict:
        if query is None:
            query = []
        if group_name is None:
            group_name = []
        if len(query)+len(group_name)>=100:
            return {'error':'Общее количество целей поиска любого типа не должно превышать 100'}
        params: dict = {'method': 'pairs.confirmableBulkGet', 'date': day, 'groupName[]': group_name, 'query[]': query}
        return self.__send_request(params=params)

    def updates_get(self, day: date) -> dict:
        res: dict = self.__send_request({'method':'updates.get', 'date': self.__get_monday(day=day)})
        return list(map(lambda x: {'name':x['name'],'faculty_short':x['short_display_name'],'faculty': x['display_name']}, res))
