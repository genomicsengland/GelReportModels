"""
Definitions of the GA4GH protocol types.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy
import sys
import json
import inspect
import itertools

import avro.io
from avro.schema import UnionSchema, ArraySchema


class ProtocolElementEncoder(json.JSONEncoder):
    """
    Class responsible for encoding ProtocolElements as JSON.
    """
    def default(self, obj):
        if isinstance(obj, ProtocolElement):
            ret = {a: getattr(obj, a) for a in obj.__slots__}
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
                    out[field.name] = None
                else:
                    out[field.name] = val.toJsonDict()
            elif isinstance(val, list):
                out[field.name] = list(val)
            else:
                out[field.name] = val
        return out

    def validate_parts(self):
        out = {}

        for field in self.schema.fields:
            val = getattr(self, field.name)
            if self.isEmbeddedType(field.name):
                if isinstance(val, list):
                    out[field.name] = list(el.validate_parts() for el in val)
                elif val is None:
                    if isinstance(field.type, UnionSchema) and 'null' in [t.type for t in field.type.schemas]:
                        out[field.name] = True
                    else:
                        out[field.name] = False

                else:
                    out[field.name] = val.validate_parts()
            elif isinstance(val, list):
                if isinstance(field.type, UnionSchema):
                    out[field.name] = False
                    for sc in field.type.schemas:
                        if isinstance(sc, ArraySchema):
                            out[field.name] = list(avro.io.validate(sc.items, el) for el in val)
                else:
                    if isinstance(field.type, ArraySchema):
                        out[field.name] = list(avro.io.validate(field.type.items, el) for el in val)
                    else:
                        out[field.name] = False
            else:
                out[field.name] = avro.io.validate(field.type, val)


        return out

    def extended_validation(self):
        for field in self.schema.fields:
            val = getattr(self, field.name)
            if field.type.type == 'string':
                if val == '':
                    return False
        return self.validate(self.toJsonDict())


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
        if isinstance(field.type, UnionSchema):
            if isinstance(field.type.schemas[1], ArraySchema):
                return list(embeddedType.fromJsonDict(elem) for elem in val)
        elif isinstance(field.type, avro.schema.ArraySchema):
            return list(embeddedType.fromJsonDict(elem) for elem in val)
        else:
            return embeddedType.fromJsonDict(val)


class SearchRequest(ProtocolElement):
    """
    The superclass of all SearchRequest classes in the protocol.
    """


class SearchResponse(ProtocolElement):
    """
    The superclass of all SearchResponse classes in the protocol.
    """
    @classmethod
    def getValueListName(cls):
        """
        Returns the name of the list used to store the values held
        in a page of results.
        """
        return cls._valueListName


def getProtocolClasses(superclass=ProtocolElement):
    """
    Returns all the protocol classes that are subclasses of the
    specified superclass. Only 'leaf' classes are returned,
    corresponding directly to the classes defined in the protocol.
    """
    # We keep a manual list of the superclasses that we define here
    # so we can filter them out when we're getting the protocol
    # classes.
    superclasses = set([
        ProtocolElement, SearchRequest, SearchResponse])
    thisModule = sys.modules[__name__]
    subclasses = []
    for name, class_ in inspect.getmembers(thisModule):
        if ((inspect.isclass(class_) and
                issubclass(class_, superclass) and
                class_ not in superclasses)):
            subclasses.append(class_)
    return subclasses


# We can now import the definitions of the protocol elements from the
# generated file.
from GelProtocols import *  # NOQA

