import pandas as pd
import sqlalchemy
from sqlalchemy import insert
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    Column,
    UUID,
    Text,
    TIMESTAMP,
    Double,
    Integer,
    Numeric,
    ARRAY,
)


Base = declarative_base()


class DatabaseHandler:
    def __init__(self, db_params: dict, table: sqlalchemy.orm.decl_api.DeclarativeMeta, echo: bool = False):
        db_url = (
            f"postgresql+asyncpg://{db_params['user']}:{db_params['password']}@"
            f"{db_params['host']}:{db_params['port']}/{db_params['dbname']}"
        )
        self.table = table
        self.engine = create_async_engine(db_url, echo=echo)
        self.async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def create_table(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def insert_data(self, df: pd.DataFrame):
        records = df.to_dict(orient="records")

        async with self.async_session() as session:
            async with session.begin():
                await session.execute(insert(self.table).values(records))
                await session.commit()

    async def query(self, sql_query: str) -> pd.DataFrame:
        async with self.engine.connect() as conn:
            result = await conn.execute(sqlalchemy.text(sql_query))
            rows = result.fetchall()
            columns = result.keys()
            df = pd.DataFrame(rows, columns=columns)
            return df

    async def close(self):
        await self.engine.dispose()


class TableRealEstateInfo(Base):
    __tablename__ = "real_estate_info"

    id = Column(UUID, primary_key=True)
    estate_id = Column(Text, nullable=False)
    action = Column(Text, nullable=False)
    search_date = Column(TIMESTAMP, nullable=False)
    post_type = Column(Text)
    link = Column(Text)
    type = Column(Text)
    image_list = Column(ARRAY(Text))
    snippet = Column(Text)
    street = Column(Text)
    neighbor = Column(Text)
    city = Column(Text)
    state = Column(Text)
    latitude = Column(Double)
    longitude = Column(Double)
    floor_size = Column(Integer)
    number_of_rooms = Column(Integer)
    number_of_bathrooms = Column(Integer)
    number_of_parking_spaces = Column(Integer)
    amenities_list = Column(ARRAY(Text))
    price = Column(Numeric(12, 2))
    condominium = Column(Numeric(12, 2))
    iptu = Column(Numeric(12, 2))
