from onshape_client.client import Client
from onshape_client import OnshapeElement
import json


base_url = "https://cad.onshape.com"
key = "wtetTUuWUCOUBSC7dcv91V63"
secret = "HJzAszERUJOPF0ZJ0R52eSmG2GMhuaZM443GPwif83yWHLEA"

headers = {'Accept': 'application/vnd.onshape.v1+json',
                        'Content-Type': 'application/json'}

client = Client(configuration={"base__url": base_url, "access_key": key, "secret_key": secret})


element = OnshapeElement("https://cad.onshape.com/documents/a4f9abf1124e12655723aa0d/w/b2c4401adbd69cbd832fcf08/e/1db4a92312fb22a4516841a5")

print(element.did)
print(element.wvmid)
print(element.wvm)
print(element.eid)

query_params = {}


url=base_url + '/api/v5' + '/variables/d/' + element.did + '/' + element.wvm + "/" + element.wvmid + "/e/" + element.eid + "/variables"
print(url)
r = client.api_client.request('GET', url=base_url + '/api/v5' + '/variables/d/' + element.did + '/' + element.wvm + "/" + element.wvmid + "/e/" + element.eid + "/variables", query_params=query_params, headers=headers)
x = json.loads(r.data)

all_variables = x[0]["variables"]
modifiableVariables = {"e_a", "l_a", "rho_a", "e_f", "l_f", "rho_f", "d", "N", "tip_stop", "bottom_stop", "t"}
variables = []
for i in range(0,len(all_variables)):
    name = all_variables[i]["name"]
    if name in modifiableVariables:
        vu = all_variables[i]["expression"].split(" ")
        value = float(vu[0])
        if len(vu) > 1:
            units = vu[1]
        else:
            units = ""
        all_variables[i]["expression"] = float(all_variables[i]["expression"].split(" ")[0])
        all_variables[i]["units"] = units
        variables.append(all_variables[i])

print(variables)


r = client.api_client.request('POST', url=base_url + '/api/v5' + '/variables/d/' + element.did + '/' + element.wvm + "/" + element.wvmid + "/e/" + element.eid + "/variables", query_params=query_params, headers=headers)

