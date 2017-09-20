
class BaseMigration(object):

    @staticmethod
    def validate_object(object_to_validate, object_type):
        if object_to_validate.validate(jsonDict=object_to_validate.toJsonDict()):
            return object_to_validate
        else:
            from protocols.util import handle_avro_errors
            from pprint import pprint
            pprint(handle_avro_errors(object_to_validate.validate_parts()))
            raise Exception("New {object_type} object is not valid".format(object_type=object_type))
