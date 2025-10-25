class BaseResponseModel:

    @classmethod
    def schema(cls) -> dict:
        convert = {
            "bool": "BOOLEAN",
            "str": "STRING",
            "list": "ARRAY",
        }
        properties_list = [k for k in cls.__annotations__.keys()]
        properties = {}

        for k, v in cls.__annotations__.items():
            title = " ".join(map(str.capitalize, k.split("_")))
            name = convert.get(v.__name__, None)

            properties[str(k)] = {
                "title": title,
                "type": name,
            }
            if name == "ARRAY":
                for i in v.__args__:
                    properties[str(k)]["items"] = {
                        "type": convert.get(i.__name__, None),
                    }

        res = {
            "responseSchema": {
                "properties": properties,
                "property_ordering": properties_list,
                "required": properties_list,
                "title": cls.__name__,
                "type": "OBJECT"
            }
        }
        return res
