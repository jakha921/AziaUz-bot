from sqlalchemy import (Column, String, Boolean, BigInteger,
                        insert, update, func, select)
from sqlalchemy.orm import sessionmaker

from tgbot.services.db_base import Base


class TGUser(Base):
    """Telegram user model"""
    __tablename__ = "telegram_users"
    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    firstname = Column(String(length=100))
    lastname = Column(String(length=100))
    username = Column(String(length=100), nullable=True)
    phone = Column(String(length=15), nullable=True)
    lang_code = Column(String(length=10), default='ru')
    token = Column(String(length=250), nullable=True)
    is_verify = Column(Boolean, default=False)

    @classmethod
    async def get_user(cls, db_session: sessionmaker, telegram_id: int) -> 'TGUser':
        """Get user by telegram_id"""
        async with db_session() as db_session:
            sql = select(cls).where(cls.telegram_id == telegram_id)
            request = await db_session.execute(sql)
            user: cls = request.scalar()
        return user

    @classmethod
    async def add_user(cls,
                       db_session: sessionmaker,
                       telegram_id: int,
                       firstname: str,
                       lastname: str,
                       username: str = None,
                       phone: str = None,
                       lang_code: str = None,
                       token: str = None,
                       is_verify: str = None
                       ) -> 'TGUser':
        """Add new user into DB"""
        async with db_session() as db_session:
            sql = insert(cls).values(telegram_id=telegram_id,
                                     firstname=firstname,
                                     lastname=lastname,
                                     username=username,
                                     phone=phone,
                                     lang_code=lang_code,
                                     token=token,
                                     is_verify=is_verify).returning('*')
            result = await db_session.execute(sql)
            await db_session.commit()
            return result.scalar()


    @classmethod
    async def update_user(cls, db_session: sessionmaker, telegram_id: int, updated_fields: dict) -> 'TGUser':
        """Update user fields"""
        async with db_session() as db_session:
            sql = update(cls).where(cls.telegram_id == telegram_id).values(**updated_fields)
            result = await db_session.execute(sql)
            await db_session.commit()
            return result

    @classmethod
    async def get_all_users(cls, db_session: sessionmaker) -> list:
        """Returns all users from DB"""
        async with db_session() as db_session:
            # select all columns from table
            sql = select(*cls.__table__.columns).order_by(cls.id)
            result = await db_session.execute(sql)
            users: list = result.fetchall()
        return users

    @classmethod
    async def users_count(cls, db_session: sessionmaker) -> int:
        """Counts all users in the database"""
        async with db_session() as db_session:
            sql = select([func.count(cls.id)]).select_from(cls)
            request = await db_session.execute(sql)
            count = request.scalar()
        return count
    
    @classmethod
    async def drop_db(cls):
        pass

    def __repr__(self):
        return f'User (ID: {self.telegram_id} - {self.firstname} {self.lang_code})'

