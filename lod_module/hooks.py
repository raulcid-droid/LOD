# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)

INITIAL_STOCK = {
    'material_hormigon_h30': 25.0,
    'material_fierro_a630': 1500.0,
    'material_fierro_a630_8': 800.0,
    'material_moldaje': 150.0,
    'material_cemento': 80.0,
    'material_arena': 15.0,
    'material_alambre': 25.0,
    'material_separadores': 500.0,
}


def _post_init_hook(env):
    """Load initial stock quantities via stock.quant after module install."""
    warehouse = env['stock.warehouse'].search([], limit=1)
    if not warehouse:
        _logger.warning("No warehouse found, skipping initial stock load")
        return

    stock_location = warehouse.lot_stock_id

    for xml_id, qty in INITIAL_STOCK.items():
        full_xml_id = f'lod_module.{xml_id}'
        template = env.ref(full_xml_id, raise_if_not_found=False)
        if not template:
            _logger.warning("Product template %s not found", full_xml_id)
            continue

        product = template.product_variant_id
        if not product:
            _logger.warning("No variant for %s", full_xml_id)
            continue

        env['stock.quant']._update_available_quantity(product, stock_location, qty)
        _logger.info("Loaded %.1f of %s into %s", qty, product.name, stock_location.name)
