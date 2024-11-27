from datetime import datetime
from pydantic import BaseModel

from pc_zap_scrapper.v2.config import config, REAL_ESTATE_TYPES, ACTION_TYPES


class RealEstateInfo(BaseModel):
    id: str | None
    action: str
    search_date: datetime
    post_type: str | None = None
    link: str | None = None
    type: str | None = None
    image_list: list[str] | None = None
    snippet: str | None = None
    street: str | None = None
    neighbor: str | None = None
    city: str | None = None
    state: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    floor_size: int | None = None
    number_of_rooms: int | None = None
    number_of_bathrooms: int | None = None
    number_of_parking_spaces: int | None = None
    amenities_list: list[str] | None = None
    price: float | None = None
    condominium: float | None = None
    iptu: float | None = None


class ZapImoveisURL(BaseModel):
    base_url: str = config.BASE_URL
    action: ACTION_TYPES
    type: REAL_ESTATE_TYPES
    localization: str
    page: str | int | None = None

    @property
    def text(self):
        _page = f"?pagina={self.page}" if self.page else ""
        return f"{self.base_url}/{self.action}/{self.type}/{self.localization}/{_page}"

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text

    def __eq__(self, other):
        if isinstance(other, str):
            return self.text == other
        return super().__eq__(other)

    def __getattr__(self, item):
        if hasattr(self.text, item):
            return getattr(self.text, item)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")

    def __add__(self, other):
        if isinstance(other, str):
            return self.text + other
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, str):
            return other + self.text
        return NotImplemented
