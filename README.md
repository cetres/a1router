# a1router
Read informations from home routers. I tested with my own D-link model DR-809.
But it is extensible and can inherit from a master class Router

```python
class Lynksys(Router):
    def get_wan_address(self):
        <create your own implementation>

```


A configuration file at ~/.a1router should be as follows:

```yaml
ip_Address: 192.168.0.1
username: admin
password: <insert_your_secret_password>
assoc_event:
  type: sqs
  region: sa-east-1
  queue: a1router
  status: /var/run/a1router/rstatus.yaml
```
