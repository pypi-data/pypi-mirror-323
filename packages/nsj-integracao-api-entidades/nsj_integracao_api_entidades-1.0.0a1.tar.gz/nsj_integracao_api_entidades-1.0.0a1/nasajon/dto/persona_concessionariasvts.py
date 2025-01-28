
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase

# Imports Lista
from nsj_rest_lib.descriptor.dto_list_field import DTOListField

from nasajon.dto.persona_tarifasconcessionariasvts import TarifasconcessionariasvtDTO
from nasajon.entity.persona_tarifasconcessionariasvts import TarifasconcessionariasvtEntity

# Configuracoes execucao
from nasajon.config import (tenant_is_partition_data)

@DTO()
class ConcessionariasvtDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='concessionariavt',
      resume=True,
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tenant: int = DTOField(
      partition_data=tenant_is_partition_data,
      resume=True,
      not_null=True,)
    codigo: str = DTOField(
      candidate_key=True,
      strip=True,
      resume=True,
      not_null=True,)
    nome: str = DTOField()
    lastupdate: datetime.datetime = DTOField()
    # Atributos de lista
    tarifasconcessionariasvts: list = DTOListField(
      dto_type=TarifasconcessionariasvtDTO,
      entity_type=TarifasconcessionariasvtEntity,
      related_entity_field='concessionariavt'
    )
