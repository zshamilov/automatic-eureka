import requests

class Pet:
    def __init__(self, id, name=None, photoUrls=None, tags=None, status=None, category=None):
        self.id = id
        self.category = category
        self.name = name
        self.photoUrls = photoUrls
        self.tags = tags
        self.status = status

endpoint = "https://petstore.swagger.io/v2"
payload = {"status": "available"}
response = requests.get(endpoint+"/pet/findByStatus", params=payload)

pet_list = []
i=0
for pet in response.json():

    pet_list.append(Pet(**pet))
    i+=1

print(pet_list)