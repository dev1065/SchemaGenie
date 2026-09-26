from ai.requirement_reconciler import reconcile_requirements

existing_requirements = [
    {"id": 4, "key": "product_type", "value": "physical products"},
    {
        "id": 5,
        "key": "account_required_for_purchase",
        "value": "users must create an account before purchasing",
    },
]

new_requirements = [
    {"key": "product_types", "value": "physical and digital products"},
    {
        "key": "account_requirement",
        "value": "users must create an account before purchasing",
    },
]

result = reconcile_requirements(existing_requirements, new_requirements)

print(result)
