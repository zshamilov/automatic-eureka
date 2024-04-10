from faker import Faker
from uuid import uuid4
import datetime
import random


class Generator:
    def __init__(self, customers: list):
        self.faker = Faker()
        self.customers = customers

    @staticmethod
    def choice(seq, weights):
        return random.choices(seq, weights=weights)[0]

    def rto(self) -> dict:
        utrnno: str = f'{random.randint(100, 99999)}'
        virtual_number: str = f'{random.randint(1, 1000000)}'
        auth_date: str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        auth_amt: str = f'{random.randint(0, 2000000)}'
        auth_curr: str = f'{self.choice([810, random.randint(100, 999)], [80, 20])}'
        trans_commission: str = f'{self.choice([0, random.randint(1, 5000)], [75, 25])}'
        state_name: str = self.choice(['HOLD', 'SUCCESS', 'REJECT'], [10, 80, 10])
        trans_subtype: str = self.choice(['CREDIT', 'ZACHISLENIE', 'POKUPKA'], [10, 10, 80])
        mcc: str = f'{self.choice([4722, 4723, random.randint(1000, 9999)], [50, 30, 20])}'
        total_amt: str = f'{random.randint(0, 5000000)}'
        country: str = self.choice(['RUSSIAN FEDERATION', 'TODO'], [90, 10])
        city: str = self.choice(['MOSKVA', 'TODO'], [70, 10])
        reversal: str = self.choice(['true', 'false'], [15, 85])
        gold_customer_id: str = f'{self.choice([random.choice(self.customers), None], [95, 5])}'

        return {
            'UTRNNO': utrnno,
            'VIRTUAL_NUMBER': virtual_number,
            'AUTH_DATE': auth_date,
            'AUTH_AMT': auth_amt,
            'AUTH_CURR': auth_curr,
            'TRANS_COMMISSION': trans_commission,
            'STATE_NAME': state_name,
            'TRANS_SUBTYPE': trans_subtype,
            'MCC': mcc,
            'TOTAL_AMT': total_amt,
            'COUNTRY': country,
            'CITY': city,
            'REVERSAL': reversal,
            'GOLD_CUSROMER_ID': gold_customer_id
        }

    def nbo(self) -> dict:
        gcid: str = random.choice(self.customers)
        channel: str = self.choice(
            ['mobile', 'ib', 'ufo', 'ufo-cc', 'ufo-dsa'],
            [20, 20, 20, 20, 20]
        )
        callpoint: str = self.choice(
            ['catalog', 'burst', 'showcase', '063/01', '063/02', '063/03', 'TODO'],
            [10, 10, 10, 10, 10, 10, 40]
        )
        service_code: str = self.choice(
            [123, 456, 21, 22, 32, random.randint(10, 999)],
            [10, 10, 10, 10, 10, 50]
        )
        service_name: str = self.choice(
            ['тема для КК(1)', 'тема для КК(2)', 'тема для ПК(1)', 'тема для ПК(2)', 'тема для НС', 'TODO'],
            [10, 10, 10, 10, 10, 50]
        )
        birthdate: str = self.faker.date_between(datetime.date(1930, 1, 1), datetime.date(2007, 1, 1))\
            .strftime('%Y-%m-%d')

        return {
            'GCID': gcid,
            'channel': channel,
            'callpoint': callpoint,
            'serviceCode': service_code,
            'serviceName': service_name,
            'birthdate': birthdate
        }

    @staticmethod
    def key() -> dict:
        return {'key': f'{uuid4()}'}
