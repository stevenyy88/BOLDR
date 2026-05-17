"""
BOLDR Self-Improving Customer Intelligence Engine
Product Lookup Module — Simulates Shopify product/order lookup for order operations

For the ECHELON 2026 competition, we simulate Shopify lookups using the KB product data.
In production, this would be replaced with real Shopify Storefront API calls.

Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# BOLDR product catalogue (from KB source data)
PRODUCTS = {
    "BLD-EXP-TI-40": {
        "sku": "BLD-EXP-TI-40",
        "name": "Expedition Titanium",
        "price_sgd": 485.00,
        "availability": "IN STOCK",
        "dial_colours": ["Slate Grey", "Forest Green", "Midnight Blue", "Sandstone"],
        "included_strap": "20mm FKM rubber strap (black)",
        "strap_options": ["FKM rubber", "Nylon NATO", "Titanium bracelet", "Leather"],
        "lug_width_mm": 20,
        "safety": {"bpa_free": True, "nickel_free": True, "hypoallergenic": True, "eu_reach": True},
        "warranty": "2 years on movement",
        "case_mm": 40,
        "movement": "Miyota 9015 automatic, 42hr power reserve",
        "water_resistance": "100m (10ATM)",
    },
    "BLD-JRN-TI-38": {
        "sku": "BLD-JRN-TI-38",
        "name": "Journey Titanium",
        "price_sgd": 395.00,
        "availability": "IN STOCK",
        "dial_colours": ["Ivory White", "Charcoal", "Terracotta", "Ocean Blue"],
        "included_strap": "20mm Nylon NATO strap (olive)",
        "strap_options": ["Nylon NATO", "FKM rubber", "Leather", "Mesh bracelet"],
        "lug_width_mm": 20,
        "safety": {"bpa_free": True, "nickel_free": True, "hypoallergenic": True, "eu_reach": True},
        "warranty": "2 years on movement",
        "case_mm": 38,
        "movement": "Miyota 6T33 automatic, 40hr power reserve",
        "water_resistance": "50m (5ATM)",
    },
    "BLD-EXP-TI-40-LE": {
        "sku": "BLD-EXP-TI-40-LE",
        "name": "Expedition Titanium — Ember Limited Edition",
        "price_sgd": 595.00,
        "availability": "SOLD OUT — waitlist available at boldr.co/waitlist",
        "dial_colours": ["Burnt Orange only"],
        "included_strap": "20mm leather strap (cognac)",
        "strap_options": ["Leather (included)"],
        "lug_width_mm": 20,
        "safety": {"bpa_free": True, "nickel_free": True, "hypoallergenic": False, "eu_reach": True},
        "warranty": "2 years on movement",
        "case_mm": 40,
        "movement": "Miyota 9015 automatic, 42hr power reserve",
        "water_resistance": "100m (10ATM)",
    },
}

# Strap catalogue
STRAPS = {
    "FKM Rubber": {"bpa_free": True, "nickel_free": True, "price_sgd": 25, "compatible": "All 20mm models"},
    "Nylon NATO": {"bpa_free": True, "nickel_free": True, "price_sgd": 18, "compatible": "All 20mm models"},
    "Titanium Bracelet": {"bpa_free": True, "nickel_free": False, "price_sgd": 85, "compatible": "Expedition Titanium only"},
    "Leather": {"bpa_free": False, "nickel_free": True, "price_sgd": 30, "compatible": "All 20mm models"},
    "Mesh Bracelet": {"bpa_free": True, "nickel_free": False, "price_sgd": 55, "compatible": "Journey Titanium only"},
}

# Simulated order statuses (in production, these come from Shopify)
ORDER_STATUSES = {
    "ORD-10001": {"status": "shipped", "tracking": "SG123456789", "carrier": "SingPost", "eta": "3-5 business days", "items": ["BLD-EXP-TI-40 (Slate Grey)"]},
    "ORD-10002": {"status": "processing", "tracking": None, "carrier": None, "eta": "2-3 business days", "items": ["BLD-JRN-TI-38 (Charcoal)"]},
    "ORD-10003": {"status": "delivered", "tracking": "SG987654321", "carrier": "SingPost", "eta": "Delivered", "items": ["BLD-EXP-TI-40 (Forest Green)", "FKM Rubber Strap (Red)"]},
}

# Engraving services
ENGRAVING_SERVICES = {
    "basic_20": {"service": "Caseback engraving — up to 20 characters", "price_sgd": 25, "notes": "Standard Roman/Latin script only"},
    "basic_21_40": {"service": "Caseback engraving — 21 to 40 characters", "price_sgd": 40, "notes": "Standard Roman/Latin script only"},
    "cjk": {"service": "Caseback engraving — CJK characters (per character)", "price_sgd": 3.0, "notes": "Up to 15 CJK characters"},
    "buckle": {"service": "Strap buckle engraving — up to 10 characters", "price_sgd": 15, "notes": "Metal buckle only; not available on rubber/NATO"},
    "logo": {"service": "Logo/symbol engraving (custom vector art)", "price_sgd": 60, "notes": "Customer must supply vector file (.ai or .svg)"},
}

# Servicing tiers
SERVICING_TIERS = {
    "battery": {"service": "Battery Replacement", "price_sgd": 35, "turnaround_days": "3-5", "notes": "Quartz movements only"},
    "regulation": {"service": "Regulation Service", "price_sgd": 85, "turnaround_days": "7-10", "notes": "Automatic movements only"},
    "full_standard": {"service": "Full Service — Standard", "price_sgd": 160, "turnaround_days": "14-21", "notes": "Recommended every 3-5 years"},
    "full_premium": {"service": "Full Service — Premium", "price_sgd": 220, "turnaround_days": "14-21", "notes": "Includes 12-month service warranty"},
    "crystal": {"service": "Crystal Replacement", "price_sgd": 65, "turnaround_days": "5-7", "notes": "OEM sapphire crystal"},
}


@dataclass
class ProductLookupResult:
    """Result of a product lookup."""
    found: bool
    product: Optional[dict] = None
    straps: Optional[list] = None
    engraving: Optional[dict] = None
    servicing: Optional[dict] = None
    order: Optional[dict] = None
    message: str = ""


def lookup_product(query: str) -> ProductLookupResult:
    """Look up a product, strap, engraving, or servicing by keyword search.

    In production, this would call the Shopify Storefront API.
    For the competition, we simulate with the KB product data.
    """
    query_lower = query.lower().strip()

    # Check order status (simulated Shopify lookup)
    for order_id, order_info in ORDER_STATUSES.items():
        if order_id.lower() in query_lower:
            return ProductLookupResult(
                found=True,
                order=order_info,
                message=f"Order {order_id} found. Status: {order_info['status']}. "
                        f"Items: {', '.join(order_info['items'])}. "
                        f"{'Tracking: ' + order_info['tracking'] + ' via ' + order_info['carrier'] if order_info['tracking'] else 'Not yet shipped.'}"
            )

    # Check product lookup by name, SKU, or keyword
    product_keywords = {
        "BLD-EXP-TI-40": ["expedition", "titanium", "exp", "40mm"],
        "BLD-JRN-TI-38": ["journey", "titanium", "jrn", "38mm"],
        "BLD-EXP-TI-40-LE": ["ember", "limited edition", "le", "burnt orange"],
    }

    for sku, keywords in product_keywords.items():
        if any(kw in query_lower for kw in keywords) or sku.lower() in query_lower:
            product = PRODUCTS[sku]
            return ProductLookupResult(
                found=True,
                product=product,
                straps=STRAPS,
                message=f"Product found: {product['name']} (SKU: {sku}). "
                        f"Price: SGD {product['price_sgd']:.2f}. "
                        f"Availability: {product['availability']}. "
                        f"Dial colours: {', '.join(product['dial_colours'])}. "
                        f"Strap options: {', '.join(product['strap_options'])}."
            )

    # Check strap lookup
    strap_keywords = {
        "FKM Rubber": ["fkm", "rubber", "rubber strap", "bpa-free strap", "silicone"],
        "Nylon NATO": ["nato", "nylon", "nylon nato", "nato strap"],
        "Titanium Bracelet": ["bracelet", "titanium bracelet", "metal bracelet"],
        "Leather": ["leather", "leather strap", "cognac"],
        "Mesh Bracelet": ["mesh", "mesh bracelet"],
    }
    for strap_name, keywords in strap_keywords.items():
        if any(kw in query_lower for kw in keywords):
            strap_info = STRAPS[strap_name]
            return ProductLookupResult(
                found=True,
                straps={strap_name: strap_info},
                message=f"Strap found: {strap_name}. Price: SGD {strap_info['price_sgd']:.2f}. "
                        f"BPA-free: {strap_info['bpa_free']}. Compatible with: {strap_info['compatible']}."
            )

    # Check engraving lookup
    if "engrav" in query_lower or "laser" in query_lower:
        return ProductLookupResult(
            found=True,
            engraving=ENGRAVING_SERVICES,
            message="Engraving services available. Basic engraving starts at SGD 25 for up to 20 characters. "
                    "CJK characters available at SGD 3 per character. Rush engraving (same-day) available at SGD 20 surcharge."
        )

    # Check servicing lookup
    servicing_keywords = {
        "battery": ["battery", "battery replacement"],
        "regulation": ["regulation", "regulate", "accuracy"],
        "full_standard": ["full service", "overhaul", "standard service"],
        "full_premium": ["premium service", "premium"],
        "crystal": ["crystal", "sapphire", "scratch"],
    }
    for tier_key, keywords in servicing_keywords.items():
        if any(kw in query_lower for kw in keywords):
            tier = SERVICING_TIERS[tier_key]
            return ProductLookupResult(
                found=True,
                servicing={tier_key: tier},
                message=f"Servicing found: {tier['service']}. Price: SGD {tier['price_sgd']}. "
                        f"Turnaround: {tier['turnaround_days']} days. Notes: {tier['notes']}."
            )

    # No match found
    return ProductLookupResult(
        found=False,
        message=f"No product, strap, servicing, or order found matching: '{query}'. "
                f"This may require a live Shopify lookup in production."
    )