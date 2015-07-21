import itertools
import json
import avro


__author__ = 'GA4GH'


class ProtocolElementEncoder(json.JSONEncoder):
    """
    Class responsible for encoding ProtocolElements as JSON.
    """
    def default(self, obj):
        if isinstance(obj, ProtocolElement):
            # Added if getattr(obj, a) is not None, this prevent printing nulls
            ret = {a: getattr(obj, a) for a in obj.__slots__ if getattr(obj, a) is not None}
        else:
            ret = super(ProtocolElementEncoder, self).default(obj)
        return ret



class ProtocolElement(object):
    """
    Superclass of GA4GH protocol elements. These elements are in one-to-one
    correspondence with the Avro definitions, and provide the basic elements
    of the on-the-wire protocol.
    """
    def __str__(self):
        return "{0}({1})".format(self.__class__.__name__, self.toJsonString())

    def __eq__(self, other):
        """
        Returns True if all fields in this protocol element are equal to the
        fields in the specified protocol element.
        """
        if type(other) != type(self):
            return False

        fieldNames = itertools.imap(lambda f: f.name, self.schema.fields)
        return all(getattr(self, k) == getattr(other, k) for k in fieldNames)

    def __ne__(self, other):
        return not self == other

    def toJsonString(self):
        """
        Returns a JSON encoded string representation of this ProtocolElement.
        """
        return json.dumps(self, cls=ProtocolElementEncoder)

    def toJsonDict(self):
        """
        Returns a JSON dictionary representation of this ProtocolElement.
        """
        out = {}

        for field in self.schema.fields:
            val = getattr(self, field.name)

            if self.isEmbeddedType(field.name):
                if isinstance(val, list):
                    out[field.name] = list(el.toJsonDict() for el in val)
                elif val is None:
                    pass
                else:
                    out[field.name] = val.toJsonDict()
            elif isinstance(val, list):
                out[field.name] = list(val)
            else:
                if val == None:
                    pass
                else:
                    out[field.name] = val
        return out

    @classmethod
    def validate(cls, jsonDict):
        """
        Validates the specified JSON dictionary to determine if it is an
        instance of this element's schema.
        """
        return avro.io.validate(cls.schema, jsonDict)

    @classmethod
    def fromJsonString(cls, jsonStr):
        """
        Returns a decoded ProtocolElement from the specified JSON string.
        """
        jsonDict = json.loads(jsonStr)
        return cls.fromJsonDict(jsonDict)

    @classmethod
    def fromJsonDict(cls, jsonDict):
        """
        Returns a decoded ProtocolElement from the specified JSON dictionary.
        """
        if jsonDict is None:
            raise ValueError("Required values not set in {0}".format(cls))

        instance = cls()
        for field in cls.schema.fields:
            instanceVal = field.default
            if field.name in jsonDict:
                val = jsonDict[field.name]
                if cls.isEmbeddedType(field.name):
                    instanceVal = cls._decodeEmbedded(field, val)
                else:
                    instanceVal = val
            setattr(instance, field.name, instanceVal)
        return instance

    @classmethod
    def _decodeEmbedded(cls, field, val):
        if val is None:
            return None

        embeddedType = cls.getEmbeddedType(field.name)
        if isinstance(field.type, avro.schema.ArraySchema):
            return list(embeddedType.fromJsonDict(elem) for elem in val)
        else:
            return embeddedType.fromJsonDict(val)
