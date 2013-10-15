#This file is part nereid_basket module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from trytond.pool import Pool
from .website import *
from .basket import *

def register():
    Pool.register(
        WebSite,
        Basket,
        module='nereid_basket', type_='model')
