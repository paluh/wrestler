wRESTler [![Build Status](https://travis-ci.org/paluh/wrestler.png?branch=master)](https://travis-ci.org/paluh/wrestler) [![Coverage Status](https://coveralls.io/repos/paluh/wrestler/badge.png?branch=master)](https://coveralls.io/r/paluh/wrestler?branch=master)
========

Set of utilities for werkzeug REST services.


# wrestler.ephemeral_routing

Router which authenticates signed url paths with single secret key (check: `itsdangerous.TimestampSigner`). You can define expiration time of your urls.

This approach can be useful if you don't want to reveal authentication credentials, but you want to give temporary access to some external http resources. For example this routing strategy can be used by javascript to access data from other services/parts of your system. To make it usable you have to implement url's mapping refresh (so javascript can refresh expired urls set).


# Testing

To run project test suite (`wrestler.tests.test_suite`) just type:

    $ python setup.py test
