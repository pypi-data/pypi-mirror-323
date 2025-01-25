"""
Main interface for kafkaconnect service.

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_kafkaconnect import (
        Client,
        KafkaConnectClient,
        ListConnectorOperationsPaginator,
        ListConnectorsPaginator,
        ListCustomPluginsPaginator,
        ListWorkerConfigurationsPaginator,
    )

    session = Session()
    client: KafkaConnectClient = session.client("kafkaconnect")

    list_connector_operations_paginator: ListConnectorOperationsPaginator = client.get_paginator("list_connector_operations")
    list_connectors_paginator: ListConnectorsPaginator = client.get_paginator("list_connectors")
    list_custom_plugins_paginator: ListCustomPluginsPaginator = client.get_paginator("list_custom_plugins")
    list_worker_configurations_paginator: ListWorkerConfigurationsPaginator = client.get_paginator("list_worker_configurations")
    ```

Copyright 2025 Vlad Emelianov
"""

from .client import KafkaConnectClient
from .paginator import (
    ListConnectorOperationsPaginator,
    ListConnectorsPaginator,
    ListCustomPluginsPaginator,
    ListWorkerConfigurationsPaginator,
)

Client = KafkaConnectClient


__all__ = (
    "Client",
    "KafkaConnectClient",
    "ListConnectorOperationsPaginator",
    "ListConnectorsPaginator",
    "ListCustomPluginsPaginator",
    "ListWorkerConfigurationsPaginator",
)
