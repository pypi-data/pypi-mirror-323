---
description: my_api.get.user_call_forwarding_no_answer()
---

# 🚗 GET - Call Forward No Answer

Retrieves the Forwarding No Answer status for the specified user

### Parameters&#x20;

* user\_id (str): Target User ID

### Returns

* Dict: Forwarding enabled status, and the Number to be Forwarded to.

### How To Use:

{% code overflow="wrap" %}
```python
from odins_spear import api

my_api= api.Api(base_url="https://base_url/api/vx", username="john.smith", password="ODIN_INSTANCE_1")
my_api.authenticate()

my_api.get.user_call_forwarding_no_answer{
    "userId"
}

```
{% endcode %}

### Example Data Returned (Formatted)

```json
{
  "isActive": true,
  "forwardToPhoneNumber": 1234,
  "numberOfRings": 5,
  "userId": "4001@domain.com"
}

```