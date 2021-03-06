import os
import uuid
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd
from sklearn.metrics import roc_curve, auc
sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.6) #1.4
# sns.set_palette("Set2")

#SWI
weights= {'A': 0.8356471476582918,
 'C': 0.5208088354857734,
 'E': 0.9876987431418378,
 'D': 0.9079044671339564,
 'G': 0.7997168496420723,
 'F': 0.5849790194237692,
 'I': 0.6784124413866582,
 'H': 0.8947913996466419,
 'K': 0.9267104557513497,
 'M': 0.6296623675420369,
 'L': 0.6554221515081433,
 'N': 0.8597433107431216,
 'Q': 0.789434648348208,
 'P': 0.8235328714705341,
 'S': 0.7440908318492778,
 'R': 0.7712466317693457,
 'T': 0.8096922697856334,
 'W': 0.6374678690957594,
 'V': 0.7357837119163659,
 'Y': 0.6112801822947587}


#make folder for figs and data
def make_folder(names):
    '''makes folder for results and figs.
    names = list of folder names
    '''
    for _ in names:
        try:
            os.makedirs(os.path.join(os.getcwd(),_,''))
        except FileExistsError:
            pass

make_folder(['figs', 'results'])

def progress(iteration, total, message=None):
    '''Simple progressbar
    '''
    if message is None:
        message = ''
    bars_string = int(float(iteration) / float(total) * 50.)
    print("\r|%-50s| %d%% (%s/%s) %s "% ('█'*bars_string+ "░" * \
                                     (50 - bars_string), float(iteration)/\
                                     float(total) * 100, iteration, total, \
                                     message), end='\r', flush=True)

    if iteration == total:
        print('\nCompleted!')

        
def fasta_reader(file):
    '''Converts .fasta to a pandas dataframe with accession as index
    and sequence in a column 'sequence'
    '''
    fasta_df = pd.read_csv(file, sep='>', lineterminator='>', header=None)
    fasta_df[['Accession', 'Sequence']] = fasta_df[0].str.split('\n', 1, \
                                        expand=True)
    fasta_df['Accession'] = fasta_df['Accession']
    fasta_df['Sequence'] = fasta_df['Sequence'].replace('\n', '', regex=True).\
                            astype(str).str.upper().replace('U', 'C')
    total_seq = fasta_df.shape[0]
    fasta_df.drop(0, axis=1, inplace=True)
    fasta_df = fasta_df[fasta_df.Sequence != '']
    fasta_df = fasta_df[fasta_df.Sequence != 'NONE']
    final_df = fasta_df.dropna()
    remained_seq = final_df.shape[0]
    if total_seq != remained_seq:
        print("{} sequences were removed due to inconsistencies in"
                      "provided file.".format(total_seq-remained_seq))
    return final_df



CODON_TO_AA={'TTT':'F','TCT':'S','TAT':'Y','TGT':'C','TTC':'F','TCC':'S',\
             'TAC':'Y','TGC':'C','TTA':'L','TCA':'S','TAA':'stop',\
             'TGA':'stop','TTG':'L','TCG':'S','TAG':'stop','TGG':'W',\
             'CTT':'L','CCT':'P','CAT':'H','CGT':'R','CTC':'L','CCC':'P',\
             'CAC':'H','CGC':'R','CTA':'L','CCA':'P','CAA':'Q','CGA':'R',\
             'CTG':'L','CCG':'P','CAG':'Q','CGG':'R','ATT':'I','ACT':'T',\
             'AAT':'N','AGT':'S','ATC':'I','ACC':'T','AAC':'N','AGC':'S',\
             'ATA':'I','ACA':'T','AAA':'K','AGA':'R','ATG':'M','ACG':'T',\
             'AAG':'K','AGG':'R','GTT':'V','GCT':'A','GAT':'D','GGT':'G',\
             'GTC':'V','GCC':'A','GAC':'D','GGC':'G','GTA':'V','GCA':'A',\
             'GAA':'E','GGA':'G','GTG':'V','GCG':'A','GAG':'E','GGG':'G'}



def translate(seq):
    seq = seq[:-3]
    length = (len(seq)- len(seq)%3)
    split_func = lambda seq, n: [seq[i:i+n] for\
                                    i in range(0, length, n)]
    codons = split_func(seq, 3)
    aa = ''
    for c in codons:
        aa+=CODON_TO_AA[c]
    return aa


def swi(seq, weights=weights):
    '''weights for amino acids
    '''
    seq = seq.replace('U', 'C')
    return np.mean([weights[i] for i in seq])


def solubility_score(seq, weights=weights):
    '''weights for amino acids
    '''
    seq = seq.replace('U', 'C')
    w = [weights[i] for i in seq]
    return w


def make_roc(df, labels, output=False, fname=None, c=None):
    lw = 1.75
    make_folder(['figs'])
    fig = plt.figure(figsize=(4, 4))
    for i, col in enumerate(df.columns):
        preds = df[col].values
        fpr, tpr, _ = roc_curve(labels, preds)
        roc_auc = auc(fpr, tpr)
#         if roc_auc < 0.5:
#             roc_auc = 1 - roc_auc
        if c:
            if len(c) !=0 :
                plt.plot(fpr, tpr, c=c[i],# c=np.random.rand(3,),
                         lw=lw, label=col +', AUC = %0.2f' % roc_auc)
        else:
            plt.plot(fpr, tpr, #c=np.random.rand(3,),
                     lw=lw, label=col +', AUC = %0.2f' % roc_auc)
        plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
#         plt.xlim([0.0, 1.0])
#         plt.ylim([0.0, 1.05])
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=False,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=True) # labels along the bottom edge are off


    plt.xlabel('False positive rate (1-Specificity)')
    plt.ylabel('True positive rate (Sensitivity)')

#     sns.despine()
    if output:
        if fname == None:
            fname = uuid.uuid4().hex.upper()[0:12]
        loc = 'figs/' + fname
        plt.savefig(loc, bbox_inches = 'tight', pad_inches = 0)
    plt.show()



def corr_heatmap(d, squared=False, output=False, fname=None, xlim=None, ylim=None, cmap=None):
    # Compute the correlation matrix
    corr = d.corr(method='spearman')
    df_to_plot = corr

    if squared:
        #squared correlation
        corr_sq = corr*corr
        df_to_plot = corr_sq

    # Generate a mask for the upper triangle
    mask = np.zeros_like(df_to_plot, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(8, 8))

    if cmap is None:
        # Generate a custom diverging colormap
        cmap = sns.diverging_palette(10, 220, sep=40, l=25, as_cmap=True)
        #cmap = sns.cubehelix_palette(8, start=.5, rot=-.75, as_cmap=True)
        #cmap = sns.cubehelix_palette(50, as_cmap=True)


    
    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(df_to_plot, mask=mask, cmap=cmap, vmax=.64, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5}, annot=True, fmt=".2f")
    if xlim is None:
            ax.set_xlim(0,df_to_plot.shape[1]-1)
    else:
        ax.set_xlim(xlim[0], xlim[1])
    if ylim is None:
        ax.set_ylim(df_to_plot.shape[1], 1)
    else:
        ax.set_ylim(ylim[0], ylim[1])
    
    if output:
        if fname == None:
            fname = uuid.uuid4().hex.upper()[0:12]
        loc = 'figs/' + fname
        plt.savefig(loc, bbox_inches = 'tight', pad_inches = 0)
    plt.show()


#################################
## Functions for optimisation ##
################################

# Flexibility
# Normalized flexibility parameters (B-values), average
# Vihinen M., Torkkila E., Riikonen P. Proteins. 19(2):141-9(1994).
flexibilities_vih = {"A": 0.984, "C": 0.906, "E": 1.094, "D": 1.068,
"G": 1.031, "F": 0.915, "I": 0.927, "H": 0.950,
"K": 1.102, "M": 0.952, "L": 0.935, "N": 1.048,
"Q": 1.037, "P": 1.049, "S": 1.046, "R": 1.008,
"T": 0.997, "W": 0.904, "V": 0.931, "Y": 0.929}


def make_dic(arr):
    '''Make an amino acid dictionary from an array of values
    '''
    dic = {}
    ks = [k for k, v in flexibilities_vih.items()]
    for i, v in enumerate(ks):
        dic[v] = arr[i]
    return dic

def cost_func(f, df):
    '''cost function is the AUC
    auc is returned negative because we will use a minimization algorithm 
    '''
    weights = make_dic(f)
    df['f'] = df['Protein'].apply(lambda x:solubility_score(x, weights))
    df['Average_Score'] = df['f'].apply(lambda x:np.mean(x))

    col = 'Average_Score'
    preds = df[col].values
    labels = df.Solubility.values
    fpr, tpr, _ = roc_curve(labels, preds)
    roc_auc = auc(fpr, tpr)
    if roc_auc < 0.5:
        roc_auc = 1 - roc_auc
    return -roc_auc



####SIGNAL PEPTIDES ETC######
# from ete3 import NCBITaxa
# ncbi = NCBITaxa()

def get_entry(x):
    try:
        return x.split('|')[1]
    except Exception:
        print(x)
        return np.nan

def list_to_int(x):
    try:
        return [int(i) for i in x]
    except Exception:
        print(x)
        return [int(i.split(';')[0]) for i in x]

def read_seqs(gz_file):
    df_ = pd.read_csv(gz_file, sep='>', lineterminator='>', \
                      header=None,)
    df_['Splitted'] = df_[0].str.split('\n')
    df_['All'] = df_['Splitted'].apply(lambda x:x[0])
    df_['Entry'] = df_['All'].apply(get_entry)
    df_['Protein'] = df_['Splitted'].apply(lambda x:''.join(x[1:]).replace('U', 'C'))
    df_['Check'] = df_['Protein'].apply(lambda x: ('X' in x[:60]) or ('Z' in x[:60]))
    df__ = df_.loc[df_['Check'] == False]
    if df_.shape[0] != df__.shape[0]:
        print("{removed} sequences were removed because they had unknown residues.".\
              format(removed=df_.shape[0] - df__.shape[0]))
    df = df__[['Entry', 'All', 'Protein']].copy()
    df.dropna(inplace=True)
    return df

# def get_all(taxid):
#     lineage = ncbi.get_lineage(taxid)
#     names = ncbi.get_taxid_translator(lineage)
#     return [names[t] for t in lineage]