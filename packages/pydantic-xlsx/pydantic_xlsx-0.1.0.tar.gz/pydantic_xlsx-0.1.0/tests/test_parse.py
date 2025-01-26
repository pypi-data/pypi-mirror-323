from pydantic_xlsx import XlsxModel, XlsxField
from pydantic import Field
from pathlib import Path

class PartnerBase(XlsxModel):
    type: str = Field(validation_alias='Тип партнера')
    name: str = XlsxField(validation_alias='Наименование партнера')
    director: str = XlsxField(validation_alias='Директор')
    email: str = XlsxField(validation_alias='Электронная почта партнера')
    telephone: str = XlsxField(validation_alias='Телефон партнера')
    legal_address: str = XlsxField(validation_alias='Юридический адрес партнера')


class Partners_import(PartnerBase):
    pass

class Partners(PartnerBase):
    __sheetname__ = 'Partners_import'

def test_parsed_values():



    path = Path(__file__).parent / 'data.xlsx'
    partners = Partners.from_file(path)
    for part in partners:
        assert (isinstance(part, Partners))



def test_sheetname_parse():
    path = Path(__file__).parent / 'data.xlsx'
    partners = Partners.from_file(path)
    partners2 = Partners_import.from_file(path)

    for part1, part2 in zip(partners, partners2):
        assert (isinstance(part1, Partners) is isinstance(part2, Partners_import))




