from protocols import reports_6_0_0
from protocols import reports_5_0_0
from protocols.migration import BaseMigration


class BaseMigrateReports500And600(BaseMigration):
    _tier_domain_mapping = [
        (reports_5_0_0.Tier.TIER1, reports_6_0_0.Domain.DOMAIN1),
        (reports_5_0_0.Tier.TIER2, reports_6_0_0.Domain.DOMAIN2),
        (reports_5_0_0.Tier.TIER3, reports_6_0_0.Domain.DOMAIN3),
        (reports_5_0_0.Tier.TIER4, reports_6_0_0.Domain.DOMAIN4),
        (reports_5_0_0.Tier.TIER5, reports_6_0_0.Domain.NONE),
        (reports_5_0_0.Tier.NONE, reports_6_0_0.Domain.NONE)
    ]

    tier_domain_map = {k: v for k, v in _tier_domain_mapping}
    domain_tier_map = {v: k for k, v in _tier_domain_mapping}

    _clinical_signicance_mapping = [
        (reports_5_0_0.ClinicalSignificance.benign, reports_6_0_0.ClinicalSignificance.benign),
        (reports_5_0_0.ClinicalSignificance.likely_benign, reports_6_0_0.ClinicalSignificance.likely_benign),
        (reports_5_0_0.ClinicalSignificance.pathogenic, reports_6_0_0.ClinicalSignificance.pathogenic),
        (reports_5_0_0.ClinicalSignificance.likely_pathogenic, reports_6_0_0.ClinicalSignificance.likely_pathogenic),
        (reports_5_0_0.ClinicalSignificance.uncertain_significance, reports_6_0_0.ClinicalSignificance.uncertain_significance),
        (reports_5_0_0.ClinicalSignificance.VUS, reports_6_0_0.ClinicalSignificance.uncertain_significance)
    ]

    clinical_signicance_map = {k: v for k, v in _clinical_signicance_mapping}
    clinical_signicance_reverse_map = {v: k for k, v in _clinical_signicance_mapping}