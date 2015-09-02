from protocols.GelProtocols import InterpretationRequest
from protocols.GelProtocols import File

# bam1 = File(URIFile="/path/to/bam1", SampleId="s1")
# bam2 = File(URIFile="/path/to/bam2", SampleId="s2")
# vcf1 = File(URIFile="/path/to/vcf1", SampleId="s1")
# vcf2 = File(URIFile="/path/to/vcf2", SampleId="s2")

bam1 = File()



request = InterpretationRequest()

print request.BAMs[0].URIFile
print request.VCFs[1].URIFile