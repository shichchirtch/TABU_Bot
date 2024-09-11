from postgress_table import session_marker, User, Admin
from sqlalchemy import select

async def insert_new_user_in_table(user_tg_id: int, name: str):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        if not needed_data:
            print('Now we are into first function')
            new_us = User(tg_us_id=user_tg_id, user_name=name)
            session.add(new_us)
            await session.commit()


async def insert_new_user_in_admin_table(user_tg_id):
    async with session_marker() as session:
        query = await session.execute(select(Admin).filter(Admin.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        if not needed_data:
            print('Now we are into first function admin table')
            new_us = Admin(tg_us_id=user_tg_id)
            session.add(new_us)
            await session.commit()


async def check_user_in_table(user_tg_id:int):
    """Функция проверяет есть ли юзер в БД"""
    async with session_marker() as session:
        print("Work check_user Function")
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        data = query.one_or_none()
        return data


# 6685637602
async def kard_inkrement(user_tg_id: int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        print('works insert_otzyv')
        needed_data.kard_quantity += 1
        await session.commit()

async def add_in_list(user_tg_id: int):
    async with session_marker() as session:
        query = await session.execute(select(Admin).filter(Admin.tg_us_id == 6685637602))
        needed_data = query.scalar()
        print('Add new spieler in admin list')
        admin_list = needed_data.spielers_list
        print('admin_list = ', admin_list)
        updated_list = admin_list+[user_tg_id]
        needed_data.spielers_list = updated_list
        await session.commit()

async def return_quantity_users():
    async with session_marker() as session:
        query = await session.execute(select(Admin).filter(Admin.tg_us_id == 6685637602))
        needed_data = query.scalar()
        return needed_data.spielers_list


async def return_kart_menge(user_tg_id:int):
    async with session_marker() as session:
        query = await session.execute(select(User).filter(User.tg_us_id == user_tg_id))
        needed_data = query.scalar()
        return needed_data.kard_quantity

