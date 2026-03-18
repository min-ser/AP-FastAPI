from azure.search.documents.indexes.models import (
    ComplexField,
    CorsOptions,
    SearchIndex,
    ScoringProfile,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
)

def create_index(data,client):
    # [START create_index]
    result = ""
    result+="[START create_index]" + "\n"
    name = data.aisearch_index_name
    fields = [
        SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
        SimpleField(name="baseRate", type=SearchFieldDataType.Double),
        SearchableField(name="description", type=SearchFieldDataType.String),
        ComplexField(name="address", fields=[
            SimpleField(name="streetAddress", type=SearchFieldDataType.String),
            SimpleField(name="city", type=SearchFieldDataType.String),
        ])
    ]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    scoring_profiles = []
    index = SearchIndex(
        name=name,
        fields=fields,
        scoring_profiles=scoring_profiles,
        cors_options=cors_options)

    result = client.create_index(index)
    # [END create_index]
    return "[END create_index] + \n" + result

def get_index(data,client):
    # [START get_index]
    result = ""
    result+="[START get_index]" + "\n"
    try:
        name = data.aisearch_index_name
        print("data.aisearch_index_name : ",data.aisearch_index_name)
        print("client.get_index(name) : ",type(client.get_index(name)))
        result += "Get Index : " + str(client.get_index(name)) + "\n"
        result += "[END get_index]" + "\n"
    except Exception as e:
        result += Exception + str(e)
        return result
    # [END get_index]
    return result

def get_index_list(data,client):
    # [START get_index]
    result = ""
    result+="[START get_index_list]" + "\n"
    
    try:
        indexes = client.list_indexes()
        index_list = list(indexes)
        if index_list:
            for index in index_list:
                result += index.name + "\n"
        else :
            result += data.aisearch_endpoint + "에 생성된 INDEX가 없습니다."
    except Exception as e:
        result += "Exception : "+str(e)
    
    result += "[END get_index_list]" + "\n"

    # [END get_index]
    return result

def update_index(data,client):
    # [START update_index]
    result = ""
    result+="[START update_index]" + "\n"
    name = data.aisearch_index_name
    fields = [
        SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
        SimpleField(name="baseRate", type=SearchFieldDataType.Double),
        SearchableField(name="description", type=SearchFieldDataType.String),
        SearchableField(name="hotelName", type=SearchFieldDataType.String),
        ComplexField(name="address", fields=[
            SimpleField(name="streetAddress", type=SearchFieldDataType.String),
            SimpleField(name="city", type=SearchFieldDataType.String),
            SimpleField(name="state", type=SearchFieldDataType.String),
        ])
    ]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    scoring_profile = ScoringProfile(
        name="MyProfile"
    )
    scoring_profiles = []
    scoring_profiles.append(scoring_profile)
    index = SearchIndex(
        name=name,
        fields=fields,
        scoring_profiles=scoring_profiles,
        cors_options=cors_options)

    result = client.create_or_update_index(index=index)
    # [END update_index]
    return "[END update_index] + \n" + result

def delete_index(data,client):
    # [START delete_index]
    result = ""
    result+="[START delete_index]" + "\n"
    name = data.aisearch_index_name
    result += name + " is deleted .."
    client.delete_index(name)
    # [END delete_index]
    return "[END delete_index] + \n"