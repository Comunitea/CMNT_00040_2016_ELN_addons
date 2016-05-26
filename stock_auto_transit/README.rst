.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
Stock Auto Transit
==================

This module allows to transfer automatically the second picking of a transfer
that involves a transit location.

When yo process the first picking to a transit location, the next chained
picking from transit location to destination location will be automatically
done.

Also we let to reserve quantity and lots of products that will be traspased
and reconciliare later the negative quants.

You must set the orig location field in stock routes, when te route involves
a transit.
Also tou must set the picking types that get the product to a transit location
with the auto transit check. When a picking is transfered, if it is marked as
autotransit, The system will propose the quantity and lots to reconciliare the
negative quants created when forcinf the sale.


Credits
=======

Contributors
------------
* Comunitea.
* Javier Colmenero Fernández <javier@comunitea.com>


Maintainer
----------
This module is maintained by Comunitea.
