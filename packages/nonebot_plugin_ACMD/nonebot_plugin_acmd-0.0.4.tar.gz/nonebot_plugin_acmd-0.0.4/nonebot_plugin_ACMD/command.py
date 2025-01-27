from __future__ import annotations
import os
import inspect
from collections import defaultdict
from weakref import WeakValueDictionary
import threading
import asyncio

import sqlite3
import aiosqlite
import pandas as pd
from rapidfuzz import fuzz
from typing import Awaitable, List, Union, Any, Dict, Callable, Final, Optional

from nonebot import logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, PrivateMessageEvent
from .connection_pool import SQLitePool
from .config import Config
from .cli import CommandRegistry
from .command_signer import HandlerManager
from .Atypes import HandlerInvoker, HandlerContext
from .Atypes import (
    UserInput,
    GroupID,
    ImageInput,
    PIN,
    Record
)

SHARED_MEMORY_DB_NAME: Final = "file:shared_memory_db?mode=memory&cache=shared"
MEMORY_DB_CONN: Final = sqlite3.connect(SHARED_MEMORY_DB_NAME, uri=True)
COMMAND_POOL: Final = SQLitePool(shared_uri=SHARED_MEMORY_DB_NAME)

from .command_signer import BasicHandler  # noqa


def create_memory_table():
    cursor = MEMORY_DB_CONN.cursor()

    # 创建 commands 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commands (
            command TEXT PRIMARY KEY,
            description TEXT,
            owner TEXT,
            full_match INTEGER,
            handler_list TEXT
        )
    ''')
    # 创建 helps 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS helps (
            owner TEXT PRIMARY KEY,
            help TEXT,
            function BOOLEAN DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_owners ON commands(owner)
    ''')

    MEMORY_DB_CONN.commit()


create_memory_table()


class CommandData:
    """数据模型类，用于存储命令的属性。"""
    __slots__ = ('command', 'description', 'owner',
                 'full_match', 'handler_list')

    def __init__(self, command: List[str], description: str, owner: str, full_match: bool, handler_list: List[str]):
        self.command = command
        self.description = description
        self.owner = owner
        self.full_match = full_match
        self.handler_list = handler_list


class CommandDatabase:
    """数据库操作类，用于命令的增删改查。"""
    __slots__ = ('conn')

    def __init__(self, db_connection: Union[sqlite3.Connection, aiosqlite.Connection] = None):
        self.conn = db_connection

    def insert_commands(self, command_data: CommandData):
        """插入命令到数据库。"""
        cursor = self.conn.cursor()
        cursor.executemany('''
            INSERT INTO commands (command, description, owner, full_match, handler_list)
            VALUES (?, ?, ?, ?, ?)
        ''', [(cmd, command_data.description, command_data.owner, command_data.full_match, ','.join(command_data.handler_list)) for cmd in command_data.command])
        self.conn.commit()

    async def _aioinsert_commands(self, command_data: CommandData):
        """插入命令到数据库。"""
        async with self.conn.cursor() as cursor:
            await cursor.executemany('''
                INSERT INTO commands (command, description, owner, full_match, handler_list)
                VALUES (?, ?, ?, ?, ?)
            ''', [(cmd, command_data.description, command_data.owner, command_data.full_match, ','.join(command_data.handler_list)) for cmd in command_data.command])
        await self.conn.commit()

    async def update_commands(self, command_data: CommandData):
        """更新命令到数据库。"""
        async with COMMAND_POOL.connection() as conn:
            try:
                conn.isolation_level = 'EXCLUSIVE'
                cursor = await conn.cursor()
                await cursor.execute('BEGIN EXCLUSIVE')
                await cursor.executemany('''
                    INSERT OR REPLACE INTO commands (command, description, owner, full_match, handler_list)
                    VALUES (?, ?, ?, ?, ?)
                ''', [(cmd, command_data.description, command_data.owner, command_data.full_match, ','.join(command_data.handler_list)) for cmd in command_data.command])
                await conn.commit()
            except Exception as e:
                await conn.rollback()
                raise e

    async def remove_commands(self, commands: List[str]):
        """删除命令记录。"""
        async with COMMAND_POOL.connection() as conn:
            cursor = await conn.cursor()
            await cursor.executemany('DELETE FROM commands WHERE command = ?', [(cmd,) for cmd in commands])
            await conn.commit()

    async def get_commands(self, command: str):
        """获取命令记录。"""
        async with COMMAND_POOL.connection() as conn:
            cursor = await conn.cursor()
            await cursor.execute('SELECT * FROM commands WHERE command = ?', (command,))
            return await cursor.fetchone()


class Command:
    # 类属性，用于存储命令实例
    _commands_dict: defaultdict = defaultdict(WeakValueDictionary)
    _lock: threading.Lock = threading.Lock()
    __slots__ = ('data', '__weakref__')

    def __init__(self, commands: List[str], description: str, owner: str, full_match: bool, handler_list: List[Union[str, BasicHandler]], **kwargs):
        # 初始化命令数据
        self.data = CommandData(
            command=list(dict.fromkeys([command.strip()
                         for command in commands])),
            description=description,
            owner=owner,
            full_match=full_match,
            handler_list=[str(handler.handler_id) if isinstance(
                handler, BasicHandler) else handler for handler in handler_list]
        )

        # 获取脚本文件夹的绝对路径
        if 'script_folder_path' not in kwargs:
            caller_frame = inspect.stack()[1]
            caller_filename = caller_frame.filename
            script_folder_path = os.path.abspath(
                os.path.dirname(caller_filename))
        else:
            script_folder_path = kwargs['script_folder_path']

        # 将命令实例添加到类属性字典中
        with self._lock:
            self._commands_dict[script_folder_path][self] = self

        # 在初始化时进行验证和保存
        if self.validate():
            if not COMMAND_POOL._initialized:
                self.save()
            else:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop and loop.is_running():
                    loop.create_task(self._aiosave())
                else:
                    asyncio.run(self._aiosave())

    def validate(self) -> bool:
        """验证命令数据的合法性。"""
        for command in self.data.command:
            if not command or not isinstance(command, str) or (command == '/help' and self.data.owner != 'origin'):
                return False
        return True

    def save(self):
        """保存命令数据到数据库。"""
        if not self.validate():
            raise ValueError("Invalid command data.")

        db = CommandDatabase(MEMORY_DB_CONN)
        db.insert_commands(self.data)

    async def _aiosave(self):
        """保存命令数据到数据库。"""
        if not self.validate():
            raise ValueError("Invalid command data.")
        async with COMMAND_POOL.connection() as conn:
            db = CommandDatabase(conn)
            await db._aioinsert_commands(self.data)

    async def update(self, new_commands: List[str] = None, new_hander_list: List[Union[str, BasicHandler]] = None):
        db = CommandDatabase()
        if new_commands is not None:
            await db.remove_commands(self.data.command)
            self.data.command = list(dict.fromkeys(
                [command.strip() for command in new_commands]))
        if new_hander_list is not None:
            self.data.handler_list = [str(handler.handler_id) if isinstance(
                handler, BasicHandler) else handler for handler in new_hander_list]
        """更新命令数据到数据库。"""
        if not self.validate():
            raise ValueError("Invalid command data.")

        await db.update_commands(self.data)

    async def delete(self, script_folder_path: str = None):
        """删除该命令。"""
        async with COMMAND_POOL.connection() as conn:
            db = CommandDatabase(conn)
            await db.remove_commands(self.data.command)

        # 从类属性字典中移除该命令实例
        if not script_folder_path:
            caller_frame = inspect.stack()[1]
            caller_filename = caller_frame.filename
            script_folder_path = os.path.abspath(
                os.path.dirname(caller_filename))
        with self._lock:
            if self in self._commands_dict[script_folder_path]:
                del self._commands_dict[script_folder_path][self]
                logger.info(f'{self.data.owner} 下属的命令 {self.data.command} 被注销')
            else:
                logger.error(f'{self.data.owner} 下属的命令 {
                             self.data.command} 未找到')


class CommandFactory:
    """
    工厂类,包含所有创建命令所需要的方法

    P.S 该类设计并不符合工厂类规范
    """
    @staticmethod
    def create_command(commands: Optional[List[str]] = None, handler_list: Union[str, int, BasicHandler, List[Union[str, int, BasicHandler]]] = None, owner: Optional[str] = None, description: Optional[str] = '', full_match: bool = False) -> Optional[Command]:
        """创建命令对象。

        Args:
            commands (List[str]): 命令列表。不传入或传入`None`代表无需命令，总是触发。
            handler_list (str, int, BasicHandler, List[str, int, BasicHandler]): 处理器单例或列表
            owner (str): 所有者, 用于标识指令所属插件
            description (str, optional): 描述. Defaults to ''.
            full_match (bool, optional): 是否完全匹配. Defaults to False.

        Returns:
            Command: 命令对象
        """
        if handler_list is None:
            raise RuntimeError("没有处理器传入")

        if not isinstance(handler_list, list):
            handler_list = [handler_list]

        caller_frame = inspect.stack()[1]
        script_folder_path = os.path.abspath(
            os.path.dirname(caller_frame.filename))

        if commands is None:
            for handler in handler_list:
                HandlerManager.set_Unconditional_handler(handler)
            return None

        if owner is None:
            raise RuntimeError(f"命令 {commands} 没有指定拥有者")

        return Command(commands, description, owner, full_match, handler_list, script_folder_path=script_folder_path)

    @staticmethod
    def create_help_command(owner: str, help_text: str = '', function: Callable = None) -> None:
        """接管帮助命令。

        Args:
            owner (str): 被接管插件对象
            help_text (str): 帮助文本
            function (Callable, optional): 帮助命令处理函数. Defaults to None.可返回字符串,也可返回None

            通常情况下,help_text与function选择一个传入即可,function优先级更高.
        """
        HelpTakeOverManager.takeover_help(owner, help_text, function)

    @staticmethod
    def CLI_cmd_register(cmd: str) -> Callable:
        """
        装饰器,用于注册控制台指令。

        非常建议详细撰写被装饰函数的文档字符串,因为它会被展示给用户

        参数:
            cmd (str): 要注册的命令名称。
        返回:
            Callable: 一个装饰器，用来装饰实现命令逻辑的异步函数。
        """
        def decorator(func: Callable[..., Awaitable[None]]) -> Callable[..., Awaitable[None]]:
            CommandRegistry.register(cmd)(func)
            return func
        return decorator

    @staticmethod
    def parameter_injection(field: str, field_type: type):
        """
        装饰器用于设置依赖关系，确保可以被解析并由handler调用。

        参数:
            field (str): 新字段的名称。
            field_type (type): 新字段的类型。
        """
        def decorator(func):
            # 检查func是否为协程函数
            if not inspect.iscoroutinefunction(func):
                raise RuntimeError("被装饰函数必须是异步的")

            HandlerContext.insert_field(field, field_type, func)

            async def wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                return result

            return wrapper

        return decorator


class HelpTakeOverManager:
    """帮助接管管理器。"""
    _owner_to_function: Dict[str, Callable] = {}

    @classmethod
    def takeover_help(cls, owner: str, help_text: str = '', function: Callable = None) -> None:
        """接管帮助命令。"""
        is_function = False
        if owner in cls._owner_to_function:
            raise ValueError(f"Help command of {
                             owner} has already taken over.")
        if not help_text and not function and owner != 'origin':
            raise ValueError(
                "Either help_text or function should be provided.")
        if function and callable(function) and asyncio.iscoroutinefunction(function):
            cls._owner_to_function[owner] = function
            is_function = True
        elif function:
            raise ValueError(
                "function should be an asynchronous function (i.e., defined with 'async def').")

        if not is_function:
            with MEMORY_DB_CONN as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO helps (owner, help, function) VALUES (?, ?, ?)', (owner, help_text, 0))
                conn.commit()
        else:
            with MEMORY_DB_CONN as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO helps (owner, help, function) VALUES (?, ?, ?)', (owner, help_text, 1))
                conn.commit()

    @classmethod
    def get_function(cls, owner: str):
        if owner in cls._owner_to_function:
            return cls._owner_to_function[owner]


def _fuzzy_match_ratio(s1: str, s2: str) -> float:
    """计算两个字符串之间的模糊匹配相似度分数。

    参数:
    s1 : 用户输入
    s2 : 标准命令

    返回:
    模糊匹配相似度分数，范围从0到100
    """
    should_trim = s1.endswith(('~', '～'))
    trimmed_s1 = s1[:-1] if should_trim else s1

    return fuzz.QRatio(trimmed_s1, s2[:len(trimmed_s1)])


async def dispatch(
    message: str,
    bot: Bot,
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    image: List[str] = [],
) -> None:
    """消息派发，执行对应逻辑"""

    groupid: str = str(getattr(event, 'group_id', -1))
    message = message.strip()
    if not message:
        return

    async with COMMAND_POOL.connection() as conn:
        cursor = await conn.cursor()
        try:
            if len(message) < 2:
                await cursor.execute('SELECT command, handler_list FROM commands WHERE command = ?', (message,))
            else:
                prefix = message[:2]
                await cursor.execute('SELECT command, handler_list, full_match FROM commands WHERE command = ? OR command LIKE ?', (message, f'{prefix}%'))
            commands = await cursor.fetchall()
        except Exception as e:
            # 记录错误信息
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            await cursor.close()

    df_commands = pd.DataFrame(
        commands, columns=['command', 'handler_list', 'full_match'])
    best_match, best_match_handlers, exact_match, highest_similarity = '', [], False, 100.0

    # 检查完全匹配
    exact_matches = df_commands[df_commands['command'] == message]
    if not exact_matches.empty:
        best_match: str = exact_matches.iloc[0]['command']
        best_match_handlers = exact_matches.iloc[0]['handler_list'].split(',')
        exact_match = True
    else:
        # 计算命令的空格数量
        df_commands['command_spaces'] = df_commands['command'].str.count(' ')

        # 获取消息的前N个单词
        message_split = message.split(' ')

        # 查找非完全匹配命令
        df_commands['message_n_plus_1_space_content'] = df_commands['command_spaces'].apply(
            lambda spaces: ' '.join(
                message_split[:spaces + 1]) if spaces + 1 <= len(message_split) else ''
        )

        matches = df_commands[(~df_commands['full_match']) & (
            df_commands['command'] == df_commands['message_n_plus_1_space_content'])]
        if not matches.empty:
            best_match: str = matches.iloc[0]['command']
            best_match_handlers = matches.iloc[0]['handler_list'].split(',')
            exact_match = True

        # 计算相似度
        if not df_commands.empty and not exact_match:
            df_commands['similarity'] = df_commands.apply(
                lambda row: _fuzzy_match_ratio(
                    row['message_n_plus_1_space_content'], row['command'])
                if row['command_spaces'] + 1 <= len(message_split) else 0.0, axis=1
            )

            # 找到相似度最高的行
            max_similarity = df_commands['similarity'].max()
            best_match_rows = df_commands[df_commands['similarity']
                                          == max_similarity]
            if len(best_match_rows) == 1 and max_similarity >= Config.Similarity_Rate:
                best_match_row = best_match_rows.iloc[0]
                best_match: str = best_match_row['command']
                best_match_handlers = best_match_row['handler_list'].split(',')
                highest_similarity = best_match_row['similarity']
                logger.debug(f"相似度最高的命令是：{best_match_rows.iloc[0]['command']}, 相似度为：{
                             max_similarity}")
            else:
                logger.debug(f"相似度最高的命令是：{best_match_rows.iloc[0]['command']}, 相似度为：{
                             max_similarity}")
                return

    # 确保字符数差异符合要求
    if best_match:
        command_full_match = df_commands[df_commands['command']
                                         == best_match]['full_match'].iloc[0]
        if command_full_match and abs(len(message) - len(best_match)) >= 3:
            return

        # 替换消息内容
        if not exact_match:
            message_parts = message.split(' ')
            command_spaces = best_match.count(' ')
            if command_spaces + 1 <= len(message_parts):
                message_parts[:command_spaces + 1] = best_match.split(' ')
                message = ' '.join(message_parts)

    best_match_handlers = [int(handle_id) for handle_id in best_match_handlers]

    # 继续执行处理程序.首先运行命令，然后运行全量
    handler_context = None
    try:
        if best_match or HandlerManager._Unconditional_Handler:
            handler_context = HandlerContext(
                msg=UserInput(message.replace(
                    best_match, '', 1).strip(), message, best_match),
                image=ImageInput(image),
                pin=PIN(str(event.user_id), event.avatar),
                groupid=GroupID(groupid, int(groupid)),
                bot=bot,
                event=event,
                record=Record(similarity=highest_similarity,
                              handlers=best_match_handlers)
            )
        if best_match:
            for handler in best_match_handlers:
                await HandlerInvoker.invoke_handler(handler, handler_context)
    finally:
        if handler_context:
            for handler in HandlerManager._Unconditional_Handler:
                await HandlerInvoker.invoke_handler(handler, handler_context, rasie_StopPropagation=False)


class Helper(BasicHandler):
    __slots__ = tuple(
        slot for slot in BasicHandler.__slots__ if slot != '__weakref__')

    async def get_unique_owners(self):
        async with COMMAND_POOL.connection() as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT DISTINCT owner FROM commands')
                owners = await cursor.fetchall()
                return [owner[0] for owner in owners if owner[0] != 'origin']

    async def get_owner_help(self, owner: str, page_cut: Union[int, str] = 1, **kwargs: Any):
        page_cut = int(page_cut)
        offset = (page_cut - 1) * 7

        async with COMMAND_POOL.connection() as db:
            query = """
                SELECT 'help' AS type, help AS content, function AS is_function FROM helps WHERE owner=?
                UNION ALL
                SELECT 'command' AS type, command AS content, description AS is_function FROM commands WHERE owner=? LIMIT ? OFFSET ?
                """

            async with db.execute(query, (owner, owner, 7, offset)) as cursor:
                results = await cursor.fetchall()

                if results:
                    # 检查是否有 helps 表的结果
                    for result in results:
                        if result[0] == 'help':
                            if result[2]:  # 检查 function 是否为 True
                                if HelpTakeOverManager.get_function(owner):
                                    func = HelpTakeOverManager.get_function(
                                        owner)
                                    # 调用异步函数并返回结果
                                    return await func(kwargs)
                            else:
                                return result[1]  # 返回 help 内容

                    # 如果没有 helps 表的结果，返回 commands 表的结果
                    formatted_results = '\n'.join(
                        [f"{cmd} : {desc}" if desc else f"{cmd}" for _,
                            cmd, desc in results if _ == 'command']
                    )
                    return formatted_results
                else:
                    return []

    async def handle(self, bot: Bot = None, event: Union[GroupMessageEvent, PrivateMessageEvent] = None, msg: UserInput = None, qq: PIN = None, groupid: GroupID = None, image: ImageInput = None) -> None:
        groups = msg.full.replace('/help ', '', 1).split(' ')
        if not groups or msg.full == '/help':
            msg_to_send = '\n'.join(await self.get_unique_owners())
            await bot.send(event, message=f'可用模块:\n{msg_to_send}\n\n使用 /help [model] [page] 来查阅详情')
            return
        else:
            msg_to_send = await self.get_owner_help(groups[0], groups[1] if len(groups) == 2 else 1, bot=bot, event=event, msg=msg, qq=qq, groupid=groupid, image=image)
            if msg_to_send:
                await bot.send(event=event, message=f'可用指令:\n{msg_to_send}\n\n使用 /help [model] [page] 来切换页码')
                return
            elif msg_to_send is not None:
                await bot.send(event=event, message='当前页码为空\n使用 /help [model] [page] 来切换页码')


CommandFactory.create_command(
    commands=['/help'],
    handler_list=[Helper(unique='origin_helper')],
    owner='origin',
    description='生成帮助文档'
)
