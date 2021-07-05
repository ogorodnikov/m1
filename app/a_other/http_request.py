import http.client

conn = http.client.HTTPSConnection("")

payload = "{\"options\":{\"client_id\":\"\",\"profile\":true,\"scope\":[\"profile\"],\"upstream_params\":{\"blog\":{\"value\":\"myblog.wordpress.com\"}}}}"

headers = {
    'authorization': "Bearer YOUR_ACCESS_TOKEN",
    'content-type': "application/json"
    }

conn.request("PATCH", "/YOUR_DOMAIN/api/v2/connections/YOUR-WORDPRESS-CONNECTION-ID", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))