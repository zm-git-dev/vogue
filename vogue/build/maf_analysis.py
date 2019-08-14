from vogue.external_models.genotype_models import *

def build_genotypes(analysis_id):
    genotype_dict = {}
    genotypes = Genotype.query.filter(Genotype.analysis_id == analysis_id).all()
    for genotype in genotypes:
        genotype_dict[genotype.rsnumber] = [genotype.allele_1, genotype.allele_2]
    return genotype_dict

def compare(analysis_1, analysis_2):
    snps = analysis_1.keys()
    compare_dict = {}
    for snp in snps:
        if analysis_1[snp] == analysis_2[snp]:
            compare_dict[snp] = True
        else:
            compare_dict[snp] = False
    return compare_dict

def build_sample(sample):
    analysis = Analysis.query.filter(Analysis.sample_id == sample.id).all()
    mongo_sample = {
                '_id' : sample.id,
                'status' : sample.status,
                'sample_created_in_genotype_db' : sample.created_at,
                'sex' : sample.sex}
    snps = {}
    for ana in analysis:
        if ana.plate_id:
            mongo_sample['plate']= ana.plate_id
        snps[ana.type] = build_genotypes(ana.id)
        if snps.get('sequence') and snps.get('genotype'):
            snps['comp'] = compare(snps['sequence'], snps['genotype'])

    mongo_sample['snps'] = snps
    return mongo_sample