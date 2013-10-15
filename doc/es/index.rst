============================
Cestas de compra para Nereid
============================

Cestas de la compra para Nereid - herramienta de desarrollo web para Tryton.

 * Cesta: http://domain.com/es/basket/
 * Añadir o actualizar cantidad productos (POST): http://domain.com/en/basket/add/
 * Eliminar producto: http://domain.com/en/basket/remode/ID

Este módulo requiere nereid_catalog y nereid_sale pero no se instalan. Puede usar
otros módulos para la gestión del catálogo o los pedidos de venta. En este caso,
los módulos que usen deben disponer de los menús:

Plantilla
---------

 * esale.catalog.menu.render_list
 * product.product.render

Estas url's son opcionales si usan plantillas personalizadas.

Redirección checkout
--------------------

 * sale.sale.render

Esta url se requiere.
