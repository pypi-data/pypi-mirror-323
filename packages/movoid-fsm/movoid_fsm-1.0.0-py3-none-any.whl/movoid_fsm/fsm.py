#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# File          : fsm
# Author        : Sun YiFan-Movoid
# Time          : 2025/1/25 22:07
# Description   : 
"""
from typing import List, Union, Dict

from movoid_function import wraps


class FsmRule:
    """
    这个是个单独的FSM类，用于基于一个模板创建一个FSM的对象
    """

    def __init__(self, status: List[str], action: Union[List[List[Union[str, List[str]]]], Dict[str, Dict[str, str]]] = None):
        self._status_list = []
        for i in status:
            i = str(i)
            if i in self._status_list:
                raise KeyError(f'repeated status:{i}')
            else:
                self._status_list.append(i)
        if len(self._status_list) == 0:
            raise ValueError('no status exist!')
        self._status_list_dict = {_v: _i for _i, _v in enumerate(status)}
        self._action_dict = {}
        if isinstance(action, dict):
            for action_name, action_dict in action.items():
                action_name = str(action_name)
                self._action_dict[action_name] = {}
                for status_ori, status_tar in action_dict.items():
                    status_ori = self._check_status_exist(status_ori)
                    status_tar = self._check_status_exist(status_tar)
                    self._action_dict[action_name][status_ori] = status_tar
        elif action:
            for status_ori_index, action_list in enumerate(action):
                if status_ori_index < len(self._status_list):
                    status_ori = self._status_list[status_ori_index]
                else:
                    raise IndexError(f'there is only {len(self._status_list)} kind of status. no index of {status_ori_index}.')
                for status_tar_index, action_name_list in enumerate(action_list):
                    if status_tar_index < len(self._status_list):
                        status_tar = self._status_list[status_tar_index]
                    else:
                        raise IndexError(f'there is only {len(self._status_list)} kind of status. no index of {status_tar_index}.')
                    if isinstance(action_name_list, (tuple, list, set)):
                        for action_name in action_name_list:
                            action_name = str(action_name)
                            self._action_dict.setdefault(action_name, {})
                            self._action_dict[action_name][status_ori] = status_tar
                    else:
                        action_name = str(action_name_list)
                        self._action_dict.setdefault(action_name, {})
                        self._action_dict[action_name][status_ori] = status_tar

        self._status = self._status_list[0]

    @property
    def status(self) -> str:
        return self._status

    def when(self, *valid_status,
             setup_action: str = None,
             return_action: str = None,
             exception_action: str = None,
             final_action: str = None,
             ):
        """
        作为装饰器使用，仅当在某些状态下时，可以运行后续内容
        :param valid_status: 有效的status
        :param setup_action: 执行前进行的action操作
        :param return_action: 运行结束后，没有错误时，执行的action
        :param exception_action: 运行结束后，有错误时，执行的action
        :param final_action: 运行结束后，无论错误与否，执行的action
        """

        def dec(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if self._status in valid_status:
                    if setup_action:
                        self.do(setup_action)
                    re_value = None
                    re_exception = None
                    try:
                        re_value = func(*args, **kwargs)
                    except Exception as err:
                        re_exception = err
                        if exception_action:
                            self.do(exception_action)
                    else:
                        if return_action:
                            self.do(return_action)
                    finally:
                        if final_action:
                            self.do(final_action)
                    if re_exception is None:
                        return re_value
                    else:
                        raise re_exception
                else:
                    raise Exception(f'now status is {self._status} not in {valid_status}.')

            return wrapper

        return dec

    def do(self, action_name: Union[str, List[str], Dict[str, str]]):
        """
        执行某个动作，实现status切换
        :param action_name: 动作名称/动作规则
        """
        if isinstance(action_name, (list, set, tuple)):
            if len(action_name) == 2:
                status_ori, status_tar = action_name
                status_ori = self._check_status_exist(status_ori)
                status_tar = self._check_status_exist(status_tar)
                self.check_status_now(status_ori)
                self._status = status_tar
                return
            elif len(action_name) == 1:
                action_name = action_name[0]
            else:
                raise ValueError(f'input should be length of 1 or 2. but now is {len(action_name)}:{action_name}')
        elif isinstance(action_name, dict):
            action_rule = action_name
            if self._status in action_rule:
                self._status = action_rule[self._status]
                return
            else:
                raise AttributeError(f'temp action only change {list(self._action_dict.keys())}, but now is {self._status}')
        if action_name in self._action_dict:
            action_rule = self._action_dict[action_name]
            if self._status in action_rule:
                self._status = action_rule[self._status]
            else:
                raise AttributeError(f'action [{action_name}] should only change {list(self._action_dict.keys())}, but now is {self._status}')

    def _check_status_exist(self, status: str):
        """检查status是否存在。会强制转换为str，并且返回status字符串"""
        status = str(status)
        if status in self._status_list:
            return status
        else:
            raise ValueError(f'status [{status}] does not exist')

    def _check_action_exist(self, action: str):
        """检查action是否存在，会强制转换为str，并且返回action字符串"""
        action = str(action)
        if action in self._action_dict:
            return action
        else:
            raise ValueError(f'action [{action}] does not exist')

    def check_status_now(self, status: str):
        """检查当前的status是否是目标status"""
        status = self._check_status_exist(status)
        if self._status != status:
            raise AttributeError(f'now status is {self._status},not {status}')


class Fsm:
    def __init__(self):
        self._rule = {}

    def add_rule(self, key: str, status: List[str], action: Union[List[List[Union[str, List[str]]]], Dict[str, Dict[str, str]]] = None, update_when_exist=False):
        key = str(key)
        if key in self._rule:
            if update_when_exist:
                raise KeyError(f'key [{key}] has already exist')
        self._rule[key] = FsmRule(status, action)

    def __getitem__(self, key: str) -> FsmRule:
        key = str(key)
        return self._rule[key]

    def __getattr__(self, key: str) -> FsmRule:
        if key in self._rule:
            return self._rule[key]
        else:
            raise KeyError(f'no rule is [{key}]')

    def get(self, key: str, default=None) -> FsmRule:
        key = str(key)
        return self._rule.get(key, default)


FSM = Fsm()
