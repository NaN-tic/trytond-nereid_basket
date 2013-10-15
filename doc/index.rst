Nereid Basket
#############

Sale Basket management for Nereid - webdevelopment framework for Python based on Tryton.

 * Basket: http://domain.com/en/basket/
 * Add or update Qty products (POST): http://domain.com/en/basket/add/
 * Delete product: http://domain.com/en/basket/remode/ID

This module depend nereid_catalog and nereid_sale modules but not install when
install nereid_basket. You could use other modules to find products (catalog)
or show sale order details.

In this case, your modules are available those menus:

Template
--------

 * esale.catalog.menu.render_list
 * product.product.render

Those urls are optional.


Return checkout
---------------

 * sale.sale.render

This url is required.
