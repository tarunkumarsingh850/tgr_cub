API_ARGS = {
    "customer_details": {
        "code": ("required", str),
        "name": ("not-required", str),
        "address_line_1": ("required", str),
        "address_line_2": ("not-required", str),
        "city": ("not-required", str),
        "state": ("not-required", str),
        "zip": ("not-required", str),
        "country": ("not-required", str),
        "email": ("required", str),
        "phone": ("required", str),
        "mobile": ("not-required", str),
        "warehouse_code": ("required", str),
    },
    "order_details": [
        {
            "product_details": {
                "code": ("required", str),
                "name": ("not-required", str),
                "product_type": ("not-required", str),
                "sale_price": ("not-required", float),
                "product_category": ("not-required", str),
            },
            "currency": ("not-required", str),
            "quantity": ("required", float),
            "unit_price": ("required", float),
            "taxes": ("not-required", float),
        }
    ],
}
