from typing import Dict, List

from app.models.sale import Sale
from app.repositories.sale_repository import SaleRepository

_sales_store: Dict[int, Sale] = {}

class SaleService:

    @classmethod
    def list_all(cls) -> List[Sale]:
        return list(_sales_store.values())

    @classmethod
    def get(cls, sale_id: int) -> Sale:
        sale = _sales_store.get(sale_id)
        if not sale:
            raise ValueError("Продажа не найдена")
        return sale

    @classmethod
    async def create(cls, sale: Sale) -> Sale:
        if sale.sale_id in _sales_store:
            raise ValueError("ID уже существует")
        await SaleRepository.save(sale)
        _sales_store[sale.sale_id] = sale
        return sale

    @classmethod
    async def update(cls, sale_id: int, sale: Sale) -> Sale:
        if sale_id != sale.sale_id or sale_id not in _sales_store:
            raise ValueError("Несовпадающий ID или запись не найдена")
        await SaleRepository.save(sale)
        _sales_store[sale_id] = sale
        return sale

    @classmethod
    async def delete(cls, sale_id: int) -> None:
        if sale_id not in _sales_store:
            raise ValueError("Запись не найдена")
        await SaleRepository.delete(sale_id)
        _sales_store.pop(sale_id, None)