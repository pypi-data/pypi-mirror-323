
import datetime
import uuid

from nsj_rest_lib.entity.entity_base import EntityBase
from nsj_rest_lib.decorator.entity import Entity


@Entity(
    table_name="persona.reajustestrabalhadores",
    pk_field="reajustetrabalhador",
    default_order_fields=["descricao"],
)
class ReajustestrabalhadoreEntity(EntityBase):
    reajustetrabalhador: uuid.UUID = None
    tenant: int = None
    data: datetime.datetime = None
    descricao: str = None
    tipo: int = None
    percentual: int = None
    salarioanterior: int = None
    salarionovo: int = None
    unidadesalarionovo: int = None
    trabalhador: uuid.UUID = None
    reajustesindicato: uuid.UUID = None
    lastupdate: datetime.datetime = None
