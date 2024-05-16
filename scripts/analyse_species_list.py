import typing
import argparse 
import pandas as pd


def getStatistics(data_rodents:pd.DataFrame)->dict:
    """
    """
    print(f"All rodents{data_rodents}")
    print(f"All rodent families: {len(data_rodents['Family'].unique())}")
    print(f"All rodent genera: {len(data_rodents['Genus'].unique())}") 
    print(f"All rodent species: {len(data_rodents['SpeciesName'].unique())}") 

    chr_level = data_rodents[data_rodents["AssemblyStatus"]=="Chromosome"]
    print(f"All rodents chromosome level: {len(chr_level)}")
    print(f"All rodent families chromosome level: {len(chr_level['Family'].unique())}")
    print(f"All rodent genera chromosome level: {len(chr_level['Genus'].unique())}") 
    print(f"All rodent species chromosome level: {len(chr_level['SpeciesName'].unique())}") 
   
    megbcontig = data_rodents[data_rodents["ContigN50"]>=1000000]
    print(f"All rodents 1Mbcontig level: {len(megbcontig)}")
    print(f"All rodent families 1Mbcontig level: {len(megbcontig['Family'].unique())}")
    print(f"All rodent genera 1Mbcontig level: {len(megbcontig['Genus'].unique())}") 
    print(f"All rodent species 1Mbcontig level: {len(megbcontig['SpeciesName'].unique())}") 

    megbcontg_chr = megbcontig[megbcontig["AssemblyStatus"]=="Chromosome"]
    print(f"All rodents 1Mbcontig chr level: {len(megbcontg_chr)}")
    print(f"All rodent families 1Mbcontig chrlevel: {len(megbcontg_chr['Family'].unique())}")
    print(f"All rodent genera 1Mbcontig chrlevel: {len(megbcontg_chr['Genus'].unique())}") 
    print(f"All rodent species 1Mbcontig chrlevel: {len(megbcontg_chr['SpeciesName'].unique())}") 
    return {}

def _select_best_assembly(df:pd.DataFrame)->pd.DataFrame:
    """
    """
   
    id_cont = df["ContigN50"].idxmax()
    id_scaff = df["ScaffoldN50"].idxmax()

    cont_max_cont = df._get_value(id_cont, "ContigN50")
    cont_max_scaff = df._get_value(id_scaff, "ContigN50")

    scaff_max_cont = df._get_value(id_cont, "ScaffoldN50")
    scaff_max_scaff = df._get_value(id_scaff, "ScaffoldN50")

    if id_cont == id_scaff:
        return df[df["ScaffoldN50"]==scaff_max_scaff]
    elif cont_max_cont < 1000000 and df._get_value(id_cont, "AssemblyStatus") != "Chromosome":
        if df._get_value(id_scaff, "AssemblyStatus") == "Chromosome":
            return  df[df["ScaffoldN50"]==scaff_max_scaff]
    return  df[df["ContigN50"]==cont_max_cont]




def remove_redundancy(data_species:pd.DataFrame, column:str)->pd.DataFrame:
    """
    
    """
    taxon_nr = data_species[column].unique()
    print(len(taxon_nr))
    nr_fam_df = None
    for elem in taxon_nr:
        print(elem)
        elem_data = data_species[data_species[column]==elem]
        print(elem_data)
        if len(elem_data) > 1:
            elem_data = _select_best_assembly(elem_data)
        print(elem_data)
        if nr_fam_df is None:
            nr_fam_df = elem_data
        else:
            nr_fam_df = pd.concat([nr_fam_df, elem_data])
    return nr_fam_df

def main(file_name:str, level:str, out_file:str)->None:
    """
    """
    data_species = pd.read_csv(file_name, delimiter = "\t")
    getStatistics(data_species)
    level_df = remove_redundancy(data_species, level)
    #print(level_df)
    level_df.to_csv(out_file, sep='\t',index=False)

########################################################################################
########### Main script
########################################################################################

parser = argparse.ArgumentParser(description='Script formating the data to be handle by the positvie selction pipeline')
parser.add_argument("--infile",type=str, help="rodent list csv file")
parser.add_argument("--level",type=str, help="Family or Genus")
parser.add_argument("--out",type=str, help="outfile")
args = parser.parse_args()

main(args.infile, args.level, args.out)