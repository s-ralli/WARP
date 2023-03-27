Weight-based vAriant Ranking in Pedigrees (WARP) pipeline ranks variants by applying five weights. The five weights are based on (a) the age of diagnosis or rarity of disease subtype of the cases, (b) the total number of cases in a family, (c) genome fraction shared amongst sequenced cases in a family, (d) population allele allele-frequency and (e) variant deleteriousness. These weights are combined for each family to generate  Family Specific variant weight (FSVW). The script creates .tsv files for each family with FSVW that are then annotated to family VCF files.

Files required for generating FSVW -
1. Incidence_Information.txt with headers in the sample file as shown in the reference data folder (note: subtyp1 is the combination of disease and gender)
2. Individual_Family_Information.txt with headers in the sample file as shown in the reference data folder
3. Sharing_Information.txt with headers in the samples file as shown in the reference data folder
Note: each file in the reference folder provides a name, heading and formatting for the .txt files required for running the script

Command to run the scripts in the WARP folder -
1. source <downloaded folder path>/WARP/WARP/environment/conf/python_env.sh 
2. <downloaded folder path>/WARP/bin/config_writer.py -d "<Path to INPUT file>" -o "<Path to OUTPUT file>"
3. python <downloaded folder path>/WARP/bin/run_analysis.py -c <Path to OUTPUT file>/lc_fam_config.ini -o /<Path to OUTPUT file>

The script should provide a .tsv file with FSVW that can be used to annotate the VCF files of the families with FSVW. The annotated FSVW vcf files can be merged using bcftools, and the variants with FSVW can be extracted as a .xlxs file. The .xlxs file can be used to average FSVW for the variants and generate multi-family weight (MFW) for further analysis.