import json
from http import HTTPStatus
from typing import List, Optional, Any
from pydantic import BaseModel

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.error import HTTPError



class Price(BaseModel):
    mainValue: int | None = None
    emptyValue: bool | None = None
    belowPrice: bool | None = None
    multiplePrices: bool | None = None

class Address(BaseModel):
    city: str | None = None
    stateAcronym: str | None = None
    neighborhood: str | None = None
    isApproximateLocation: bool | None = None

class Image(BaseModel):
    src: str | None = None
    alt: str | None = None
    isPriority: bool | None = None

class Amenities(BaseModel):
    usableAreas: str | None = None
    bedrooms: str | None = None
    bathrooms: str | None = None
    parkingSpaces: str | None = None
    values: List[str] | None = None

class RealEstate(BaseModel):
    id: str | None = None
    legacyId: int | None = None
    name: str | None = None
    advertiserUrl: str | None = None
    tier: str | None = None
    license: str | None = None
    createdDate: str | None = None
    phoneNumbers: List[str] | None = None
    whatsAppNumber: str | None = None
    defaultMessage: str | None = None
    totalCountByFilter: int | None = None
    totalCountByAdvertiser: int | None = None
    isVerified: bool | None = None
    isPremium: bool | None = None
    imageUrl: str | None = None

class AdvertiserLogo(BaseModel):
    src: str | None = None
    alt: str | None = None

class RealEstateElement(BaseModel):
    id: str
    externalId: str
    contractType: str | None = None
    href: str | None = None
    prices: Price | None = None
    address: Address | None = None
    business: str | None = None
    highlight: str | None = None
    imageList: List[Image] | None = None
    amenities: Amenities | None = None
    realEstate: RealEstate | None = None
    visualized: bool | None = None
    description: str | None = None
    isNoWarrantorRent: bool | None = None
    constructionStatus: str | None = None
    expansionType: str | None = None
    sourceId: str | None = None
    stamps: List[str] | None = None
    unitTypes: List[str] | None = None
    displayAddressType: str | None = None
    advertiserLogo: AdvertiserLogo | None = None
