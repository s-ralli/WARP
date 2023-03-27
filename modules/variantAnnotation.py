import numpy as np
import pandas as pd

from biofx.variants.features import SNV, Indel
from copy import copy


def create_variant_from_record(r):
    variants = []

    if r.is_snp:
        for alt in r.ALT:
            v = SNV(r.CHROM, r.POS, r.POS)
            v.set_ref(str(r.REF))
            v.set_alt(str(alt))
            v.add_misc(record=r)
            variants.append(v)

    else:
        v = Indel(r.CHROM, r.POS)
        v.set_ref(str(r.REF))
        v.set_alt(str(r.ALT[0])) # ignoring multiple alt alleles for indels
        v.add_misc(record=r)
        variants.append(v)

    return variants
   

class VAnnotator(object):
    """
    """
    def __init__(self, weights):
        self.weights = weights

    def run(self, reader):
        self.vdf_list = []
        
        weight_dict = {}
        print(reader.samples)
        for indiv in reader.samples:
            weight_dict[indiv] = {}
            weight_dict[indiv]["fid"] = self.weights.loc[(self.weights["ExID"] == indiv)]["Family"].tolist()[0]
            weight_dict[indiv]["individual_weight"] = self.weights.loc[(self.weights["ExID"] == indiv)]["Normalized Individual Weight"].tolist()[0] #Instead of using individual weight, used normalized weights in the future for individual, sharing, and family weights
            weight_dict[indiv]["family_weight"] = self.weights.loc[(self.weights["ExID"] == indiv)]["Normalized Family Weight"].tolist()[0]
            weight_dict[indiv]["sharing_weight"] = self.weights.loc[(self.weights["ExID"] == indiv)]["Normalized Sharing Weight"].tolist()[0]

        for record in reader:
            print(record)
            variants = create_variant_from_record(record)


            for v in variants:
                vdict = {}
                vdf = pd.DataFrame(columns=['Exid', 'FamID', 'Chrom', 'Position', 'Ref', 'Alt', 'ID', 'total_indiv_weight', 'Familyspecific_variant_weight', 'vcf_info', 'variant_instance'])
                v.vcfinfo = ";".join(["{}={}".format(key, val) for key, val in record.INFO.items()])

                allele_freq = 0.0
                freq_tags = ['ALFA', 'GnomAD', 'ExAC', '1000Genomes']
                freq_list = [record.INFO.get(tag, 'NA') for tag in freq_tags]
                for f in freq_list:
                    if f != 'NA':
                        allele_freq = float(f)
                        break

#                print(allele_freq)
                population_af = 1- float(allele_freq)
#                print(population_af)
                v.population_weight = population_af

                CADD_weight = record.INFO.get('CADD_RawScore', 1)
                if float(CADD_weight) < 0:
                    CADD_weight = 0.000001
                elif float(CADD_weight) == 1:
                    CADD_weight = 16.168944

#                print(CADD_weight)
                prediction_weight = float(CADD_weight) / 16.168944
#                print(prediction_weight)
                v.prediction_weight = prediction_weight

                for individual in reader.samples:
                    var = copy(v)
                    var.exid = individual
                    var.fid = weight_dict[individual]["fid"]
                    var.individual_weight = weight_dict[individual]["individual_weight"]
                    var.family_weight = weight_dict[individual]["family_weight"]
                    var.sharing_weight = weight_dict[individual]["sharing_weight"]

                    total_indiv_weight = var.individual_weight * var.family_weight * var.sharing_weight * var.population_weight * var.prediction_weight
                    var.total_indiv_weight = total_indiv_weight

                    vdict = {"Exid":var.exid,
                             "FamID":var.fid,
                             "Chrom":record.CHROM,
                             "Position":record.POS,
                             "Ref":record.REF,
                             "Alt":",".join([str(x) for x in record.ALT]),
                             "ID":record.ID,
                             "total_indiv_weight":var.total_indiv_weight,
                             "Familyspecific_variant_weight":np.nan,
                             "vcf_info":var.vcfinfo,
                             "variant_instance":var}
                    vdf = vdf.append(vdict, ignore_index=True)
                vdf["Familyspecific_variant_weight"] = vdf["total_indiv_weight"].mean()
                self.vdf_list.append(vdf)

    def concat_variant_lists(self):

        return pd.concat(self.vdf_list, ignore_index=True)




