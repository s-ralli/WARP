import csv
import logging
import os

class FileWriter(object):
    def __init__(self, fid):
        self.family_id = fid

    def create_header(self):
        header = (["ExID",
                   "FamID",
                   "Chrom",
                   "Position",
                   "Ref",
                   "Alt",
                   "ID",
#                   "total_weight"
                   "Familyspecific_variant_weight",
#                   "total_indiv_weight",
                   "vcf_info"])

        self.header = header
        return header

    def create_df(self):
        if not self.header:
            raise ValueError("Empty header! Create header before creating df")
        data = OrderedDict([(k, []) for k in self.header])
        df = pd.DataFrame(data = data)
        self.df = df

    def get_df(self):
        self.df["Position"] = self.df["Position"].astype(int)
        return self.df

    def add_to_df(self, var, exid):

        record = var.misc['record']

        res = {"Exid":exid,
               "FamID":self.fid,
               "Chrom":record.CHROM,
               "Position":record.POS,
               "Ref":record.REF,
               "Alt":",".join([str(x) for x in record.ALT]),
               "ID":record.ID,
               "Familyspecific_variant_weight": var.Familyspecific_variant_weight,
               "vcf_info": ";".join(["{}={}".format(key, val) for key, val in record.INFO.items()])}

        self.df = self.df.append(res, ignore_index=True)
        
