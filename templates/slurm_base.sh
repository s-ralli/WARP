#!/bin/bash -l
#SBATCH --export=ALL
#SBATCH --job-name=${job_name}
#SBATCH --mem 16000M
#SBATCH --partition=short
#SBATCH --output=${outdir}
#SBATCH -t 16:00:00

source ${home}/environment/conf/python_env.sh
time run_generic_germline_calling.py -c ${config} -o ${outdir} -r ${resources} -f ${frequency} -n ${coding_choice} -e ${repository} -s ${snpeff_impact} -m ${omim} -p ${clinvar}

if [ $$? -ne 0 ]; then touch ${outdir}/failure; exit 1; fi

### Script created by ${program} at ${datetime}
