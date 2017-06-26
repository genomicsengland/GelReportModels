from protocols.reports_3_0_0 import (
    Actions,
    ReportEvent,
    CancerSample,
    CalledGenotype,
    MatchedSamples,
    ReportedVariant,
    ReportEventCancer,
    ReportedStructuralVariant,
)
from protocols.reports_4_0_0 import Actions as Actions_4_0_0
from protocols.reports_3_1_0 import ReportEvent as ReportEvent_3_1_0
from protocols.reports_3_1_0 import CancerSample as CancerSample_3_1_0
from protocols.reports_3_1_0 import CalledGenotype as CalledGenotype_3_1_0
from protocols.reports_3_1_0 import MatchedSamples as MatchedSamples_3_1_0
from protocols.reports_3_1_0 import ReportedVariant as ReportedVariant_3_1_0
from protocols.reports_4_0_0 import ReportEventCancer as ReportEventCancer_4_0_0
from protocols.reports_3_1_0 import ReportedStructuralVariant as ReportedStructuralVariant_3_1_0

TYPES_CONTAINED_WITHIN_ARRAYS = (
    Actions,
    ReportEvent,
    CancerSample,
    Actions_4_0_0,
    CalledGenotype,
    MatchedSamples,
    ReportedVariant,
    ReportEventCancer,
    ReportEvent_3_1_0,
    CancerSample_3_1_0,
    CalledGenotype_3_1_0,
    MatchedSamples_3_1_0,
    ReportedVariant_3_1_0,
    ReportEventCancer_4_0_0,
    ReportedStructuralVariant,
    ReportedStructuralVariant_3_1_0,
)


class MockTestObject(object):

    def __init__(self, object_type):
        self.object_type = object_type

    def set_embedded_objects(self, new_gel_object):
        for field_key in new_gel_object.schema.fields_dict.keys():
            if new_gel_object.isEmbeddedType(field_key):
                embedded_object = new_gel_object.getEmbeddedType(field_key)()
                schema_fields = embedded_object.schema.fields_dict.keys()
                embedded_objects_present = [embedded_object.isEmbeddedType(field) for field in schema_fields]
                embedded_object_types = [
                    embedded_object.getEmbeddedType(field) for field in schema_fields
                    if embedded_object.isEmbeddedType(field)
                ]
                if any(embedded_objects_present):
                    if not (len(embedded_object_types) == 1 and isinstance(embedded_object, embedded_object_types[0])):
                        self.set_embedded_objects(embedded_object)
                    else:
                        setattr(new_gel_object, field_key, embedded_object)
                if isinstance(embedded_object, TYPES_CONTAINED_WITHIN_ARRAYS):
                    setattr(new_gel_object, field_key, [embedded_object])
                else:
                    setattr(new_gel_object, field_key, embedded_object)

    def get_valid_empty_object(self):
        new_gel_object = self.object_type()
        self.set_embedded_objects(new_gel_object)
        return new_gel_object
