API_ARGS = {
    "customer_details": {
        "code": ("required", str),
        "name": ("required", str),
        "address_line_1": ("required", str),
        "address_line_2": ("not-required", str),
        "city": ("required", str),
        "state": ("not-required", str),
        "zip": ("required", str),
        "country": ("required", str),
        "email": ("required", str),
        "phone": ("required", str),
        "mobile": ("not-required", str),
        "warehouse_code": ("required", str),
    },
    "order_details": [
        {
            "product_details": {
                "code": ("required", str),
                "name": ("required", str),
                "product_type": ("required", str),
                "sale_price": ("required", float),
                "product_category": ("required", str),
            },
            "currency": ("required", str),
            "quantity": ("required", float),
            "unit_price": ("required", float),
            "taxes": ("not-required", float),
        }
    ],
}
