/*
 * Copyright 2017 Genomics England Ltd.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.gel.cva.models.dto;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;
import org.gel.cva.models.avro.CurationClassification;
import org.gel.cva.models.avro.KnownVariantAvro;
import org.opencb.biodata.models.variant.VariantFactory;
import org.opencb.biodata.models.variant.VariantSource;
import org.opencb.biodata.models.variant.VariantVcfFactory;
import org.opencb.biodata.models.variant.Variant;
import org.opencb.biodata.models.variant.StudyEntry;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

/**
 * @author Pablo Riesgo Ferreiro &lt;pablo.ferreiro@genomicsengland.co.uk&gt;
 */
public class KnownVariantTest {

    private VariantSource source = new VariantSource("filename.vcf", "fileId", "studyId", "studyName");
    private VariantFactory factory = new VariantVcfFactory();

    @Rule
    public ExpectedException thrown = ExpectedException.none();

    @Before
    public void setUp() throws Exception {
        List<String> sampleNames = Arrays.asList("NA001", "NA002", "NA003");
        source.setSamples(sampleNames);
    }

    @Test
    public void testCreateEmptyCuratedVariant() {
        KnownVariant knownVariant = new KnownVariant();
        assertEquals("VUS", knownVariant.getCurationClassification());
        assertEquals(new Integer(0), knownVariant.getCurationScore());
        assertNotNull(knownVariant.getCurationHistory());
        assertEquals(0, knownVariant.getCurationHistory().size());
        assertNotNull(knownVariant.getEvidences());
        assertEquals(0, knownVariant.getEvidences().size());
        assertNotNull(knownVariant.getComments());
        assertEquals(0, knownVariant.getComments().size());
        assertNotNull(knownVariant.getVariant());
        KnownVariantAvro curatedVariantAvro = knownVariant.getImpl();
        assertNotNull(curatedVariantAvro);
        assertEquals(CurationClassification.VUS, curatedVariantAvro.getClassification());
        assertEquals(new Integer(0),
                KnownVariant.curation_score_mapping.inverse().get(curatedVariantAvro.getCurationScore()));
        assertNotNull(curatedVariantAvro.getHistory());
        assertNotNull(curatedVariantAvro.getEvidences());
        assertNotNull(curatedVariantAvro.getComments());
        assertNotNull(curatedVariantAvro.getVariant());
    }

    @Test
    public void testCreateCuratedVariantFromVariantAndDefaultValues() {
        // Test when there are differences at the end of the sequence
        String line = "1\t1000\t.\tTCACCC\tTGACGG\t.\t.\t.";

        List<Variant> result = factory.create(source, line);
        result.stream().forEach(variant -> variant.setStudies(Collections.<StudyEntry>emptyList()));

        Variant variant = result.get(0);
        KnownVariant knownVariant = new KnownVariant(variant);
        assertEquals("VUS", knownVariant.getCurationClassification());
        assertEquals(new Integer(0), knownVariant.getCurationScore());
        assertNotNull(knownVariant.getCurationHistory());
        assertEquals(0, knownVariant.getCurationHistory().size());
        assertNotNull(knownVariant.getEvidences());
        assertEquals(0, knownVariant.getEvidences().size());
        assertNotNull(knownVariant.getComments());
        assertEquals(0, knownVariant.getComments().size());
        assertNotNull(knownVariant.getVariant());
        assertEquals(variant, knownVariant.getVariant());
        KnownVariantAvro curatedVariantAvro = knownVariant.getImpl();
        assertNotNull(curatedVariantAvro);
        assertEquals(CurationClassification.VUS, curatedVariantAvro.getClassification());
        assertEquals(new Integer(0),
                KnownVariant.curation_score_mapping.inverse().get(curatedVariantAvro.getCurationScore()));
        assertNotNull(curatedVariantAvro.getHistory());
        assertNotNull(curatedVariantAvro.getEvidences());
        assertNotNull(curatedVariantAvro.getComments());
        assertNotNull(curatedVariantAvro.getVariant());
    }

    @Test
    public void testCreateCuratedVariantFromVariant() {
        // Test when there are differences at the end of the sequence
        String line = "1\t1000\t.\tTCACCC\tTGACGG\t.\t.\t.";

        List<Variant> result = factory.create(source, line);
        result.stream().forEach(variant -> variant.setStudies(Collections.<StudyEntry>emptyList()));

        Variant variant = result.get(0);
        KnownVariant knownVariant = new KnownVariant(variant,
                "disease_associated_variant", 5,
                null, null, null);
        assertEquals("disease_associated_variant", knownVariant.getCurationClassification());
        assertEquals(new Integer(5), knownVariant.getCurationScore());
        assertNotNull(knownVariant.getCurationHistory());
        assertEquals(0, knownVariant.getCurationHistory().size());
        assertNotNull(knownVariant.getEvidences());
        assertEquals(0, knownVariant.getEvidences().size());
        assertNotNull(knownVariant.getComments());
        assertEquals(0, knownVariant.getComments().size());
        assertNotNull(knownVariant.getVariant());
        assertEquals(variant, knownVariant.getVariant());
        KnownVariantAvro curatedVariantAvro = knownVariant.getImpl();
        assertNotNull(curatedVariantAvro);
        assertEquals(CurationClassification.disease_associated_variant, curatedVariantAvro.getClassification());
        assertEquals(new Integer(5),
                KnownVariant.curation_score_mapping.inverse().get(curatedVariantAvro.getCurationScore()));
        assertNotNull(curatedVariantAvro.getHistory());
        assertNotNull(curatedVariantAvro.getEvidences());
        assertNotNull(curatedVariantAvro.getComments());
        assertNotNull(curatedVariantAvro.getVariant());
    }

    @Test(expected = IllegalArgumentException.class)
    public void testCreateCuratedVariantIllegalClassification() {
        // Test when there are differences at the end of the sequence
        String line = "1\t1000\t.\tTCACCC\tTGACGG\t.\t.\t.";

        List<Variant> result = factory.create(source, line);
        result.stream().forEach(variant -> variant.setStudies(Collections.<StudyEntry>emptyList()));

        Variant variant = result.get(0);
        KnownVariant knownVariant = new KnownVariant(variant,
                "MY_CUSTOM_VARIANT", 5,
                null, null, null);
    }

    @Test(expected = IllegalArgumentException.class)
    public void testCreateCuratedVariantIllegalScore() {
        // Test when there are differences at the end of the sequence
        String line = "1\t1000\t.\tTCACCC\tTGACGG\t.\t.\t.";

        List<Variant> result = factory.create(source, line);
        result.stream().forEach(variant -> variant.setStudies(Collections.<StudyEntry>emptyList()));

        Variant variant = result.get(0);
        KnownVariant knownVariant = new KnownVariant(variant,
                "VUS", 6,
                null, null, null);
    }

    @Test(expected = IllegalArgumentException.class)
    public void testCreateCuratedVariantIllegalScore2() {
        // Test when there are differences at the end of the sequence
        String line = "1\t1000\t.\tTCACCC\tTGACGG\t.\t.\t.";

        List<Variant> result = factory.create(source, line);
        result.stream().forEach(variant -> variant.setStudies(Collections.<StudyEntry>emptyList()));

        Variant variant = result.get(0);
        KnownVariant knownVariant = new KnownVariant(variant,
                "VUS", -1,
                null, null, null);
    }
}
