wRESTler
========

Set of utilities for werkzeug REST services.


# wrestler.ephemeral_routing

Router which authenticates signed url paths with single secret key (check: `itsdangerous.TimestampSigner`). You can define expiration time of your urls.

This approach can be useful if you don't want to reveal authentication credentials, but you want to give temporary access to some external http resources. For example this routing strategy can be used by javascript to access data from other services/parts of your system. To make it work you have to implement url's mapping refresh (so javascript can refresh expired urls set).
