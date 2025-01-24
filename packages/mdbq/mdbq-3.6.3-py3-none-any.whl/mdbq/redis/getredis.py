# -*- coding: UTF-8 –*-
import redis
import socket
from mdbq.mysql import s_query
from mdbq.config import myconfig
import pandas as pd
import json
import datetime
import threading


if socket.gethostname() == 'company' or socket.gethostname() == 'Mac2.local':
    conf = myconfig.main()
    conf_data = conf['Windows']['company']['mysql']['local']
    username, password, host, port = conf_data['username'], conf_data['password'], conf_data['host'], conf_data['port']
    redis_password = conf['Windows']['company']['redis']['local']['password']
else:
    conf = myconfig.main()
    conf_data = conf['Windows']['xigua_lx']['mysql']['local']
    username, password, host, port = conf_data['username'], conf_data['password'], conf_data['host'], conf_data['port']
    redis_password = conf['Windows']['company']['redis']['local']['password']  # redis 使用本地数据，全部机子相同



class RedisData(object):
    def __init__(self, redis_engin, download):
        self.redis_engin = redis_engin  # redis 数据处理引擎
        self.download = download  # mysql 数据处理引擎
        self.minute = 60  # 缓存过期时间: 分钟

    def get_from_mysql(self, _db_name, _table_name, _set_year, start_date, end_date):
        """
        _set_year: _table_name 中是否含有年份
        """
        if _set_year:
            __res = []
            for year in range(2024, datetime.datetime.today().year + 1):
                _df = self.download.data_to_df(
                    db_name=_db_name,
                    table_name=f'{_table_name}_{year}',
                    start_date=start_date,
                    end_date=end_date,
                    projection={},
                )
                __res.append(_df)
            _df = pd.concat(__res, ignore_index=True)
        else:
            _df = self.download.data_to_df(
                db_name=_db_name,
                table_name=_table_name,
                start_date=start_date,
                end_date=end_date,
                projection={},
            )
        if len(_df) == 0:
            print(f'{_db_name} - {_table_name}: mysql读取的数据不能为空')
            return pd.DataFrame()
        if '日期' in _df.columns.tolist():
            _df['日期'] = pd.to_datetime(_df['日期'], format='%Y-%m-%d', errors='ignore')  # 转换日期列
        return _df

    def get_from_redis(self, _db_name, _table_name, _set_year, start_date, end_date):
        """
        _set_year: _table_name 中是否含有年份
        _col_list: 如果不传就取 table 的所有列
        对于日期: 最终传出的是日期格式，但如果存入 redis ，需要先格式化为 str，避免日期变整数形式
        """
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        if _set_year:
            my_key = f'{_db_name}:{_table_name}_haveyear'
        else:
            my_key = f'{_db_name}:{_table_name}'
        # ttl 对于不存在的键，它返回 -2；而对于没有设置过期时间的键，它返回 -1
        try:
            ttl_result = self.redis_engin.ttl(my_key)
        except Exception as e:
            # redis 连接失败, 则绕过 redis 直接从 mysql 获取数据
            print('redis 连接失败, 绕过 redis 直接从 mysql 获取数据')
            _df = self.get_from_mysql(_db_name=_db_name, _table_name=_table_name, start_date=start_date, end_date=end_date, _set_year=_set_year)
            return _df
        _df = pd.DataFrame()

        if ttl_result < 60:
            # 1. redis 没有该数据时
            print(f'数据不存在或过期')
            thread = threading.Thread(target=self.set_redis, args=(my_key, _db_name, _table_name, _set_year, start_date, end_date, _df))
            thread.start()
            # _df = self.set_redis(my_key=my_key, _db_name=_db_name, _table_name=_table_name, _set_year=_set_year, start_date=start_date, end_date=end_date)
            _df = self.get_from_mysql(_db_name=_db_name, _table_name=_table_name, start_date=start_date, end_date=end_date, _set_year=_set_year)
            return _df
        # 2. redis 有数据时
        json_string = self.redis_engin.get(my_key)
        data_dict = json.loads(json_string.decode('utf-8'))
        _df = pd.DataFrame(data_dict)

        if '日期' in _df.columns.tolist():
            _df['日期'] = pd.to_datetime(_df['日期'], format='%Y-%m-%d', errors='ignore')  # 转换日期列
            min_date = _df['日期'].min()
            max_date = _df['日期'].max()
            # Bug: 如果外部请求日期小于 table 最小日期，每次都要从 mysql 获取数据，即使 redis 缓存了数据
            if start_date < min_date:  # 外部请求日期小于 redis 数据最小日期
                # 3. redis 有数据但数据不完整时
                print(f'{start_date} -- {min_date} 数据日期不对劲需要更新')
                thread = threading.Thread(target=self.set_redis, args=(my_key, _db_name, _table_name, _set_year, start_date, end_date, _df))
                thread.start()
                # _df = self.set_redis(my_key=my_key, _db_name=_db_name, _table_name=_table_name, _set_year=_set_year, start_date=start_date, end_date=end_date)
                _df = self.get_from_mysql(_db_name=_db_name, _table_name=_table_name, start_date=start_date, end_date=end_date, _set_year=_set_year)
                return _df
            _df = _df[(_df['日期'] >= start_date) & (_df['日期'] <= end_date)]

        return _df

    def set_redis(self, my_key, _db_name, _table_name, _set_year, start_date, end_date, before_df):
        """
        从 mysql 读取数据并存储 redis
        由于这个函数是异步执行的，从页面段首次加载数据时，可能返回空，等待异步执行结束后会正常返回数据
        """
        _df = self.get_from_mysql(
            _db_name=_db_name,
            _table_name=_table_name,
            start_date=start_date,
            end_date=end_date,
            _set_year=_set_year
        )
        if '日期' in _df.columns.tolist():
            _min_date = _df['日期'].min()
            _max_date = _df['日期'].max()
        if '日期' in before_df.columns.tolist():
            # 移除 redis 指定范围的数据，再合并新数据
            before_df1 = before_df[(before_df['日期'] < _min_date)]
            before_df2 = before_df[(before_df['日期'] > _max_date)]
            _df = pd.concat([_df, before_df1, before_df2], ignore_index=True, axis=0)
        # if '日期' in _df.columns.tolist():
        #     _df['日期'] = _df['日期'].astype('str')
        for col in _df.columns.tolist():
            # 存入 redis ，需要先格式化为 str，避免日期变整数形式
            if _df[col].dtype == 'datetime64[ns]':
                _df[col] = _df[col].astype('str')
        if len(_df) == 0:
            print(f'{_table_name}: 写入 redis 的数据不能为空')
            return pd.DataFrame()
        jsondata = _df.to_json(orient='records', force_ascii=False)
        self.redis_engin.set(my_key, jsondata)
        self.redis_engin.expire(my_key, self.minute * 60)  # 设置缓存过期时间: 分钟
        if '日期' in _df.columns.tolist():
            _df['日期'] = pd.to_datetime(_df['日期'], format='%Y-%m-%d', errors='ignore')  # 转换日期列
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'{now}: 刷新 redis -> {_db_name}:{_table_name}')
        return _df


if __name__ == '__main__':
    # ****************************************************
    # 这一部分在外部定义，只需要定义一次，开始
    redis_config = {
        'host': '127.0.0.1',
        'port': 6379,  # 默认Redis端口
        'db': 0,  # 默认Redis数据库索引
        # 'username': 'default',
        'password': redis_password,
    }
    # redis 实例化
    r = redis.Redis(**redis_config)
    # mysql 实例化
    d = s_query.QueryDatas(username=username, password=password, host=host, port=port)
    # 将两个库的实例化对象传给 RedisData 类，并实例化数据处理引擎
    m = RedisData(redis_engin=r, download=d)
    # ****************************************************

    # 以下为动态获取数据库数据
    db_name = '聚合数据'
    table_name = '多店推广场景_按日聚合'
    set_year = False
    df = m.get_from_redis(
        _db_name=db_name,
        _table_name=table_name,
        _set_year=set_year,
        start_date='2025-01-01',
        end_date='2025-01-31'
    )
    print(df)
