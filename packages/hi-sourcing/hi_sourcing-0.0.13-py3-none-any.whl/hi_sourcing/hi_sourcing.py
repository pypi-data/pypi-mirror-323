# ************************************************************************************
# ***                C O N F I D E N T I A L  --  H I - S O U R C I N G          ***
# ************************************************************************************
# *                                                                                  *
# *                Project Name : Hi-Sourcing Utilities                              *
# *                                                                                  *
# *                File Name : hi_sourcing.py                                        *
# *                                                                                  *
# *                Programmer : Jinwen Liu                                           *
# *                                                                                  *
# *                Start Date : January 9, 2025                                      *
# *                                                                                  *
# *                Last Update : January 9, 2025                                     *
# *                                                                                  *
# *                Version : 0.0.5                                                   *
# *                                                                                  *
# *-------------------------------------------------------------------------------*
# * Class Description:                                                              *
# *   HiSourcing -- Main class for performing similarity-based data sourcing       *
# *   Uses FAISS (Facebook AI Similarity Search) to find similar entries in a      *
# *   database based on a query dataset. Supports filtering by labels and custom   *
# *   column removal.                                                              *
# *                                                                                *
# * Functions:                                                                     *
# *   Public:                                                                      *
# *   - __init__ -- Initialize with query/database DataFrames and label column    *
# *   - remove_columns_from_df -- Removes specified columns from DataFrames       *
# *   - set_fillna_method -- Sets method for handling NaN values                  *
# *   - fillna -- Fills NaN values using specified method                         *
# *   - run -- Performs similarity search using FAISS after filtering by label    *
# *   - sourcing -- Returns the sourcing results as a DataFrame                   *
# *   - validate -- Compares label counts before and after sourcing              *
# *   Private:                                                                     *
# *   - _get_credentials -- Internal method for credential verification           *
# *       - Prompts user for credentials and returns the input credential        *
# *       - Used for access control in the run method                            *
# *                                                                                *
# * Parameters:                                                                    *
# *   query_df -- DataFrame containing the query data, MUST HAVE  label                                *
# *   db_df -- DataFrame containing the database to search within, MUST have label*
# *   label -- Column name for label-based filtering                              *
# *   fillna_method -- Method to handle missing values                            *
# *   k -- Number of nearest neighbors to retrieve                                *
# *   credentials -- Optional credentials for access control                       *
# *                                                                                *
# *******************************************************************************/

import pandas as pd
import numpy as np
import faiss
from getpass import getpass
import datetime


class HiSourcing:
    def __init__(self,
                 query_df: pd.DataFrame,
                 db_df: pd.DataFrame,
                 label: str = None,
                 query_remove_columns: list[str] = None,
                 db_remove_columns: list[str] = None,
                 fillna_method: str = 'zero',
                 k: int = 1000,
                 sourcing_rate: float = 0.0, 
                 credentials: str = None
    ):
        self.query_df = query_df # assume it has label
        self.db_df = db_df

        # keep a copy for validation
        self.query_df_raw = query_df.copy()
        self.db_df_raw = db_df.copy()  
        self.sourced_db_df_with_label = None,

        self.label = label

        self.query_remove_columns = query_remove_columns
        self.db_remove_columns = db_remove_columns

        self.fillna_method = fillna_method
        self.k = k
        self.sourcing_rate = sourcing_rate

        self.D = None
        self.I = None

        self.indices = []  # Initialize as empty list
        self.sourced_db_df = pd.DataFrame()  # Initialize as empty DataFrame
        self.credentials = credentials

        start = datetime.datetime.now()
        self.pre_process()
        end = datetime.datetime.now()
        print(f"Preprocessing took {end-start}")

    def pre_process(self):
        #
        print ("pre processing")
        if self.label in self.query_df.columns:
            # select real query dataframe
            self.query_df = self.query_df[self.query_df[self.label]==1]

            # drop label column
            self.query_df = self.query_df.drop(self.label, axis=1)
            if self.query_remove_columns is not None:
                remove_columns_query = [col for col in self.query_remove_columns if col in self.query_df.columns]
                self.query_df = self.query_df.drop(remove_columns_query, axis=1)

            print ("query ready")
            
        if self.label in self.db_df.columns:
            # drop label column
            self.db_df = self.db_df.drop(self.label, axis=1)
            if self.db_remove_columns is not None:
                remove_columns_db = [col for col in self.db_remove_columns if col in self.db_df.columns]
                self.db_df = self.db_df.drop(remove_columns_db, axis=1)

            print ("database ready")

        
        # fillna
        self.query_df = self.fillna(self.query_df)
        print ("query nan value filled")
        
        self.db_df = self.fillna(self.db_df)
        print ("database nan value filled")

    def set_fillna_method(self, method):
        self.fillna_method = method

    def fillna(self, df):
        try:
            if self.fillna_method == 'zero':
                return df.fillna(0)
            elif self.fillna_method == 'mean':
                mean_values = df.mean()
                if mean_values.isna().any():
                    print("Warning: Some columns have all NA values, using 0 for those columns")
                    df = df.fillna(mean_values)
                    return df.fillna(0)  # Fill remaining NAs with 0
                return df.fillna(mean_values)
            elif self.fillna_method == 'median':
                median_values = df.median()
                if median_values.isna().any():
                    print("Warning: Some columns have all NA values, using 0 for those columns")
                    df = df.fillna(median_values)
                    return df.fillna(0)
                return df.fillna(median_values)
            elif self.fillna_method == 'mode':
                mode_values = df.mode().iloc[0]
                if mode_values.isna().any():
                    print("Warning: Some columns have all NA values, using 0 for those columns")
                    df = df.fillna(mode_values)
                    return df.fillna(0)
                return df.fillna(mode_values)
            elif self.fillna_method == 'max':
                max_values = df.max()
                if max_values.isna().any():
                    print("Warning: Some columns have all NA values, using 0 for those columns")
                    df = df.fillna(max_values)
                    return df.fillna(0)
                return df.fillna(max_values)
            elif self.fillna_method == 'min':
                min_values = df.min()
                if min_values.isna().any():
                    print("Warning: Some columns have all NA values, using 0 for those columns")
                    df = df.fillna(min_values)
                    return df.fillna(0)
                return df.fillna(min_values)
            else:
                print("Invalid fillna_method. Using 'zero' method instead.")
                return df.fillna(0)
        except Exception as e:
            print(f"Error in fillna: {str(e)}. Using 'zero' method instead.")
            return df.fillna(0)
    
    def _get_credentials(self):
        """
        Internal method for credential verification.

        Prompts user for credentials and returns the input credential.
        Used for access control in the run method.
        """
        credential = getpass("Please enter your credentials: ")
        return credential

    def indexing(self):
        # credential box
        # input_credential = self._get_credentials()
        # if input_credential != 'hijinwen':
        #     print("Access denied: Invalid credentials")
        #     return False
            
        start = datetime.datetime.now()
        try:
            
            # faiss
            index = faiss.IndexFlatL2(self.query_df.shape[1])
            index.add(self.db_df)
            
            # Ensure k doesn't exceed database size
            effective_k = min(self.k, len(self.db_df))
            self.D, self.I = index.search(self.query_df, effective_k)

            self.indices = list(set([index for sublist in self.I for index in sublist]))
            
            end = datetime.datetime.now()
            print(f"Indexing took {end-start}")
            return self.indices
            
        except Exception as e:
            print(f"Error running sourcing: {str(e)}")
            return False
        

    def sourcing(self):
        """Returns the sourcing results as a DataFrame."""
        self.indexing()
        self.sourced_db_df = self.db_df.iloc[self.indices]
        self.sourced_db_df_with_label = self.db_df_raw.iloc[self.indices]
        # self.sourced_db_df = self.sourced_db_df.drop_duplicates()
        return self.sourced_db_df, self.sourced_db_df_with_label

    def validate(self):
        if self.label not in self.db_df_raw.columns:
            print("Label is needed in database for validation.")
            return

        """Validates the sourcing results by comparing label counts."""
        try:
            if self.indices is None or not self.indices:
                print("No results to validate. Run the sourcing process first.")
                return
                
            # labels in db_db
            self.raw_label_number = self.db_df_raw[self.db_df_raw[self.label]==1].shape[0]
            
            self.sourced_label_number = self.sourced_db_df_with_label[self.sourced_db_df_with_label[self.label]==1].shape[0] 

            print("Label before sourcing: " + str(self.raw_label_number))
            print("Label after sourcing: " + str(self.sourced_label_number))

            print("Number of rows before sourcing: " + str(self.db_df_raw.shape[0]))
            print("Number of rows after sourcing: " + str(self.sourced_db_df.shape[0]))

        except Exception as e:
            print(f"Error validating: {str(e)}")
