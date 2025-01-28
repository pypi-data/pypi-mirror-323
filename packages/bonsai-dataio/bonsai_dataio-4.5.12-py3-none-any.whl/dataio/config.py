# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 16:05:31 2022

@author: ReMarkt
"""
import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dataio.resources import ResourceRepository


class Config:

    def __init__(self, current_task_name, custom_resource_path=None, **kwargs) -> None:

        self.current_task_name = current_task_name
        self.log_level = logging.WARNING
        self.log_handler = logging.StreamHandler()

        self.custom_resource_path = custom_resource_path

        for key, value in kwargs:
            self.__setattr__(key, value)

    def load_env(self) -> dict:
        from dotenv import load_dotenv

        load_dotenv()

        env_dict = {}

        for key in os.environ:
            env_dict[key] = os.environ[key]
        return env_dict

    @property
    def bonsai_home(self):
        env_dict = self.load_env()
        assert env_dict[
            "BONSAI_HOME"
        ], "Please set up environmental variable for 'BONSAI_HOME'"
        return Path(env_dict.get("BONSAI_HOME", str(Path.home())))

    @property
    def schemas(self):
        from dataio.schemas import bonsai_api

        return bonsai_api

    @property
    def resource_repository(self) -> ResourceRepository:
        from dataio.resources import CSVResourceRepository

        db_path = (
            self.custom_resource_path if self.custom_resource_path else self.bonsai_home
        )

        return CSVResourceRepository(db_path)
