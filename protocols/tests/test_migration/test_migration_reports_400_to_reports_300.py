import factory.fuzzy
from random import randint

from protocols import reports_4_0_0
from protocols import reports_3_0_0
from protocols.util.dependency_manager import VERSION_61
from protocols.util.dependency_manager import VERSION_500
from protocols.util.dependency_manager import VERSION_400
from protocols.util.factories.avro_factory import FactoryAvro
from protocols.util.factories.avro_factory import GenericFactoryAvro
from protocols.migration import MigrationParticipants100ToReports
from protocols.tests.test_migration.base_test_migration import TestCaseMigration
from protocols.migration import MigrateReports400To300


class TestMigrateReports4To3(TestCaseMigration):
    old_model = reports_4_0_0
    new_model = reports_3_0_0

    def _check_variant_coordinates(self, old_variants, new_variants):
        for new_variant, old_variant in zip(new_variants, old_variants):
            self.assertEqual(new_variant.reference, old_variant.reference)
            self.assertEqual(new_variant.alternate, old_variant.alternate)
            self.assertEqual(new_variant.position, old_variant.position)
            self.assertEqual(new_variant.chromosome, old_variant.chromosome)

    def test_migrate_rd_interpreted_genome(self, fill_nullables=True):
        # creates a random interpreted genome RD for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.InterpretedGenomeRD, VERSION_400, fill_nullables=fill_nullables
        ).create(interpretationRequestVersion='1', reportedStructuralVariants=None)  # we need to enforce that it can be cast to int

        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance, exclusions=['reportedStructuralVariants'])

        new_instance = MigrateReports400To300().migrate_interpreted_genome_rd(old_instance=old_instance)
        self.assertIsInstance(new_instance, self.new_model.InterpretedGenomeRD)
        self._validate(new_instance)
        if fill_nullables:
            self._check_variant_coordinates(
                old_variants=old_instance.reportedVariants,
                new_variants=new_instance.reportedVariants,
            )

    def test_migrate_rd_interpreted_genome_fill_nullables_false(self):
        self.test_migrate_rd_interpreted_genome(fill_nullables=False)

    def test_migrate_rd_clinical_report(self, fill_nullables=True):
        # creates a random clinical report RD for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.ClinicalReportRD, VERSION_400, fill_nullables=fill_nullables
        ).create(interpretationRequestVersion='1')  # we need to enforce that it can be cast to int

        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        new_instance = MigrateReports400To300().migrate_clinical_report_rd(old_instance=old_instance)
        self.assertIsInstance(new_instance, self.new_model.ClinicalReportRD)
        self._validate(new_instance)
        if fill_nullables:
            self._check_variant_coordinates(
                old_variants=old_instance.candidateVariants,
                new_variants=new_instance.candidateVariants,
            )

    def test_migrate_rd_clinical_report_fill_nullables_false(self):
        self.test_migrate_rd_clinical_report(fill_nullables=False)

    def test_migrate_rd_exit_questionnaire(self, fill_nullables=True):
        # creates a random clinical report RD for testing filling null values
        old_instance = GenericFactoryAvro.get_factory_avro(
            self.old_model.RareDiseaseExitQuestionnaire, VERSION_400, fill_nullables=fill_nullables
        ).create()  # we need to enforce that it can be cast to int

        self._validate(old_instance)
        if fill_nullables:
            self._check_non_empty_fields(old_instance)

        new_instance = MigrateReports400To300().migrate_exit_questionnaire_rd(old_instance=old_instance)
        self.assertIsInstance(new_instance, self.new_model.RareDiseaseExitQuestionnaire)
        self._validate(new_instance)

        camels = [vq.variantDetails for gq in old_instance.variantGroupLevelQuestions for vq in
                       gq.variantLevelQuestions]
        snakes = [vq.variant_details for gq in new_instance.variantGroupLevelQuestions for vq in
                          gq.variantLevelQuestions]
        for camel, snake in zip(camels, snakes):
            self.assertEqual(camel, snake)  # !!

        camels = [gq.variantGroup for gq in old_instance.variantGroupLevelQuestions]
        snakes = [gq.variant_group for gq in new_instance.variantGroupLevelQuestions]
        for camel, snake in zip(camels, snakes):
            self.assertEqual(camel, snake)  # !!

    def test_migrate_rd_exit_questionnaire_fill_nullables_false(self):
        self.test_migrate_rd_exit_questionnaire(fill_nullables=False)

    def test_migrate_interpretation_request_rd(self):
        ir_rd_4 = self.get_valid_object(
            object_type=self.old_model.InterpretationRequestRD,
            version=self.version_4_0_0,
            fill_nullables=True,
        )
        ir_rd_3 = MigrateReports400To300().migrate_interpretation_request_rd(old_instance=ir_rd_4)
        self.assertIsInstance(ir_rd_3, self.new_model.InterpretationRequestRD)
        self.assertTrue(ir_rd_3.validate(ir_rd_3.toJsonDict()))

    def test_migrate_pedigree(self):
        pedigree_v4 = self.get_valid_object(
            object_type=self.old_model.Pedigree,
            version=self.version_4_0_0,
            fill_nullables=True
        )
        pedigree_v3 = MigrationParticipants100ToReports().migrate_pedigree(old_instance=pedigree_v4)
        self.assertIsInstance(pedigree_v3, self.new_model.Pedigree)
        self.assertTrue(pedigree_v3.validate(pedigree_v3.toJsonDict()))

        for a, d in zip(pedigree_v3.analysisPanels, pedigree_v3.diseasePenetrances):
            self.assertIsInstance(a, self.new_model.AnalysisPanel)
            self.assertIsInstance(d, self.new_model.DiseasePenetrance)

    def test_migrate_file(self):
        file_v4 = self.get_valid_object(
            object_type=self.old_model.File,
            version=self.version_4_0_0,
            fill_nullables=True,
        )
        self.assertIsInstance(file_v4, self.old_model.File)
        self.assertTrue(file_v4.validate(file_v4.toJsonDict()))
        file_v3 = MigrateReports400To300()._migrate_file(old_file=file_v4)
        self.assertIsInstance(file_v3, self.new_model.File)
        self.assertTrue(file_v3.validate(file_v3.toJsonDict()))

    def test_migrate_member_to_participant(self):
        member = self.get_valid_object(
            object_type=self.old_model.PedigreeMember,
            version=self.version_4_0_0,
            fill_nullables=True,
        )

        participant = MigrationParticipants100ToReports()._migrate_member_to_participant(
            old_member=member, family_id='some test family id'
        )
        self.assertIsInstance(participant, self.new_model.RDParticipant)
        self.assertTrue(participant.validate(participant.toJsonDict()))

        # Check individual values
        self.assertEqual(participant.pedigreeId, member.pedigreeId)
        self.assertEqual(participant.isProband, member.isProband)
        self.assertEqual(
            participant.sex,
            MigrationParticipants100ToReports()._migrate_sex(old_sex=member.sex)
        )
        for d, h in zip(participant.disorderList, participant.hpoTermList):
            self.assertIsInstance(d, self.new_model.Disorder)
            self.assertIsInstance(h, self.new_model.HpoTerm)
        self.assertEqual(
            participant.personKaryotipicSex,
            MigrationParticipants100ToReports()._migrate_person_karyotypic_sex(old_pks=member.personKaryotypicSex)
        )
        self.assertIsInstance(participant.inbreedingCoefficient, self.new_model.InbreedingCoefficient)
        self.assertIsInstance(participant.ancestries, self.new_model.Ancestries)
        self.assertIsInstance(participant.consentStatus, self.new_model.ConsentStatus)
