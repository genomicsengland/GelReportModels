
class MigrationError(Exception):

    pass


class BaseMigration(object):

    @staticmethod
    def convert_class(target_klass, instance):
        new_instance = target_klass.fromJsonDict(
            jsonDict=instance.toJsonDict()
        )
        return new_instance

    @staticmethod
    def validate_object(object_to_validate, object_type):
        if object_to_validate.validate(jsonDict=object_to_validate.toJsonDict()):
            return object_to_validate
        else:
            from protocols.util import handle_avro_errors
            from pprint import pprint
            pprint(handle_avro_errors(object_to_validate.validate_parts()))

            for message in object_to_validate.validate(object_to_validate.toJsonDict(), verbose=True).messages:
                print "---------------"
                print message

            raise Exception("New {object_type} object is not valid".format(object_type=object_type))

    @staticmethod
    def convert_string_to_integer(string):
        if string is None:
            return None
        try:
            return int(string)
        except ValueError:
            raise Exception("Value: {string} is not an integer contained in a string !".format(string=string))
