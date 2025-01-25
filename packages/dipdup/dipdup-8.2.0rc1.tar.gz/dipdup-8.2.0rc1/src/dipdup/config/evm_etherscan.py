from __future__ import annotations

import logging
from typing import Literal

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from dipdup.config import DatasourceConfig
from dipdup.config import HttpConfig

_logger = logging.getLogger(__name__)


@dataclass(config=ConfigDict(extra='forbid', defer_build=True), kw_only=True)
class EvmEtherscanDatasourceConfig(DatasourceConfig):
    """Etherscan datasource config

    :param kind: always 'evm.etherscan'
    :param url: API URL
    :param api_key: API key
    :param http: HTTP client configuration
    """

    # NOTE: Alias, remove in 9.0
    kind: Literal['evm.etherscan'] | Literal['abi.etherscan']
    url: str
    api_key: str | None = None

    http: HttpConfig | None = None

    def __post_init__(self) -> None:
        if self.kind == 'abi.etherscan':
            _logger.warning(
                '`abi.etherscan` datasource has been renamed to `evm.etherscan`. Please, update your config.'
            )
