import pandas as pd
import datapackage
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def load_and_process():
    import pandas as pd
    import datapackage
    import seaborn as sns
    import matplotlib.pyplot as plt
    import numpy as np
    ## Getting all country codes
    WID_CC = (pd.read_csv('../data/raw/WID_countries.csv', sep = ";"))
    
    ## Getting developed countries
    AfDev = (pd.read_csv('../data/raw/AfricanDevelopment.csv')[0:27])
    
    ## Getting Country Codes of Developed Countries
    Af_CC = pd.DataFrame(columns = WID_CC.columns)
    for c in AfDev['country']:
        Af_CC = Af_CC.append(WID_CC.loc[WID_CC['titlename'] == c], ignore_index=True)
    Af_CC = (
        Af_CC.drop(Af_CC.index[Af_CC['titlename'] == 'Namibia']).reset_index(drop=True))
    
    ## Creating one dataframe for all the countries
    AllC = (pd.read_csv("../data/raw/WID_data_SC.csv", sep = ";"))
    AllList = pd.DataFrame(columns = pd.read_csv("../data/raw/WID_data_SC.csv", sep = ";").columns)
    AllList = []
    for cc in Af_CC['alpha2']:
        AllList.append(pd.read_csv(f"../data/raw/WID_data_{cc}.csv", sep = ';'))
    AllC = pd.concat(AllList)
    
    ## Getting Getting Dataset with only Key Variables
    KeyIWD = {
        'sptinc992j' : 'Share Nat. Income',
        'anninc992i' : 'Nat. Income',
        'agdpro992i': 'GDP',
        'anweal992i' : 'Nat. Wealth',
        'wwealn999i': 'Nat. Wealth to Income',
        'rptinc992j': 't10/b50 ratio', 
        'npopul999i' : 'Population'}
    AllIW = pd.DataFrame(columns = AllC.columns)
    for c in KeyIWD:
        AllIW = AllIW.append(AllC.loc[AllC["variable"] == c], ignore_index=True)
        
    ## Getting only Key Percentiles
    KeyPer = ["p90p100", "p50p90", "p0p50", "p99p100", ]
    AllPer = pd.DataFrame(columns = AllIW.columns)
    for c in KeyPer:
        AllPer = (AllPer.append([AllIW.loc[AllIW["variable"] == 'sptinc992j'].loc[AllIW["percentile"] == c]] +
                               [AllIW.loc[AllIW["variable"] != 'sptinc992j']],
                                 ignore_index=True))
    
    ## Getting 1998-2015
    AllPer['year'] = AllPer['year'].astype(int)
    All_Y = pd.DataFrame(columns = AllPer.columns)
    for c in range(1998,2016):
        All_Y = All_Y.append(AllPer.loc[AllPer['year'] == c], ignore_index=True)
        
    ## Getting Curruption Perception Index Data for selected countries
    data_url = 'https://datahub.io/core/corruption-perceptions-index/datapackage.json'
    package = datapackage.Package(data_url)
    resources = package.resources
    for resource in resources:
        if resource.tabular:
            CPIData = pd.read_csv(resource.descriptor['path'])
    CPI_CC = pd.DataFrame(columns = CPIData.columns)
    for c in Af_CC['titlename']:
        CPI_CC = CPI_CC.append(CPIData.loc[CPIData['Jurisdiction'] == c], ignore_index=True)
    CPI_CC['CC'] = Af_CC['alpha2']
    
    ## Reformatting CPI Data
    Comb = pd.DataFrame(columns = All_Y.columns)
    years = ['Jurisdiction', '1998', '1999', '2000', '2001', '2002', '2003', '2004',
            '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013',
            '2014', '2015', 'CC']
    for con in range(0,24):
        for c in range(1,19):
            temp = pd.DataFrame({
            'country' : [CPI_CC['CC'][con]],
            'variable' : ['CPI'],
            'percentile' : ['NA'],
            'year' : [int(1997+c)],
            'age' : ['NA'],
            'value' : [CPI_CC[years[c]][con]],
            'pop' : ['NA']
            })
            Comb = pd.concat([Comb, temp], ignore_index=True)
    Comb['value'] = [float(x) if x != '-' else x for x in Comb['value']]
    Comb['value'] = [x * 10 if type(x) == float and x < 10 else x for x in Comb['value']]
            
    ## Completly Cleaned Data   
    CIdata = pd.concat([All_Y, Comb], ignore_index=True)
    
    return CIdata

def scatter_plot1(CC = 'MU', CID = load_and_process()):
    import pandas as pd
    import datapackage
    import seaborn as sns
    import matplotlib.pyplot as plt
    import numpy as np
    CC_D = CID.loc[CID['country'] == CC]
    CC_D = CC_D[CC_D.value != '-']
    plt.title(f"Country : {CC}")
    plt.xlabel(f"Top 1% Share Nat. Income")
    plt.ylabel(f"CPI Index")
    plt.plot(CC_D.loc[CC_D['percentile'] == 'p99p100']['value'], CC_D.loc[CC_D['variable'] == 'CPI']['value'], 'o', color = 'green')

def sp50(CC = 'MU', CID = load_and_process()):
    import pandas as pd
    import datapackage
    import seaborn as sns
    import matplotlib.pyplot as plt
    import numpy as np
    CC_D = CID.loc[CID['country'] == CC]
    CC_D = CC_D[CC_D.value != '-']
    plt.title(f"Country : {CC}")
    plt.xlabel(f"Bottom 50% Share Nat. Income")
    plt.ylabel(f"CPI Index")
    plt.plot(CC_D.loc[CC_D['percentile'] == 'p0p50']['value'], CC_D.loc[CC_D['variable'] == 'CPI']['value'], 'o', color = 'red')

def cpi_timeseries(CC= 'UG', CID = load_and_process()):
    import pandas as pd
    import datapackage
    import seaborn as sns
    import matplotlib.pyplot as plt
    import numpy as np
    CPI = CID.loc[CID['variable'] == 'CPI']
    CPI_UG = CPI.loc[CPI['country'] == CC]
    CPI_UG = CPI_UG.loc[CPI_UG['value'] != '-']
    plt.rcParams["figure.figsize"] = [10, 4]
    CPI_time = sns.barplot(x="year", y="value", data=CPI_UG)
    CPI_time.set_xlabel("Year")
    CPI_time.set_ylabel("CPI")
    CPI_time.set_title(f"CPI index over time in {CC}")

def cpi_year(year = 2015, CID = load_and_process()):
    import pandas as pd
    import datapackage
    import seaborn as sns
    import matplotlib.pyplot as plt
    import numpy as np
    CPI = CID.loc[CID['variable'] == 'CPI']
    CC_year = CPI.loc[CPI['year'] == year]
    CC_year = CC_year.loc[CC_year['value'] != '-']
    CC_yearPlot = sns.barplot(x = 'country', y = 'value', data = CC_year, color = 'violet', orient = 'v')
    CC_yearPlot.set_title(f"CPI values in {year}")