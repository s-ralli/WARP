
import collections
import csv
from fractions import Fraction
import logging
import math
import numpy as np
import os
import pandas as pd


class SEERData(object):
    """
    Attributes:
        self.seer_data (pandas.DataFrame): dataframe of the SEER data
        self.age_to_range (dict): dictionary of discrete integer ages and their corresponding age header
        self.sex_to_seersex (dict): maps M and F to the SEER data described male and female options
    """
    def __init__(self, input_path):
        """
        Args:
            input_path (string): path to the seer data tsv
        """
        logging.info("Using SeerData from: {}".format(os.path.abspath(input_path)))

        seerdf = pd.read_csv(input_path, sep="\t")
        
        a2r = {}
        for column in seerdf:
            if column.endswith('years'):
                ageRange = self.convert_age_header_to_range(column)
                for age in ageRange:
                    a2r[age] = column
            else:
                continue

        for index, row in seerdf.iterrows():
            subtype_string = " ".join(row["Subtype"].split()[1:])
            seerdf.at[index, 'Subtype'] = subtype_string

        self.seer_data = seerdf
        self.age_to_range = a2r
        self.sex_to_seersex = {"F":"female white", "M": "male white"}            

    def convert_age_header_to_range(self, string):
        """
        Convert the age headers from seer into arrays

        Args:
            string (string): the header "XX-YY years"

        Retruns:
            numpy array of each year in range XX-YY
        """
        ageRange = string.strip('years')
        if '+' in ageRange:
            lowBound = ageRange.split('+')[0]
            highBound = 125 #An arbitrarily high value
        elif '-' not in ageRange:
            lowBound = 0
            highBound = 0
        else:
            lowBound = ageRange.split('-')[0]
            highBound = ageRange.split('-')[1]
            
        return np.arange(int(lowBound), int(highBound)+1, 1)

class SharingInfo(object):
    """
    Attributes:
        self.sharing_df (pandas.DataFrame): dataframe of the sharing data
    """
    def __init__(self, input_path):
        """
        Args:
            input_path (string): path to sharing info tsv
        """

        sdf = pd.read_csv(input_path, sep="\t")
        self.sharing_df = sdf

        for index, row in sdf.iterrows():
            self.sharing_df.at[index, 'Sharing weight'] = float(Fraction(row['Sharing weight']))
            self.sharing_df.at[index, '1/sw'] = float(Fraction(row['1/sw']))

class IndividualFamilyInfo(object):
    """
    Attributes:
        self.if_info (pandas.DataFrame): dataframe of the individual-family info
    """
    def __init__(self, input_path):
        """
        Args:
            input_path (string): path to individual-family info tsv
        """
        logging.info("Using Individual-Family info from: {}".format(os.path.abspath(input_path)))

        if_df = pd.read_csv(input_path, sep="\t")

        self.if_info = if_df

    def load_individual_incidence_rates(self, seerdata):
        """
        Retrieves incidence rates of each individual and calculates individual weight for affecteds

        Args:
            seerdata (loader.SEERData): instance of SEERData class
        """

        self.if_info['Incidence rate'] = np.nan
        self.if_info['Individual weight'] = np.nan
#        print(pd.isna(self.if_info['Health Status']))
#        null_rows = self.if_info.columns[self.if_info.isnull().any()]
#        print(self.if_info[null_rows].isnull().sum())
        for individual, row in self.if_info.iterrows():
            if 'Unaffected' in row['Health Status']:
                self.if_info.at[individual, 'Incidence rate'] = np.nan
                self.if_info.at[individual, 'Individual weight'] = np.nan
            else:
                ageHeader = seerdata.age_to_range[row['Age Dx']]
#                sex = seerdata.sex_to_seersex[row['Sex']]
                subtype = row['Final Subtype']
#                column = seerdata.seer_data[['Subtype', 'Sex']]
                incidence_rate = seerdata.seer_data.loc[(seerdata.seer_data['Subtype1'] == subtype),
                                            ageHeader]
                try:
                    print(incidence_rate)
                    self.if_info.at[individual, 'Incidence rate'] = float(incidence_rate)
                    print(self.if_info.at[individual, 'Incidence rate'])
                    self.if_info.at[individual, 'Individual weight'] = 1/float(incidence_rate)
                    print(self.if_info.at[individual, 'Individual weight'])
                except ZeroDivisionError:
                    self.if_info.at[individual, 'Individual weight'] = 12

    def calculate_average_indiv_weight(self):
        """
        Averages the individual weights for all affecteds within each family

        Raises:
            AssertionError: rowcount != number_affected
        """

        self.if_info['Average Individual Weight by family'] = np.nan
        families = self.if_info["Family"].unique().tolist()
        average_individual_weights = {}

        for fam in families:
            fam_df = self.if_info.loc[(self.if_info["Family"] == fam) & 
                    (self.if_info["Incidence rate"].notna())]
#            print(fam_df)
            row_count = fam_df.shape[0]
#            print(row_count)
            fam_df.columns = fam_df.columns.str.strip() #removespace in the 'Total Lymphoid Affected' column header
            number_affected = fam_df['Total Lymphoid Affected'].unique().tolist()[0]
#            print(number_affected)
#            assert(row_count == number_affected), "Invalid flag"
            average_individual_weights[str(fam)] = fam_df["Individual weight"].mean()
#            print(average_individual_weights[str(fam)])
        for individual, row in self.if_info.iterrows():
            self.if_info.at[individual, 'Average Individual Weight by family'] = \
                    average_individual_weights[str(row['Family'])] if \
                    row.isnull()['Incidence rate'] != True else np.nan

    def calculate_sharing_weight(self, sdf):
        """
        Retrieves sharing data for each family and assigns it to corresponding individuals within family

        Args:
            sdf (pandas.DataFrame): sharing data from loader.SharingInfo class
        """

        self.if_info['Sharing weight'] = np.nan
        self.if_info['Inverse sharing'] = np.nan
#        x = (len(self.if_info))
        for individual, row in self.if_info.iterrows():
            s_weight = sdf.loc[(sdf['Family ID'] == row['Family'])]['Sharing weight'].to_list()[0]
#            print(s_weight)
            inverse_s_weight = sdf.loc[(sdf['Family ID'] == row['Family'])]['1/sw'].to_list()[0]
            self.if_info.at[individual, 'Sharing weight'] = float(s_weight)
            self.if_info.at[individual, 'Inverse sharing'] = float(inverse_s_weight)
#            print(self.if_info.at[individual, 'Sharing weight'])
#            print(self.if_info.at[individual, 'Inverse sharing'])

    def normalize_weights(self):
        """
        Normalizes weights through formula (xi - max(x))/(max(x) - min(x)) where xi is each individuals
        current weight and x represents a vector of all weights of a given type among individuals

        """
        self.if_info['Normalized Individual Weight'] = np.nan
        max_individual_weight = self.if_info['Individual weight'].max()
#        min_individual_weight = self.if_info['Individual weight'].min()

        self.if_info['Normalized Family Weight'] = np.nan
        self.if_info.columns = self.if_info.columns.str.strip()
        max_family_weight = self.if_info['Total Lymphoid Affected'].max()
#        min_family_weight = self.if_info['Total Lymphoid Affected'].min()

        self.if_info['Normalized Sharing Weight'] = np.nan
        max_sharing_weight = self.if_info['Inverse sharing'].max()
#        min_sharing_weight = self.if_info['Inverse sharing'].min()

        for individual, row in self.if_info.iterrows():\

            normalized_individual_weight = (row["Individual weight"])/(max_individual_weight) if row.isnull()["Individual weight"] != True else np.nan
            if normalized_individual_weight == 0.0:
                normalized_individual_weight = 0.001 

            normalized_family_weight = (row["Total Lymphoid Affected"])/(max_family_weight) if row.isnull()["Individual weight"] != True else np.nan
            if normalized_family_weight == 0.0:
                normalized_family_weight = 0.001

            normalized_sharing_weight = (row["Inverse sharing"])/(max_sharing_weight) if row.isnull()["Individual weight"] != True else np.nan 
            if normalized_sharing_weight == 0.0:
                normalized_sharing_weight = 0.001

            self.if_info.at[individual, 'Normalized Individual Weight'] = normalized_individual_weight
            self.if_info.at[individual, 'Normalized Family Weight'] = normalized_family_weight
            self.if_info.at[individual, 'Normalized Sharing Weight'] = normalized_sharing_weight
