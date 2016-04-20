# *-* coding:utf-8 *-*

from importlib import import_module

from Araneae.utils.log import Plog

try:
    import MySQLdb 
except ImportError:
    ERROR('MySQLdb moudle not in os')

try:
    import redis
    from redis.exceptions import RedisError
except ImportError:
    ERROR('reids moudle not in os')

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure,ServerSelectionTimeoutError,PyMongoError
    from pymongo.cursor import CursorType
    from bson.objectid import ObjectId
except ImportError:
    ERROR('pymongo moudle not in os')

class BaseDataPipeline(object):

    def select(self,db,table,**kvargs):
        """
        选择数据库和表,如果为关系型数据库需要建立相应的表
        """
        raise NotImplementedError('DataPipeline必须实现select')

    def insert(self,data):
        """
        插入数据
        """
        raise NotImplementedError('DataPipeline必须实现insert')

    def update(self,filter,data):
        """
        更新数据,如果存在已有字段则覆盖
        """
        raise NotImplementedError('DataPipeline必须实现update')

class MongoDataPipeline(BaseDataPipeline):
    
    def __init__(self,**args):
        self.reset(**args)

    def reset(self,**args):
        self._mongo = None
        self._db = None
        self._collection = None
        
        mongo_config = {'host':args['host'],'port':int(args['port']),'connectTimeoutMS':int(args['timeout'])}

        try:
            self._mongo = MongoClient(**mongo_config)
        
        except ConnectionFailure,e:
            EROR('Mongo Error -- connect failed[%s]' % e)
            raise MongoException

    def select(self,db,collection):
        self._db = self._mongo[db]
        self._collection = self._db[collection]

    def insert(self,data):
        try:
            obj_id = str(self._collection.insert_one(data).inserted_id)
            Plog('Mongo insert -- data[%s] -- _id[%s]' % (data,obj_id))
            return obj_id
        except PyMongoError as e:    
            raise TypeError(e)

    def update(self,filter,data):
        try:
            filter = {'_id':ObjectId(filter)}
            update_id = str(self._collection.update_one(filter = filter,update = {'$set':data}).upserted_id)
            Plog('Mongo update -- filter[%s] -- data[%s] -- upserted id[%s]' % (filter,data,update_id))
            return update_id
        except PyMongoError as e:
            raise TypeError(e)

    def find(self,filter=None,projection=None,skip=0,limit=0,no_cursor_timeout=False,cursor_type=CursorType.NON_TAILABLE,sort=None,allow_partial_results=False,\
             oplog_replay=False, modifiers=None, manipulate=True):
        return self._collection.find(filter=filter,projection=projection,skip=skip,limit=limit,no_cursor_timeout=no_cursor_timeout,\
               cursor_type=CursorType.NON_TAILABLE,sort=sort,allow_partial_results=allow_partial_results,oplog_replay=oplog_replay,\
               modifiers=modifiers, manipulate=manipulate)
    
    def count(self):
        return self._collection.count()


    def collection_names(self,system = True):
        return self._db.collection_names(include_system_collections = system)

MYSQL_RETRY_TIMES = 10

class Mysql(object):


    def __init__(self,**args):
        self._connect_flag = False

        self._cur = None
        self._conn = None
        self._sql = ''
        self._retry = MYSQL_RETRY_TIMES

        self._mysql_config = args
        self.reset(args)

    def reset(self,args):
        mysql_config = {'host':args['host'],'port':int(args['port']),'user':args['user'],'db':args['db'],
                        'passwd':args['password'],'charset':args['charset'],'connect_timeout':int(args['timeout'])}

        #status: 0 free;1 used;
        self._status = 0
        self._event_flag = False
        
        if self._connect_flag:
            self._cur.close()
            self._conn.close() 

        try:
            self._conn = MySQLdb.connect(**mysql_config)
            self._cur = self._conn.cursor(MySQLdb.cursors.DictCursor)
            self._connect_flag = True

        except MySQLdb.Error,e:
            self._connect_flag = False
            ERROR('Mysql Error -- msg[Connect Failed]')
            raise MysqlException('Connect Failed')

    def start_event(self):
        try:
            self._conn.autocommit(False)
            self._conn.begin()
            self._event_flag = True

        except MySQLdb.OperationalError,e:
            self.reconnect()
            self.start_event()

    def exec_event(self,sql,**kwds):
        if self._event_flag:
            res = self.query(sql,**kwds)
            return res

        else:
            ERROR('Mysql Error -- [Not Start Event]')
            raise MysqlException('Not Start Event')

    def end_event(self):
        if self._event_flag:
            self._conn.commit()
            self._conn.autocommit(True)
            self._event_flag = False

    def query(self,sql,**kwds):
        for i in range(self._retry):
            try:
                self._sql = sql
                self._kwds = kwds
                sql = sql % kwds
                INFO('Mysql -- execute SQL[%s]' % (sql))
                self._cur.execute(sql)  
                self._sql = ''
            except MySQLdb.OperationalError,e:
                self.reconnect()
                ERROR('Mysql Error -- SQL[%s] -- msg[Mysql Gone Away or Operate Error!%s]' % (sql,e))
                continue
            except MySQLdb.Error,e:
                self._event_flag = False
                ERROR('Mysql Error -- SQL[%s] -- msg[Mysql Execute Failed!%s]' % (sql,e))
                raise MysqlException('Mysql Execute Failed')
            except:
                ERROR('Mysql Error -- msg[Sql Format Failed!] -- SQL[%s] -- Data[%s]' % (sql,kwds))
                raise MysqlException('Sql Format Failed')
                
            effect = self._cur.rowcount

            INFO('Mysql Effect Row [%d]' % effect)

            if not self._event_flag:
                self._conn.commit()

            return effect
        
        raise MysqlException('Mysql Gone Away or Operate Error')

    def reconnect(self):
        self.reset(self._mysql_config)
        INFO('Mysql Reconnect')

    def rollback(self):
        self._conn.rollback()

    def fetch(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

    def commit(self):
        self._conn.commit()

    @property
    def id(self):
        return int(self._conn.insert_id())

    @property
    def sql(self):
        return self._sql

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self,status):
        self._status = status    

    def __def__(self):
        self._cur.close()
        self._conn.close()


class Redis(object):
        
    def __init__(self,**args):
        self.reset(**args)
        
    def reset(self,**args):
        self._redis = None

        redis_config = {'host':args['host'],'port':int(args['port']),'password':args['password'],
                        'db':int(args['db']),'socket_timeout':int(args['timeout']),'charset':args['charset']}

        self._redis = redis.StrictRedis(**redis_config)

    def srem(self,name,*values):
        try:
            ret = self._redis.srem(name,*values)       
            INFO('Redis srem  -- redis command[srem %s %s]' % (name,values))
            
        except RedisError:
            raise RedisException

        return ret

    def sismember(self,name,value):
        try:
            ret = self._redis.sismember(name,value)       
            INFO('Redis sismember -- redis command[sismember %s %s]' % (name,value))
            
        except RedisError:
            raise RedisException

        return ret

    def incr(self,name,amount = 1):
        try:
            ret = self._redis.incr(name,amount)       
            INFO('Redis incr -- redis command[incr %s %d]' % (name,amount))
            
        except RedisError:
            raise RedisException

        return ret

    def get(self,name):
        try:
            ret = self._redis.get(name)       
            INFO('Redis get -- redis command[get %s]' % name)

        except RedisError:
            raise RedisException

        return ret

    def setnx(self,name,value):
        try:
            ret = self._redis.setnx(name,value)       
            INFO('Redis setnx -- redis command[setnx %s %s]' % (name,value))

        except RedisError:
            raise RedisException
        
        return ret

    def hmset(self,name,arg_dict):
        try:
            ret = self._redis.hmset(name,arg_dict)       
            INFO('Redis hmset -- redis command[hmset %s %s]' % (name,arg_dict))

        except RedisError:
            raise RedisException

            return ret

    def hset(self,name,key,value):
        try:
            ret = self._redis.hset(name,key,value)       
            INFO('Redis hset -- redis command[hset %s %s %s]' % (name,key,value))

        except RedisError:
            raise RedisException

        return ret

    def hget(self,name,key):
        try:
            ret = self._redis.hget(name,key)
            INFO('Redis hget -- redis command[hget %s %s]' % (name,key))

        except RedisError:
            raise RedisException

        return ret

    def hmget(self,name,*args):
        try:
            ret = self._redis.hmget(name,*args)  
            INFO('Redis hmget -- redis command[hmget %s %s]' % (name,args))

        except RedisError:
            raise RedisException

        return ret

     
    def hgetall(self,name):
        try:
            ret =  self._redis.hgetall(name)       
            INFO('Redis hgetall -- redis command[hgetall %s]' % name)

        except RedisError:
            raise RedisException

        return ret

    def exists(self,name):
        try:
            ret = self._redis.exists(name)       
            INFO('Redis exists -- redis command[exists %s]' % (name))

        except RedisError,e:
            ERROR('Redis Error -- exists[%s] -- msg[%s]' % (name,e))
            raise RedisException

        return ret 

    def setex(self,name,time,value):
        try:
            ret = self._redis.setex(name,time,value)
            INFO('Redis setex -- redis command[setex %s %d %s]' % (name,time,value))

        except ReidsError:
            raise RedisExceptions

        return ret

    def set(self,name,value):
        try:
            ret = self._redis.set(name,value)
            INFO('Redis set -- redis command[set %s %s]' % (name,value))

        except ReidsError:
            raise RedisExceptions

        return ret

    def expire(self,name,time):
        try:
            ret = self._redis.expire(name,time)
            INFO('Redis expire -- redis command[expire %s %d]' % (name,time))

        except ReidsError:
            raise RedisExceptions

        return  ret

    def delete(self,*name):
        try:
            ret = self._redis.delete(*name)
            INFO('Redis delete -- redis command[delete %s]' % name)

        except ReidsError:
            raise RedisException

        return ret


DEFAULT_PIPELINE_TYPE = 'mongo'
        
def generate_pipeline(**args):
    """
    生成pipeline对象
    """
    pipeline_type = args.get('type',DEFAULT_PIPELINE_TYPE).lower()

    #后续可以支持更多种类
    option_type = {'mongo':'MongoDataPipeline'}

    pipeline_obj = None

    if not pipeline_type in option_type:
        raise TypeError('不支持该类型pipeline，目前只支持mongo')
    else:
        pipeline_module = import_module('Araneae.pipeline')
        pipeline_obj = getattr(pipeline_module,option_type[pipeline_type])(**args)

    return pipeline_obj

