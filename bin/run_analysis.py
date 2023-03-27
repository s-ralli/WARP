import configparser
import csv
import logging
import glob
import numpy as np
import os
import pandas as pd
import bin.settings as settings
import vcf

from modules.loader import SEERData, SharingInfo, IndividualFamilyInfo
from modules.variantAnnotation import VAnnotator
from optparse import OptionParser


def _prepare_optparser():
    """
    Prepare optparser object
    """

    program_version = settings.__version__
    usage = ("usage: %prog")
    description = """This analysis needs work """
    optparser = OptionParser(version=program_version, description=description,
                             usage=usage, add_help_option=False)

    optparser.add_option(
            "-o",
            "--output",
            dest="output",
            type="string",
            default="./",
            help="The directory where the output files will be generated")

    optparser.add_option(
            "-c",
            "--config",
            dest="config",
            type="string",
            help="custom config file",
            default=None)

    optparser.add_option(
            "-h",
            "--help",
            action="help",
            help="show this help message and exit")

    return optparser

def directory_parser(directory):
    filelist = glob.glob(os.path.abspath(directory)+"/*")
    vcflist = []
    for f in filelist:
        if f.endswith(".vcf"): 
            logging.info("Found VCF: {}".format(vcf))
            vcflist.append(f)
    logging.info("Total: {} vcfs".format(len(vcflist)))
    return vcflist


def main():
    optparser = _prepare_optparser()
    (options, dummy) = optparser.parse_args()
    output_dir = os.path.abspath(options.output)

    config = configparser.ConfigParser()
    config.read(os.path.abspath(options.config))

    vcf_directory = config.get("Directories", "vcf_directory")
    family_vcfs = directory_parser(vcf_directory)

    env_paths = os.environ.get("PATH").split(":")
    home_path = os.environ.get(settings.HOME_VAR)

    reference_data = os.environ.get(settings.RESOURCES_VAR)

    mean_indiv_weights = []

    seer_data_path = os.path.join(reference_data, "Incidence_Information.txt")
    sharing_info_path = os.path.join(reference_data, "Sharing_Information.txt")
    individual_family_info_path = os.path.join(reference_data, "Individual_Family_Information.txt")
    print(reference_data)
    print(seer_data_path)
    print(sharing_info_path)
    print(individual_family_info_path)
    seerData = SEERData(seer_data_path)
    shareData = SharingInfo(sharing_info_path)
    ifData = IndividualFamilyInfo(individual_family_info_path)
    ifData.load_individual_incidence_rates(seerData)
    ifData.calculate_average_indiv_weight()
    ifData.calculate_sharing_weight(shareData.sharing_df)
    ifData.normalize_weights()
    ifData.if_info.to_csv(os.path.join(options.output, "PedigreeWeight_Details.tsv"), index=False, sep="\t")

    variant_annotator = VAnnotator(ifData.if_info)
    
    for vcf_file in family_vcfs:
        fam_name = os.path.splitext(os.path.basename(vcf_file))[0]
        vcf_reader = vcf.Reader(filename=vcf_file)
        variant_annotator.run(vcf_reader)
        family_df = variant_annotator.concat_variant_lists()
        family_df.to_csv(os.path.join(options.output, "{}_results.tsv".format(fam_name)), index=False, sep="\t")
        family_df_by_famID= family_df[['FamID','Chrom','Position','Ref','Alt','total_indiv_weight']].groupby(['FamID','Chrom','Position','Ref','Alt']).mean()
        family_df_by_famID.rename(index=str, columns={'FamID':'FamID', 'Chrom':'Chrom', 'Position':'Position', 'Ref':'Ref', 'Alt':'Alt', 'ID':'ID', 'GENEINFO':'GENEINFO', 'SYN':'SYN', 'GnomAD':'GnomAD', 'ALFA':'ALFA', 'ExAC':'ExAC', '1000Genomes':'1000Genomes', 'CADD_PHREDscore':'CADD_PHREDscore', 'CADD_RawScore':'CADD_RawScore', 'total_indiv_weight':'mean_indiv_weight'})
        mean_indiv_weights.append(family_df_by_famID)
    
    multifamily_weights = pd.concat(mean_indiv_weights, ignore_index=True)
    multifamily_weights.to_csv(os.path.join(options.output, "multifamily_weights.tsv"), index=False, sep="\t")

#        filewriter = FileWriter()
#        for v in annotated_variants:
#            filewriter.add_to_df(v, exid)

if __name__ == "__main__":
    main()
