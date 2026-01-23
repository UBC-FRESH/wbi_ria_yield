# Auto-generated from 01b_run-tsa.ipynb

def run_tsa():
    
    # --- cell 1 ---
    #!mv ./data/04_output.out ./data/tipsy_output_tsa08.out
    #!mv ./data/04_output.out ./data/tipsy_output_tsa16.out
    #!mv ./data/04_output.out ./data/tipsy_output_tsa24.out
    #!mv ./data/04_output.out ./data/tipsy_output_tsa40.out
    #!mv ./data/04_output.out ./data/tipsy_output_tsa41.out
    
    # --- cell 2 ---
    ##################################################################################
    # Code below is adapted from a script developed by Cosmin Man (cman@forsite.ca).
    ##################################################################################
    
    import pandas as pd
    import numpy as np
    import time
    Start = time.time()
    
    #change line below
    loc = r'.'
    
    #############no need to change the code below
    tipsy_excel = './data/tipsy_params_tsa%s.xlsx' % tsa
    tipsyout = './data/04_output-tsa%s.out' % tsa
    outYield = './data/tipsy_curves_tsa%s.csv' % tsa
    outSPP = './data/tipsy_sppcomp_tsa%s.csv' % tsa
    
    
    def conditions(s):
        if s in ['AT']:
            return 'DEC'
        elif s in ['BA', 'BG', 'BL']:
            return 'BL'
        elif s in ['CW']:
            return 'CW'
        elif s in ['FD']:
            return 'FD'
        elif s in ['HW', 'HM']:
            return 'HW'
        elif s in ['PL']:
            return 'PL'
        elif s in ['SX', 'SE']:
            return 'SX'
        else:
            return 'NONE'
    
    
    def conditions(s):
        return s
    
    
    spp = np.vectorize(conditions)
    df = pd.read_excel(tipsy_excel, sheet_name='TIPSY_inputTBL', usecols='A:AF')
    df=df.query('SI > 0').copy()
    
    # reformat data
    for i in range(1,6):
        df[['PCT_'+str(i)]] = df[['PCT_'+str(i)]].fillna(0)
        if df['PCT_'+str(i)].dtype==object:  
            df['PCT_'+str(i)] = pd.to_numeric(df['PCT_'+str(i)]).astype(int)
        else:
            df['PCT_'+str(i)] = df['PCT_'+str(i)].astype(int)
    
    # consolidate species
    for i in range (1,4):
        ds = df.groupby(['AU', 'Proportion','SPP_'+str(i)], as_index=False)[['PCT_'+str(i)]].mean()
        ds['SPP'] = ds['SPP_'+str(i)]
        ds['PCT'] = ds['Proportion']*ds['PCT_'+str(i)]
        ds = ds.query("PCT>0")
        ds = ds.groupby(['AU', 'SPP'], as_index=False)[['PCT']].sum()
        if i ==1:
            dspp = ds
        else:
            dspp = pd.concat([dspp, ds], ignore_index=True)
    dspp = dspp.groupby(['AU', 'SPP'])[['PCT']].sum()
    
    #unstack and remove extra columns
    dspp = dspp.unstack()
    dspp.columns = dspp.columns.droplevel(0)
    dspp.reset_index(inplace=True)
    dspp.to_csv (outSPP, header=True, index=False)
    
    # consolidate yields
    cols = ['TABLE_NO', 'Empty' ,'Age', 'Yield', 'Vol_gross', 'DBHq', 'Height', 'TPH', 'Crown_C', 'Crown_L', 'CWD_TPH']
    dy = pd.read_csv(tipsyout, low_memory=False, header=None, skiprows = 4, delim_whitespace=True)
    dy.columns = cols
    dy.drop('Empty', axis=1, inplace=True)
    dy.set_index('TABLE_NO', inplace=True)
    dp = df.groupby(['AU', 'TBLno'],as_index=False)[['Proportion']].sum()
    dp.set_index('TBLno',inplace=True)
    dy = dy.join(dp)
    dy.reset_index(inplace=True)
    dyf = dy.groupby(['AU', 'Age'], as_index=False).agg({'Yield':['sum'], 'Height':['max'], 'DBHq':['max'], 'TPH':['sum']})
    dyf.columns = dyf.columns.droplevel(1) #drop the sum/max labels
    
    # export result to a CSV file
    dyf.to_csv(outYield, header=True, index=False)
    
    # --- cell 4 ---
    df = pd.read_csv('./data/tipsy_curves_tsa%s.csv' % tsa)
    df['AU'] = df['AU'].astype('int')
    df.set_index(['AU', 'Age'], inplace=True)
    tipsy_curves[tsa] = df
    
    palette = sns.color_palette('Greens', 3)#, len(df.index.unique(level=0)))
    sns.set_palette(palette)
    
    for i, au in enumerate(df.index.unique(level=0)):
        print(i, au)
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        au_ = int(str(au)[-4:])
        stratumi = int(str(au)[-2:])
        _, _, result = results[tsa][stratumi]
        sc, si_level = au_scsi[tsa][au_]
        ss = result[si_level]['ss']
        print(au, sc, si_level)
        #(df.loc[au].Yield * ss.CROWN_CLOSURE.median() * 0.01).plot(ax=ax, label='TIPSY (scaled by CC)', linestyle='--')
        (df.loc[au].Yield * 1.00).plot(ax=ax, label='TIPSY (raw)', linestyle='--')
        df2 = vdyp_curves_smooth[tsa].set_index(['stratum_code', 'si_level'])
        df2.loc[sc, si_level].set_index('age').volume.plot(label='VDYP')
        #plt.plot(df.loc[au].Age, df.loc[au].Yield, linestyle='-', alpha=0.5, label=au, linewidth=2)s
        plt.xlabel('Age')
        plt.ylabel('Yield (m3/ha)')
        plt.title('%s %s (AU %i)' % (sc, si_level, au))
        plt.legend()
        plt.xlim([0, 300])
        plt.ylim([0, 600])
        plt.savefig('./plots/tipsy_vdyp_tsa%s-%s.png' % (tsa, au), facecolor='white')

if __name__ == '__main__':
    run_tsa()
