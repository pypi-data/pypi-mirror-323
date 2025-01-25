---
description: my_api.group_call_center_overflow()
---

# 🌊 PUT - Group Call Center Overflow

Update the overflow settings of a single Call Center (CC).

### Parameters&#x20;

* call\_center\_user\_id (str): Service user ID of the target CC.&#x20;
* updates (dict): Updates to apply to target CC.

### Returns

* None: This method does not return any specific value.

### How To Use:

```python
from odins_spear import api

my_api= api.Api(base_url="https://base_url/api/vx", username="john.smith", password="ODIN_INSTANCE_1")
my_api.authenticate()

my_call_center = "call_center_user_id@domain.com"
my_updates= {
	"action":"Busy",
	"transferPhoneNumber":null,
	"overflowAfterTimeout":true,
	"timeoutSeconds":30,
	"playAnnouncementBeforeOverflowProcessing":true,
	"audioMessageSource":"Default",
	"videoMessageSource":"Default",
	"audioUrlList":[],
	"videoUrlList":[],
	"audioFileList":[],
	"videoFileList":[]
}

my_api.put.group_call_center_forced_forwarding(
    call_center_user_id = my_call_center,
    updates = my_updates
)
```
