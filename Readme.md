# NetApp StorageGRID Webscale proxy for Grafana
Per official netapp [API docs](https://library.netapp.com/ecm/ecm_download_file/ECMLP2753104) Prometheus metrics are exposed:  
> __metrics__ – Operations on StorageGRID Webscale metrics including instant metric queries at a single point in time and range metric queries over a range of time.
>> __Note__: The Grid Management API uses the Prometheus systems monitoring tool as the backend data source. For information about constructing Prometheus queries, see the Prometheus web site.

But this endpoint is incompatible for direct use by Grafana, because of Token requirements and renamed URI locations.

This proxy fixes incompatibilities and allows to have Grafana dashboards for data inside StorageGRID.

### Quick start
You can use proxy.py directly, or there is docker-compose example with grafana provided for quick check.

First, create User on NetApp with `Metric Query` access rights:  
![](https://habrastorage.org/webt/lt/o9/o6/lto9o6tqvpzmhb878sowpaamhsm.png)

Then create secret file with his creds and endpoint URI, and save it as `napp.json`:
```json
{"username": "zabbix", "password": "pass", "endpoint": "https://napp.local"}
```

Start proxy and grafana:
```bash
docker-compose up
```
Proxy will check access on start, and die with detailed message in case of any issues.
In case everything is up - grafana should be available on your http://localhost

Login with `admin`/`admin` and set the datasource to proxy container:
![](https://habrastorage.org/webt/g4/9_/gj/g49_gjrmoe-5up8efyw39zsrp3k.png)

Then you should see NetApp items:
![](https://habrastorage.org/webt/jk/gn/qa/jkgnqayxgdlnb-_adi1ylwvsgw8.png)

### Use in docker
Image is available on docker hub as: `sepa/netapp-grafana-proxy`  
You can set these environment variables to override defaults:
```
environment:
  PORT: '8080'
  SECRET: /run/secrets/napp.json
```
