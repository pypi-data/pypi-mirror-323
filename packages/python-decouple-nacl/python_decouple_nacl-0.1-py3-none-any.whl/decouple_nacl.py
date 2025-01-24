# pylint: disable=wildcard-import, unused-wildcard-import
# pylint: disable=redefined-builtin, redefined-outer-name
# pylint: disable=protected-access, no-member

from __future__ import annotations

import base64
import functools
import re
from typing import Mapping, Optional

from decouple import *  # Tarjotaan `python-decouple`-paketin sisältö.

from nacl.exceptions import CryptoError
from nacl.public import PrivateKey, PublicKey, SealedBox


YKSITYINEN_AVAIN = 'DECOUPLE_NACL_SK'
JULKINEN_AVAIN = 'DECOUPLE_NACL_PK'
SALATTU = re.compile(r'!{([^}]+)}')


class VirheellinenAvain(RuntimeError):
  ''' Parametrisoidut yksityinen ja julkinen avain eivät täsmää. '''


def julkinen_avain(config: Config | AutoConfig) -> PublicKey:
  return config(
    JULKINEN_AVAIN,
    cast=lambda pk: PublicKey(base64.b64decode(pk))
  )
  # def julkinen_avain -> PublicKey


def yksityinen_avain(config: Config | AutoConfig) -> PrivateKey:
  '''
  Lue ja palauta Base-64-koodattu yksityinen avain.

  Mikäli julkinen avain on parametrisoitu, verrataan sitä yksityiseen ja
  nostetaan tarvittaessa poikkeus.

  Mikäli yksityisiä avaimia on lueteltu useita, vaaditaan (yksi)
  julkinen avain ja palautetaan sitä vastaava yksityinen avain.
  '''
  yksityiset_avaimet: list[PrivateKey] = config(
    YKSITYINEN_AVAIN,
    cast=Csv(
      cast=lambda sk: PrivateKey(base64.b64decode(sk)),
      strip=' '
    ),
  )

  try:
    _julkinen_avain = julkinen_avain(config)

  except UndefinedValueError as exc:
    try:
      ainoa_yksityinen_avain, = yksityiset_avaimet
      return ainoa_yksityinen_avain
    except ValueError:
      raise VirheellinenAvain(
        'Useita yksityisiä avaimia. Julkinen avain on määritettävä.'
      ) from exc

  else:
    for yksityinen_avain in yksityiset_avaimet:
      if (
        todellinen_julkinen_avain := yksityinen_avain.public_key
      ) == _julkinen_avain:
        return yksityinen_avain
    try:
      # Anna viimeisin, julkinen avain virhesanoman mukana.
      raise VirheellinenAvain(
        f'Julkinen avain ei täsmää. Käytössä on:\n'
        f'{base64.b64encode(todellinen_julkinen_avain.encode()).decode()}'
      )
    except NameError:
      raise VirheellinenAvain('Ei yhtään yksityistä avainta!') from None
  # def yksityinen_avain -> PrivateKey


@functools.lru_cache(maxsize=None)
def avaaja(config: Config | AutoConfig) -> SealedBox:
  ''' Lue Base-64-koodattu yksityinen avain ja alusta `SealedBox`. '''
  return SealedBox(yksityinen_avain(config))


@functools.lru_cache(maxsize=None)
def salaaja(config: Config | AutoConfig) -> SealedBox:
  ''' Lue Base-64-koodattu julkinen avain ja alusta `SealedBox`. '''
  return SealedBox(julkinen_avain(config))


def avattu(arvo: str, config: Config | AutoConfig) -> tuple[str, bool]:
  '''
  Korvaa salatut (Base-64-koodatut) merkkijonot selväkielisillä vastineillaan.

  Huomaa, että avaamiseen käytetty yksityinen avain haetaan (tarvittaessa)
  `config(...)`-kutsun avulla.

  Palautetaan avattu merkkijono sekä tieto siitä, oliko arvo salattu.
  '''
  oli_salattu: bool = False

  def parametrin_avaus(salattu: re.Match) -> str:
    nonlocal oli_salattu
    oli_salattu = True
    salattu = base64.b64decode(salattu.group(1))
    return avaaja(config).decrypt(salattu).decode()

  return SALATTU.sub(parametrin_avaus, arvo), oli_salattu
  # def avattu


def laajenna_toteutus(luokka: type):
  '''
  Puukota __init__- ja __getitem__-toteutukset Repository-toteutusluokassa.
  '''
  @functools.wraps(luokka.__init__)
  def __init__(
    repository: RepositoryIni | RepositoryEnv,
    *args,
    autoconfig: Optional[AutoConfig] = None,
    **kwargs
  ):
    '''
    Otetaan vastaan valinnainen `autoconfig`-parametri silloin, kun
    `Repository` alustetaan osana `AutoConfig`-alustusta.

    Asetetaan `self._config`-määre arvonaan joko tämä `AutoConfig`-olio
    tai yksittäisen `Repositoryn` laajuinen `Config`-olio.

    Lisätään tälle `AutoConfig`- tai `Config`-oliolle sanakirja
    `_salatut_parametrit`, johon pyydetyt, salatut alkuperäiset arvot
    tallennetaan.
    '''
    __init__.__wrapped__(repository, *args, **kwargs)
    repository._config = config = autoconfig or Config(repository)
    config._salatut_parametrit = {}
    # def __init__
  luokka.__init__ = __init__

  @functools.wraps(luokka.__getitem__)
  def __getitem__(repository, avain):
    ''' Tulkitaan mahdolliset salatut arvot. '''
    try:
      tulos, oli_salattu = avattu(
        alkuperainen := __getitem__.__wrapped__(repository, avain),
        config=(config := repository._config)
      )
    except CryptoError as exc:
      raise ValueError(
        f'Salatun arvon purku avaimella {avain} ei onnistunut.'
      ) from exc
    if oli_salattu:
      config._salatut_parametrit[avain] = alkuperainen
    return tulos
    # def __getitem__
  luokka.__getitem__ = __getitem__
  # def laajenna_toteutus


# Laajennetaan toteutukset `.ini`- ja `.env`-tiedostoja luettaessa.
laajenna_toteutus(RepositoryIni)
RepositoryIni.__iter__ = lambda ri: iter(ri.parser[ri.SECTION])
laajenna_toteutus(RepositoryEnv)
RepositoryEnv.__iter__ = lambda re: iter(re.data)


# Ota talteen alkuperäinen (staattinen) `SUPPORTED`-taulu.
_alkuperainen_SUPPORTED: Mapping = AutoConfig.SUPPORTED


def supported(autoconfig: AutoConfig) -> Mapping:
  ''' Lisää alustusparametri `autoconfig` kullekin tuetulle toteutukselle. '''
  return type(_alkuperainen_SUPPORTED)(
    (avain, functools.partial(arvo, autoconfig=autoconfig))
    for avain, arvo in _alkuperainen_SUPPORTED.items()
  )


# Aseta oliokohtaisesti välimuistitettu `SUPPORTED`-toteutus AutoConfigille.
AutoConfig.SUPPORTED = functools.cached_property(supported)
AutoConfig.SUPPORTED.__set_name__(AutoConfig, 'SUPPORTED')
