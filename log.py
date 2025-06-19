import datetime
from typing import Literal

OP_TYPES = Literal['INSERT', 'UPDATE', 'DELETE']

class Logger:
    def add(self, op_type: OP_TYPES, tablename: str,  op_data: str):
        with open('log.txt', 'a', encoding='utf8') as file:
            file.write(f'{datetime.datetime.now()} | {op_type:6} | {tablename:20} | {op_data}\n')