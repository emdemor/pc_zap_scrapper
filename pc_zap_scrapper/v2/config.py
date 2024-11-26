from typing import Literal
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    BASE_URL: str = Field(default="https://www.zapimoveis.com.br", env="BASE_URL")
    EXPECTED_ESTATES_PER_PAGE: int = Field(default=120, env="EXPECTED_ESTATES_PER_PAGE")
    MAX_ESTATES_PER_PAGE: int = Field(default=200, env="MAX_ESTATES_PER_PAGE")
    MAX_SCROLL_ITER_PER_PAGE: int = Field(default=20, env="MAX_SCROLL_ITER_PER_PAGE")
    BROWSER_EXTRA_HTTP_HEADERS: dict = Field(
        default={"Accept-Language": "en-US,en;q=0.9", "Referer": "https://www.google.com/"}
    )
    BROWSER_TIMEOUT: int = Field(default=10000, env="BROWSER_TIMEOUT")


load_dotenv()
config = Config()

ACTION_TYPES = Literal["venda"]

REAL_ESTATE_TYPES = Literal[
    "imoveis",
    "apartamentos",
    "studio",
    "quitinetes",
    "casas",
    "sobrados",
    "casas-de-condominio",
    "cobertura",
    "flat",
    "loft",
    "terrenos-lotes-condominios",
    "fazendas-sitios-chacaras",
    "loja-salao",
    "conjunto-comercial-sala",
    "casa-comercial",
    "hoteis-moteis-pousadas",
    "terrenos-lotes-comerciais",
    "galpao-deposito-armazem",
    "box-garagem",
]
