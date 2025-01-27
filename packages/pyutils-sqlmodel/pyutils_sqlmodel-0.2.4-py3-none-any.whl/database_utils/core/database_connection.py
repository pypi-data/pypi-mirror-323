import os

from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel
from typing import Optional

load_dotenv()

URL = os.getenv("URL")
USER_DB = os.getenv("USER_DB")
PASS_DB = os.getenv("PASS_DB")
HOST_DB = os.getenv("HOST_DB")
PORT_DB = os.getenv("PORT_DB")
NAME_DB = os.getenv("NAME_DB")


def get_engine(view_logs: Optional[bool] = False):
    SGDB = os.getenv("SGDB")

    if URL is not None:
        DATABASE_URL = URL
    elif (SGDB == "sqlite"):
        DATABASE_URL = f"sqlite:///{NAME_DB}.db"
    elif (SGDB == "postgres"):
        DATABASE_URL = f"postgresql://{USER_DB}:{PASS_DB}@{HOST_DB}:{PORT_DB}/{NAME_DB}"
    elif (SGDB == "mysql"):
        DATABASE_URL = (
            f"mysql+mysqlconnector://{USER_DB}:{PASS_DB}@{HOST_DB}:{PORT_DB}/{NAME_DB}"
        )
    else:
        raise ValueError(f"SGDB not supported: {SGDB}")

    return create_engine(DATABASE_URL, echo=view_logs)

def create_db(view_logs: Optional[bool] = False):
    SQLModel.metadata.create_all(get_engine(view_logs))
