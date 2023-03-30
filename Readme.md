Weight-based vAriant Ranking in Pedigrees (WARP) pipeline ranks variants by applying five weights. The five weights are based on (a) the age of diagnosis or rarity of disease subtype of the cases, (b) the total number of cases in a family, (c) genome fraction shared amongst sequenced cases in a family, (d) population allele allele-frequency and (e) variant deleteriousness. These weights are combined for each family to generate  Family Specific variant weight (FSVW). The script creates .tsv files for each family with FSVW for each family.

Files for generating FSVW are stored in the reference folder. The 3 files that are required are as follows -
1. Incidence_Information.txt 
2. Individual_Family_Information.txt with headers in the sample file as shown in the reference data folder
3. Sharing_Information.txt with headers and the data spacing in the samples file as shown in the reference data folder

The reference folder provides a sample file of these 3 files. Each file contains the required header for each file except for the Sharing_Information.txt, for which spacing of data is also provided as an example. Please note that the file's name should be similar to the sample files provided.  

<u>Note:</u> Subtyp1 in the Incidence_Information.txt file is the combination of disease and gender.

Command to run the scripts in the WARP folder -
1. The requirements.txt list add-on python libraries that need to be downloaded. Create an environment of these files and then source the python environment to run steps 2 and 3.   
2. < downloaded folder path >/WARP/bin/config_writer.py -d "< Path to INPUT folder >" -o "< Path to OUTPUT folder >"
3. python < downloaded folder path >/WARP/bin/run_analysis.py -c < Path to OUTPUT folder >/lc_fam_config.ini -o < Path to OUTPUT folder >

Note: Create an input folder with the .vcf files for analysis and an output folder to store the .tsv files

The script should provide a .tsv file with FSVW that can be used to annotate the VCF files of the families with FSVW. The annotated FSVW vcf files can be merged using bcftools, and the variants with FSVW can be extracted as a .xlxs file. The .xlxs file can be used to average FSVW for the variants and generate multi-family weight (MFW) for further analysis.
