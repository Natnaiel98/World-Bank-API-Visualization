# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 10:32:08 2023

@author: natem
"""

##This is a function that takes a world bank indicator name and explores it's relationship with GDP per capita Growth Rate
##for a selected Year. The function utilizes the wbgapi library to pull data from the World Bank's API and 


def WorldBankGDPVisual(SeriesID,Year,COUNTRIES_TO_HIGHLIGHT):
    
    import wbgapi as wb
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sn
    import numpy as np
    import matplotlib.pyplot as plt
    
    from adjustText import adjust_text
    from matplotlib.lines import Line2D # for the legend
    from sklearn.linear_model import LinearRegression
    from sklearn.linear_model import HuberRegressor
    
    
    #Inflations,Savings,Foreign Direct Investment, GDP per capita annual growth %, 'NE.GDI.TOTL.ZS': Gross capital formation (% of GDP), 'NE.IMP.GNFS.ZS':  Imports of goods and services (% of GDP), 'NE.EXP.GNFS.ZS':Exports of goods and services (% of GDP)
    CompleteSeriesIDs=['FP.CPI.TOTL.ZG','NY.GDP.PCAP.KD.ZG','BX.KLT.DINV.WD.GD.ZS', 'NE.GDI.TOTL.ZS', 'NE.IMP.GNFS.ZS', 'NE.EXP.GNFS.ZS', 'BM.KLT.DINV.WD.GD.ZS', 'HD.HCI.OVRL']#complete IDs for Mastertable
    Year=2019
    #Nested function that takes a member name (region name), SeriesIDs, and Year and pulls data from API and Wrangles this data into an appropriate dataframe format
    def Wrangleddf(member_name, CompleteSeriesIDs, Year):
       wbdataframe=wb.data.DataFrame(CompleteSeriesIDs,wb.region.members(member_name), time=range(Year-2,Year+2), skipBlanks=True,labels=True).reset_index()
       #Next steps to perform regression, flatten the year mmns so  they are one column and widen the Series column so that they are all individual rows
       #Using the pd.Melt() function to flatten multiple year columns into one
       year_list=list(wbdataframe.columns)[4:]
       Indlist=list(wbdataframe.columns)[2:4]

       wbdataframe_long = pd.melt(wbdataframe,id_vars= Indlist , value_vars=year_list,value_name='Series Value')
       ser=list(wbdataframe_long.columns)[1]

       #reformat the columns so that the series column is widened to be separated by multiple variables
       #Indlist2=['Country','variable']
       Indlistlong=['Country','variable']

       wbdataframe_wide=wbdataframe_long.pivot_table(index=Indlistlong, columns =ser ,values = 'Series Value').reset_index() #Reshape from long to wide
       wbdataframe_wide['variable'] = wbdataframe_wide['variable'].map(lambda x:x[2:])
        
       # wbdataframe_long.tolist.columns()
       #converting the name of the variable into year column
       wbdataframe_fin=wbdataframe_wide.rename(columns={"variable":"Year"})
       #add a region column to the dataframe 
       wbdataframe_fin['region']=member_name
        
       return wbdataframe_fin




            

    #returning economic data for multiple regions using the previous function
    SSAdataframe=Wrangleddf('SSA',CompleteSeriesIDs,Year)
    CLAdataframe= Wrangleddf('LCN',CompleteSeriesIDs,Year)
    CMEdataframe= Wrangleddf('MEA',CompleteSeriesIDs,Year)
    EUUdataframe= Wrangleddf('EUU',CompleteSeriesIDs,Year)
    NACdataframe= Wrangleddf('NAC',CompleteSeriesIDs,Year)
    EASdataframe= Wrangleddf('EAS',CompleteSeriesIDs,Year)
    #return the combined dataframe
    masterworldbankdataframe=pd.concat([SSAdataframe, CLAdataframe,CMEdataframe, EUUdataframe, NACdataframe,EASdataframe], ignore_index=True, axis=0)
    
    #return masterworldbankdataframe

    #list(functiontest.columns)
    #list(wbdataframe_long.columns)[1]
    ####PRODUCING THE VISUALIZATION
    # Subset of the data for year 2019, with all null values removed
    wbyear = masterworldbankdataframe[masterworldbankdataframe['Year'] == str(Year)]
    # IQR


    #Converting the provided series name into the indicaor/column name
    ConversionDict={'NY.GDP.PCAP.KD.ZG':'GDP per capita growth (annual %)','BX.KLT.DINV.WD.GD.ZS':'Foreign direct investment, net inflows (% of GDP)','NY.GNS.ICTR.ZS':'Savings as % of GDP', 'FP.CPI.TOTL.ZG':'Inflation, consumer prices (annual %)','NE.GDI.TOTL.ZS': 'Gross capital formation (% of GDP)', 'NE.IMP.GNFS.ZS':  'Imports of goods and services (% of GDP)', 'NE.EXP.GNFS.ZS':'Exports of goods and services (% of GDP)', 'BM.KLT.DINV.WD.GD.ZS':'Foreign direct investment, net outflows (% of GDP)', 'HD.HCI.OVRL':'Human capital index (HCI) (scale 0-1)', 'SP.POP.SCIE.RD.P6':'Researchers in R&D (per million people)','BX.GSR.CCIS.ZS':'ICT service exports (% of service exports, BoP)', 'TX.VAL.AGRI.ZS.UN':'Agricultural raw materials exports (% of merchandise exports)'}
    Indicator= ConversionDict[SeriesID]
    # Calculate the upper and lower limits of the X varaible
    Q1 = wbyear[Indicator].quantile(0.25)
    Q3 = wbyear[Indicator].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5*IQR
    upper = Q3 + 1.5*IQR
    
    # Create arrays of Boolean values indicating the outlier rows
    wbyear=wbyear.reset_index(drop=True)
    upper_array = np.where(wbyear[Indicator]>=upper)[0]
    lower_array = np.where(wbyear[Indicator]<=lower)[0]

     
    # Removing the outliers
    wbyear.drop(index=upper_array, inplace=True)
    wbyear.drop(index=lower_array, inplace=True)
    
    # Calculate the upper and lower limits of the Y varaible
    Q1Y = wbyear['GDP per capita growth (annual %)'].quantile(0.25)
    Q3Y = wbyear['GDP per capita growth (annual %)'].quantile(0.75)
    IQRY = Q3Y - Q1Y
    lowerY = Q1Y - 1.5*IQRY
    upperY = Q3Y + 1.5*IQRY
     
    # Create arrays of Boolean values indicating the outlier rows
    wbyear=wbyear.reset_index(drop=True)
    upper_arrayy = np.where(wbyear['GDP per capita growth (annual %)']>=upperY)[0]
    lower_arrayy = np.where(wbyear['GDP per capita growth (annual %)']<=lowerY)[0]
    
     # Removing the outliers
    wbyear.drop(index=upper_arrayy, inplace=True)
    wbyear.drop(index=lower_arrayy, inplace=True)
    
    
    #dropping Null Values and reseting Index, subset to make sure that we are only dropping NAs for the specifically analyzed variables
    wbyearfin=wbyear[[Indicator,'GDP per capita growth (annual %)', 'Country', 'region']].dropna()
    wbyearfin=wbyearfin.reset_index()
    IND=wbyearfin[Indicator]
    GDP=wbyearfin['GDP per capita growth (annual %)']
    #fig, ax = plt.subplots(figsize=(12, 8));
    #ax.scatter(IND,GDP, vmax=50)
    #plt.xlim(-20, 20);
    #function for adjusting the lightness of the color
    
    def adjust_lightness(color, amount=0.5):
        import matplotlib.colors as mc
        import colorsys
        try:
            c = mc.cnames[color]
        except:
            c = color
        c = colorsys.rgb_to_hls(*mc.to_rgb(c))
        return colorsys.hls_to_rgb(c[0], c[1] * amount, c[2])
    
    # Okabe Ito colors
    REGION_COLS = ["#E69F00", "#CC79A7", "#009E73", "#F0E442", "#0072B2", "#D55E00"]
    
    # Category values for the colors
    CATEGORY_CODES = pd.Categorical(wbyearfin["region"]).codes
    
    # Select colors for each region according to its category.
    COLORS = np.array(REGION_COLS)[CATEGORY_CODES]
    
    # Compute colors for the edges: simply darker versions of the original colors
    EDGECOLORS = [adjust_lightness(color, 0.6) for color in COLORS] 
    
    
    
 
    
    #producing the limits for the X Axis, 
    
    xmin=wbyearfin[Indicator].min()
    xmax=wbyearfin[Indicator].max()
    #Plotting with colors included
    fig, ax = plt.subplots(figsize=(12, 8));
    ax.scatter(
        IND, GDP, color=COLORS,
        s=80, alpha=0.25, zorder=10
    )
    plt.xlim(xmin-1, xmax+1);
        
        # Some notes: 
    # * scikit-learn asks 2-dimensional arrays for X, that's why the reshape
    # * The response, y, does not need to be 2-dimensional
    X = IND.values.reshape(-1, 1)
    y = GDP
    
    np.any(np.isnan(X))
    np.all(np.isfinite(X))
    
    
    
    # Initialize linear regression object, attempting to use Huber Regressor as it is more robust against outliers
    HuberRegressor = HuberRegressor()
    
    # Fit linear regression model of HDI on the log of CPI( got rid of the log for now, may reintroduce it if I deem it necessary)
    HuberRegressor.fit((X), y)
    
    # Make predictions
    # * Construct a sequence of values ranging from 10 to 95 and
    #   apply logarithmic transform to them.
    x_pred = np.log(np.linspace(10, 95, num=200).reshape(-1, 1))
    
    # * Use .predict() method with the created sequence
    y_pred = HuberRegressor.predict(X)  
    ax.plot((X), y_pred, color="#696969", lw=2)
    Indicator_name= ConversionDict[SeriesID]
    ax.set_xlabel(Indicator_name, fontweight ='bold')
    ax.set_ylabel('GDP per capita growth (annual %)', fontweight ='bold')
    ax.set_title('GDP Per Capita Vs '+ Indicator_name +' '+ str(Year), 
             fontsize = 14)
    fig
    
    # Make predictions
    # * Construct a sequence of values ranging from 10 to 95 and
    #   apply logarithmic transform to them.
    # Adding labels
    
    # Names of the main regions of the world
    REGIONS = [
        "Sub-Saharan\nAfrica","Latin and Central America", "Middle East", "EU Nations",
        "North America", "Asia Pacific", 
    ]
    
    # Create handles for the lines.
    handles = [
        Line2D(
            [], [], label=label, 
            lw=0, # there's no line added, just the marker
            marker="o", # circle marker
            markersize=10, 
            markerfacecolor=REGION_COLS[idx], # marker fill color
        )
        for idx, label in enumerate(REGIONS)
    ]
    
    # Append a handle for the line
    handles += [Line2D([], [], label="y ~ x", color="#696969", lw=2)]
    
    # Add legend -----------------------------------------------------
    legend = fig.legend(
        handles=handles,
        bbox_to_anchor=[0.5, 0.95], # Located in the top-mid of the figure.
        fontsize=12,
        handletextpad=0.6, # Space between text and marker/line
        handlelength=1.4, 
        columnspacing=1.4,
        loc="center", 
        ncol=6,
        frameon=False
    )
    
    # Set transparency 
    # Iterate through first five handles and set transparency
    for i in range(5): 
        handle = legend.legendHandles[i]
        handle.set_alpha(0.25)
    fig

    
    
    
    
    #Next step would be to highlight some of the nations in the graph
    # All the countries, in the order they appear in the dataset 
    COUNTRIES = wbyearfin["Country"].values
    

    # Iterate through all the countries in COUNTRIES
    # `ax.text()` outputs are appended to the `TEXTS` list. 
    # This list is passed to `adjust_text()` to adjust the position of
    # the legends and add connecting lines
    TEXTS = []
    for idx, country in enumerate(COUNTRIES):
        # Only append selected countries
        if country in COUNTRIES_TO_HIGHLIGHT:
            x, y = IND[idx], GDP[idx]
            TEXTS.append(ax.text(x, y, country, fontsize=12));
    
    # Adjust text position
    # 'expand_points' is a tuple with two multipliers by which to expand
    # the bounding box of texts when repelling them from points

    adjust_text(
        TEXTS, 
        expand_points=(3, 3),
        arrowprops=dict(arrowstyle="-", lw=1),
        ax=ax
     );
    return fig

