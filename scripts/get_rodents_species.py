import argparse 
import requests
import json

"""

This script fetch the list fo species and associated information from the iucn web site

usage:
    python get_rodents_species.py --clade_lvl <order/family...> --clade <RODENTIA/CARNIVORA...> --token <iucn token> --out <outfile>

"""

def fetch_species_list_iucn_page(clade_lvl:str, clade:str, page:int, token:str)->list:
    """
    Get species informaiton from a given page in the iucn list website

    :param clade_lvl: clade level associated (order, family etc...)
    :param clade: clade name eg : Rodentia, Carnivora etc...
    :param page: page number
    :param token: taken id for using iucn api.
    :return: list of species and their assocated information
    """

    print (f"request page {page}")
    iucn_request = f"https://apiv3.iucnredlist.org/api/v3/species/page/{page}?token={token}"
    try:
        response = requests.get(iucn_request)
    except:
        return {"detail": "Connection error"} 
    iucn_data = response.json()
    
    results = []
    count = int(iucn_data["count"])
    lst_species = iucn_data["result"]
    for species in lst_species:
        if species[f"{clade_lvl}_name"] == clade:
             results.append(species)    
    return results, count

def fetch_all_clade_species(clade_lvl:str, clade:str, token:str,)-> list:
    """
    Get species associated to a given clade fomr the iucn list website

    :param clade_lvl: clade level associated (order, family etc...)
    :param clade: clade name eg : Rodentia, Carnivora etc...
    :param token: taken id for using iucn api.
    :return: list of species and their assocated information
    """
    all_species = []
    i = 0
    while True:
        species, count = fetch_species_list_iucn_page(clade_lvl, clade, i, token)
        if count == 0:
            break
        all_species = all_species + species
        i = i + 1
    return all_species

def get_habitat_species(lst_species:list, token:str)->list:
    """
    Get the list of haboittas associated with each species

    :param lst_species: the list fo species objects 
    :param token: token provided by iucn
    :result: list of psecies objectes enriched with habita information 
    """
    results = []
    for species in lst_species:
        name = species["scientific_name"].replace(" ", "%20")
        print(name)
        habitat_request = f"https://apiv3.iucnredlist.org/api/v3/habitats/species/name/{name}?token={token}"
        try:
            response = requests.get(habitat_request)
        except:
            return {"detail": "Connection error"} 
        habitat_data = response.json()
        species["habitats"] = habitat_data["result"]
        results.append(species)
    return results

def get_country_species(lst_species:list, token:str)->list:
    """
    Get the list of countries where  each species can be found

    :param lst_species: the list fo species objects 
    :param token: token provided by iucn
    :result: list of species objects enriched with country information
    """
    results = []
    for species in lst_species:
        name = species["scientific_name"].replace(" ", "%20")
        print(name)
        country_request = f"https://apiv3.iucnredlist.org/api/v3/species/countries/name/{name}?token={token}"
        try:
            response = requests.get(country_request)
        except:
            return {"detail": "Connection error"} 
        country_data = response.json()
        species["countries"] = country_data["result"]
        results.append(species)
    return results

def main(clade_lvl:str, clade:str, token:str, outfile:str)-> None:
    """
    Main function of the script

    :param clade_lvl: the level of phylogeny we want to request
    :param clade: the name clade
    :param token: 
    :result: list of species objects enriched with country information
    
    """
    species = fetch_all_clade_species(clade_lvl, clade, token)
    with open(outfile, 'w') as f:
        json.dump(species, f)

    species_country = get_country_species(species, token)
    with open(f"{outfile}.country", 'w') as f:
        json.dump(species_country, f)

    species_habitat = get_habitat_species(species_country, token)
    with open(f"{outfile}.country.hab", 'w') as f:
        json.dump(species_habitat, f)
    
    
########################################################################################
########### Main script
########################################################################################

parser = argparse.ArgumentParser(description='Script gettting the list of species from a clade stored in the iucn web site ')
parser.add_argument('--clade_lvl',type=str, help='phylogentic rank (order, family etc..)')
parser.add_argument('--clade', type=str, help='name of the clade (rodentia, carnivora, primates...)')
parser.add_argument('--token', type=str, help='token associated to an account to the iucn web site ')
parser.add_argument('--out', type=str, help='outfile where to save the data')

args = parser.parse_args()
main(args.clade_lvl, args.clade, args.token, args.out)

