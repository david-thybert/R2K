
import typing
import argparse 
import pandas as pd

from Bio import Entrez
import requests
import xmltodict
import pprint
import json

def fetch_assemblies_ID(term:str)-> list:
    '''
    Returns the assembly Id for all assembly associated 
    with the term given in input

    :param term: term to use foer the filtering
    :return: list of gnbnk ID associated to the term
    '''
    handle = Entrez.esearch(db="assembly", term=term, RetMax=500)
    record = Entrez.read(handle)

    return record["IdList"]

def fetch_species_info(ncbi_tax_id:str)->dict:
    """
    Get species informtations from ToLID web site 
    and enriched the dictionary with these information

    :param info: information to enriche with ToLID info
    :return: enriched dictionary
    """
    tolid_request = f"https://id.tol.sanger.ac.uk/api/v2/species/{ncbi_tax_id}"
    try:
        response = requests.get(tolid_request)
    except:
        return {"detail": "Connection error"} 
    
    tolid_data = response.json()
    try:
        return tolid_data[0]
    except:
        return tolid_data

def get_assembly_info(gnbk_ids:list)-> pd.DataFrame:
    """
    Returns information associated to the assemblies through a panda object
    
    :param gnbk_ids: list of genbank ids.
    :return: dataframe with all information for each assemblies
    """
    result = pd.DataFrame(columns=["Family","Genus","SpeciesName","SpeciesTaxid","ToLPrefix",
                                   "AssemblyAccession", "AssemblyName","AssemblyStatus", "ContigN50",
                                    "ScaffoldN50", "RefSeq_category","AsmReleaseDate_GenBank"])
    
    for id in gnbk_ids:

        dic_result = {}

        ## request Entrez 
        try:
            handle = Entrez.efetch(db="assembly", id=id, rettype="docsum", retmode="xml")
        except:
            print(f"{id}: Issue with entrez request")
            continue
        record = handle.read()
        dict_data = xmltodict.parse(record)
        doc_sum = dict_data["eSummaryResult"]["DocumentSummarySet"]["DocumentSummary"]
       
        # get data of interest
        dic_result["SpeciesName"] = doc_sum["SpeciesName"]
        dic_result["SpeciesTaxid"] = doc_sum["SpeciesTaxid"]
        dic_result["AssemblyAccession"] = doc_sum["AssemblyAccession"]
        dic_result["AssemblyName"] = doc_sum["AssemblyName"]
        dic_result["AssemblyStatus"] = doc_sum["AssemblyStatus"]
        dic_result["ContigN50"] = doc_sum["ContigN50"]
        dic_result["ScaffoldN50"] = doc_sum["ScaffoldN50"]
        dic_result["RefSeq_category"] = doc_sum["RefSeq_category"]
        dic_result["AsmReleaseDate_GenBank"] = doc_sum["AsmReleaseDate_GenBank"]
        
        ## request tolID
        dic_result["Family"] = ""
        dic_result["Genus"] = ""
        dic_result["ToLPrefix"] = ""
        doc_tol = fetch_species_info(doc_sum["SpeciesTaxid"])
        if 'detail' in doc_tol:
            print(f"{id}: Issue with tolID : {doc_tol['detail']}")
            continue
        dic_result["Family"] = doc_tol["family"]
        dic_result["Genus"] = doc_tol["genus"]
        dic_result["ToLPrefix"] = doc_tol["prefix"]
        
        #append to the end of the data frame
        result.loc[len(result)] = dic_result

    return result


def main(email:str, term:str, out_file:str)-> None:
    '''
    Main function of the script

    :param email: email adress of the user
    :param term: term to use foer the filtering
    '''
    Entrez.email = email
    gbnkIDs = fetch_assemblies_ID(term)
    print(len(gbnkIDs))
    data_assemblies = get_assembly_info(gbnkIDs)
    data_assemblies.to_csv(out_file, sep='\t',index=False)

########################################################################################
########### Main script
########################################################################################

parser = argparse.ArgumentParser(description='Script formating the data to be handle by the positvie selction pipeline')
parser.add_argument('--email',type=str, help='email adress to use for entrez request. this is a required option')
parser.add_argument('--term', type=str, help='term used for requesting assembly genomes')
parser.add_argument('--out', type=str, help='outfile where to save the data')
args = parser.parse_args()

main(args.email, args.term, args.out)


