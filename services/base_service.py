"""
AI Trading OS
Base Service
"""

from database.unit_of_work import UnitOfWork


class BaseService:

    def __init__(self):

        self.uow = UnitOfWork()