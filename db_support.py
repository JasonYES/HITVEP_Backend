import asyncio
import db
import json
import sqlalchemy as sa
from sqlalchemy.sql import select, insert, update, delete
from aiomysql.sa import create_engine
import decimal, datetime
import aiohttp
import logging

def alchemyencoder(obj):
    """JSON encoder function for SQLAlch emy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)

def do_log(level, info):
    if level == 5:
        logging.critical(info)
    elif level == 4:
        logging.error(info)
    elif level == 3:
        logging.warning(info)
    elif level == 2:
        logging.info(info)
    elif level == 1:
        logging.debug(info)
        
async def aio_post(url, data):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as resp:
                return await resp.json()
    except Exception as e:
        # print(e)
        return False

async def aio_delete(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(url) as resp:
                # print(resp)
                return await resp.json()
    except Exception as e:
        # print(e)
        return False

async def aio_put(url, data):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=data) as resp:
                return await resp.json()
    except Exception as e:
        # print(e)
        return False

async def aio_patch(url, data):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, json=data) as resp:
                return await resp.json()
    except Exception as e:
        # print(e)
        return False

async def db_select(form_name, find=["*"], **kwargs):
    try:
        select_engine = await create_engine(**db.config)
        cell = getattr(db, form_name)
        if find[0] == "*":
            finds = [cell]
        else:
            finds = []
            for i in find:
                finds.append(getattr(cell.c, i))
        async with select_engine.acquire() as conn:
            sql = select(finds)
            for i in kwargs:
                sql = sql.where(getattr(cell.c, i) == kwargs[i])
            select_info = await conn.execute(sql)

        result = json.dumps([(dict(row.items()))
                             for row in select_info], default=alchemyencoder)
        # print(result)
        return json.loads(result)

    except Exception as e:
        do_log(4, "select error:" + str(e))
        return []


async def db_insert(form_name, **kwargs):
    try:
        insert_engine = await create_engine(**db.config)
        cell = getattr(db, form_name)
        async with insert_engine.acquire() as conn:
            trans = await conn.begin()
            try:
                await conn.execute(insert(cell).values(kwargs))
            except Exception as e:
                main.do_log(4, "insert error:" + str(e))
                await trans.rollback()
                return False
            else:
                await trans.commit()
        return True
    except Exception as e:
        do_log(4, "insert error:" + str(e))
        return False


async def db_update(form_name, set={}, **kwargs):
    try:
        update_engine = await create_engine(**db.config)
        cell = getattr(db, form_name)
        async with update_engine.acquire() as conn:
            sql = update(cell).values(set)
            for i in kwargs:
                sql = sql.where(getattr(cell.c, i) == kwargs[i])
            trans = await conn.begin()
            try:
                await conn.execute(sql)
            except Exception as e:
                main.do_log(4, "update error:" + str(e))
                await trans.rollback()
                return False
            else:
                await trans.commit()
        return True
    except Exception as e:
        do_log(4, "update error:" + str(e))
        return False


async def db_delete(form_name, **kwargs):
    try:
        delete_engine = await create_engine(**db.config)
        cell = getattr(db, form_name)
        async with delete_engine.acquire() as conn:
            sql = delete(cell)
            for i in kwargs:
                sql = sql.where(getattr(cell.c, i) == kwargs[i])
            trans = await conn.begin()
            try:
                await conn.execute(sql)
            except Exception as e:
                main.do_log(4, "delete error:" + str(e))
                await trans.rollback()
                return False
            else:
                await trans.commit()
        return True
    except Exception as e:
        do_log(4, "delete error:" + str(e))
        return False
