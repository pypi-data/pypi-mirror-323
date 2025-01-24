from zope.interface import implementer
import redis

from jh_scrapyd import sqlite
from jh_scrapyd.interfaces import ISpiderQueue
from jh_scrapyd.jh.queue.redis_queue import RedisQueue
from jh_scrapyd import debug_log, get_config


@implementer(ISpiderQueue)
class SqliteSpiderQueue:
    def __init__(self, config, project, table="spider_queue"):
        self.q = sqlite.initialize(sqlite.JsonSqlitePriorityQueue, config, project, table)

    def add(self, name, priority=0.0, **spider_args):
        message = spider_args.copy()
        message["name"] = name
        self.q.put(message, priority=priority)

    def pop(self):
        return self.q.pop()

    def count(self):
        return len(self.q)

    def list(self, limit: int = -1):
        return [message for message, _ in self.q.get_list(limit)]

    def remove(self, func):
        return self.q.remove(func)

    def has(self, jobid):
        return self.q.has(jobid)

    def remove_one(self, jobid):
        return self.q.remove_one(jobid)

    def clear(self):
        self.q.clear()


@implementer(ISpiderQueue)
class RedisSpiderQueue(object):

    def __init__(self, config, project, table='default'):
        # 队列参数
        self.config = config
        self.project = project
        self.table = table
        # 更新队列
        self.queue = None
        self.update_queue()

    def add(self, name, priority=0.0, **spider_args):
        d = spider_args.copy()
        d['name'] = name
        # 补充字段
        d['_project'] = self.project
        # 写入
        self.put(d, priority)

    def put(self, message, priority):
        # 调试日志
        debug_log(message, title='队列put方法调度')

        return self.queue.put(self.project, message['_job'], message, float(priority))

    def pop(self):
        # 调试日志
        debug_log('project:', self.project, title='队列pop方法调度')

        return self.queue.pop(self.project)

    def count(self):
        # 个数
        c = self.queue.count(self.project)
        # 调试日志
        debug_log('count:', c, title='队列count方法调度')

        return c

    def list(self, limit: int = -1):
        # 调试日志
        debug_log('project:', self.project, title='队列list方法调度')

        return self.queue.list(self.project, True, limit)

    def clear(self):
        # 调试日志
        debug_log('project:', self.project, title='队列clear方法调度')

        self.queue.clear(self.project)

    def has(self, jobid):
        # 调试日志
        debug_log('project:', self.project, jobid, title='队列has方法调度')

        return self.queue.has(self.project, jobid)

    def remove_one(self, jobid):
        # 调试日志
        debug_log('project:', self.project, jobid, title='队列cancel方法调度')

        return self.queue.remove(self.project, jobid)
    
    def remove(self, func):
        # 调试日志
        debug_log('project:', self.project, title='队列remove方法调度')

    def update_queue(self):
        # 获取redis配置
        cluster_conf = get_config(section='cluster')
        conf = {
            'host': cluster_conf.get('host', 'localhost'),
            'port': cluster_conf.get('port', 6379),
            'db': cluster_conf.get('db', 0)
        }
        password = cluster_conf.get('password')
        if password:
            conf['password'] = password
        redis_obj = redis.StrictRedis(
            **conf
        )
        # 获取表名称
        table = cluster_conf.get('queue_prefix', self.table)
        # 创建队列对象
        self.queue = RedisQueue(redis_obj, table, cluster_conf.get('is_unified_queue'))
