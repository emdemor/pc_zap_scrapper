from pc_zap_scrapper.v2.config import config
from pc_zap_scrapper.v2.database import DatabaseHandler, TableRealEstateInfo

__version__ = "2.0.0"

DEFAULT_ACTION = "venda"
DEFAULT_TYPE = "imoveis"
DEFAULT_LOCALIZATION = "mg+pocos-de-caldas"

__all__ = [
    "__version__",
    "config",
    "DatabaseHandler",
    "TableRealEstateInfo",
    "DEFAULT_ACTION",
    "DEFAULT_TYPE",
    "DEFAULT_LOCALIZATION",
]
