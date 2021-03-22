from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy

    def process_item(self, item, spider):
        collection = self.mongo_base['vacancy']

        if spider.name == 'hhru':
            salary_list = []
            for _ in item['salary']:
                s = _.replace(" ", "").replace("\xa0", "")
                salary_list.append(s)
            item['salary'] = salary_list
            if item['salary'][0] == 'от':
                item['salary_min'] = int(item['salary'][1])
                if item['salary'][2] == 'до':
                    item['salary_max'] = int(item['salary'][3])
                    item['currency'] = item['salary'][5]
                else:
                    item['salary_max'] = 'NA'
                    item['currency'] = item['salary'][3]
            elif item['salary'][0] == 'до':
                item['salary_min'] = 'NA'
                item['salary_max'] = int(item['salary'][1])
                item['currency'] = item['salary'][3]
            elif item['salary'][0] == 'з/пнеуказана':
                item['salary_min'] = 'NA'
                item['salary_max'] = 'NA'
            else:
                item['salary_min'] = 'wrong'
                item['salary_max'] = 'wrong'
            del item['salary']

            item['location'] = ' '.join(item['location']).replace("  ", " ").replace(" ,", ",")
            item['company'] = ' '.join(item['company']).replace("\xa0", "").replace("  ", " ").strip()
            item['site'] = 'https://hh.ru'
            item['link'] = item['link'][:item['link'].find('?')]

        if spider.name == 'sjru':
            salary_list = []
            for _ in item['salary']:
                s = _.replace(" ", "").replace("\xa0", "")
                salary_list.append(s)
            item['salary'] = salary_list

            if item['salary'][0] == 'Подоговорённости':
                item['salary_min'] = 'NA'
                item['salary_max'] = 'NA'

            elif item['salary'][2] == '—':
                item['salary_min'] = int(item['salary'][0])
                item['salary_max'] = int(item['salary'][4])
                item['currency'] = item['salary'][6]

            elif item['salary'][0] == 'от':
                pos = item['salary'][2].find('руб.')
                item['salary_min'] = item['salary'][2][:pos]
                item['currency'] = item['salary'][2][pos:]

            elif item['salary'][0] == 'до':
                pos = item['salary'][2].find('руб.')
                item['salary_max'] = item['salary'][2][:pos]
                item['currency'] = item['salary'][2][pos:]

            elif item['salary'][2] == 'руб.':
                item['salary_min'] = item['salary'][0]
                item['salary_max'] = item['salary'][0]
                item['currency'] = item['salary'][2]
            else:
                item['salary_min'] = 'wrong'
                item['salary_max'] = 'wrong'
            del item['salary']

            item['location'] = ' '.join(item['location']).replace("  ", " ")\
                .replace(" ,", ",").replace(" Показать на карте", "")
            item['site'] = 'https://superjob.ru'

        collection.insert_one(item)
        return item