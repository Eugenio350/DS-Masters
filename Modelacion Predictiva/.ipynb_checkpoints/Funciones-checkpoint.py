import pandas as pd
import numpy as np
import statsmodels.api as sm
import patsy
import warnings
from scipy.stats.contingency import association
from scipy.stats import contingency
import missingno as msno
import sklearn.impute as skl_imp
from sklearn.experimental import enable_iterative_imputer
import feature_engine.imputation as fe_imp
from sklearn.model_selection import train_test_split
from statsmodels.formula.api import ols
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold
from sklearn.linear_model import LinearRegression
import seaborn as sns
import scipy.stats as stats
from sklearn.preprocessing import scale
from statsmodels.graphics.factorplots import interaction_plot
import plotly.express as px

def cross_val_lin(formula:str, data:pd.DataFrame, seed=1):
    y, x = patsy.dmatrices(formula, data, return_type='dataframe')
    model = LinearRegression()
    # Establecemos esquema de validación fijando random_state 
    cv = RepeatedKFold(n_splits=5, n_repeats=20, random_state=seed)
    # Obtenemos los resultados de r2 para cada partici[on training-test
    scores = cross_val_score(model, x, y, cv=cv)
    
    # Sesgo y varianz
    print('Modelo:' + str(formula)) 
    print("Coeficiente de determinacion R2: %.3f (%.3f)" % (np.mean(scores), np.std(scores)))
    return scores

def ols_formula(df, dependent_var, *excluded_cols):
    df_columns = list(df.columns.values)
    df_columns.remove(dependent_var)
    for col in excluded_cols:
        df_columns.remove(col)
    return dependent_var + ' ~ ' + ' + '.join(df_columns)

def cat_plot(col):
    if col.dtypes == "category":
        fig = px.bar(col.value_counts())
        return fig
    
def plot(col):
    if col.dtypes != "category":
        histogram_boxplot(col, xlabel=col.name, title="Distribucion Continua")
    else:
        cat_plot(col)
    
def histogram_boxplot(data, xlabel= None, title = None, font_scale=2, figsize=(9,8), bins=None):
    sns.set(font_scale=font_scale)
    f2, (ax_box2, ax_hist2) = plt.subplots(2, sharex=True, gridspec_kw={"height_ratios": (.15, .85)}, 
                                           figsize=figsize)
    sns.boxplot(x=data, ax=ax_box2)

    sns.histplot(x=data, ax=ax_hist2, bins=bins) if bins else sns.histplot(x=data, ax=ax_hist2)

    ax_hist2.axvline(np.mean(data), color='g', linestyle='-')

    ax_hist2.axvline(np.median(data), color='y', linestyle='--')

    if xlabel: ax_hist2.set(xlabel=xlabel)
    if title: ax_box2.set(title=title, xlabel="")

    plt.show()
    
# Función para calcular VCramer (dos nominales de entrada!)
def cramers_v(var1, varObj):
    
    if not var1.dtypes == 'category':
        #bins = min(5,var1.value_counts().count())
        var1 = pd.cut(var1, bins = 5)
    if not varObj.dtypes == 'category': #np.issubdtype(varObj, np.number):
        #bins = min(5,varObj.value_counts().count())
        varObj = pd.cut(varObj, bins = 5)
        
    data = pd.crosstab(var1, varObj).values
    vCramer = stats.contingency.association(data, method = 'cramer')
    return vCramer
    
def mean_absolute_deviation(series):
    return (series - series.mean()).abs().mean()

## Función manual de winsor con clip+quantile 
def winsorize_with_pandas(s, limits):
    """
    s : pd.Series
        Series to winsorize
    limits : tuple of float
        Tuple of the percentages to cut on each side of the array, 
        with respect to the number of unmasked data, as floats between 0. and 1
    """
    return s.clip(lower=s.quantile(limits[0], interpolation='lower'), 
                  upper=s.quantile(1-limits[1], interpolation='higher'))
## Función para gestionar outliers
def gestiona_outliers(col,clas = 'check'):

    print(col.name)
    # Condición de asimetría y aplicación de criterio 1 según el caso
    if abs(col.skew()) < 1:
        criterio1 = abs((col-col.mean())/col.std())>3
    else:
        criterio1 = abs((col-col.median())/ mean_absolute_deviation(col)) > 8

    # Calcular primer cuartil     
    q1 = col.quantile(0.25)  
    # Calcular tercer cuartil  
    q3 = col.quantile(0.75)
    # Calculo de IQR
    IQR=q3-q1
    # Calcular criterio 2 (general para cualquier asimetría)
    criterio2 = (col<(q1 - 3*IQR))|(col>(q3 + 3*IQR))
    lower = col[criterio1&criterio2&(col<q1)].count()/col.dropna().count()
    upper = col[criterio1&criterio2&(col>q3)].count()/col.dropna().count()
    # Salida según el tipo deseado
    if clas == 'check':
        return(lower*100,upper*100,(lower+upper)*100)
    elif clas == 'winsor':
        return(winsorize_with_pandas(col,(lower,upper)))
    elif clas == 'miss':
        print('\n MissingAntes: ' + str(col.isna().sum()))
        col.loc[criterio1&criterio2] = np.nan
        print('MissingDespues: ' + str(col.isna().sum()) +'\n')
    return(col)

def mejorTransf (vv,target, name=False, tipo = 'cramer', graf=False):
    
    # Escalado de datos (evitar fallos de tamaño de float64 al hacer exp de número grande..cosas de python)
    vv = pd.Series(scale(vv), name=vv.name)
    # Traslación a valores positivos de la variable (sino falla log y las raíces!)
    vv = vv + abs(min(vv))+0.0001
      
    # Definimos y calculamos las transformaciones típicas  
    transf = pd.DataFrame({vv.name + '_ident': vv, vv.name + '_log': np.log(vv), vv.name + '_exp': np.exp(vv), vv.name + '_sqrt': np.sqrt(vv), 
                         vv.name + '_sqr': np.square(vv), vv.name + '_cuarta': vv**4, vv.name + '_raiz4': vv**(1/4)})
      
    # Distinguimos caso cramer o caso correlación
    if tipo == 'cramer':
      # Aplicar la función cramers_v a cada transformación frente a la respuesta
        tablaCramer = pd.DataFrame(transf.apply(lambda x: cramers_v(x,target)),columns=['VCramer'])
      
      # Si queremos gráfico, muestra comparativa entre las posibilidades
        if graf: px.bar(tablaCramer,x=tablaCramer.VCramer,title='Relaciones frente a ' + target.name).update_yaxes(categoryorder="total ascending").show()
      # Identificar mejor transformación
        best = tablaCramer.query('VCramer == VCramer.max()').index
        ser = transf[best[0]].squeeze()
    
    if tipo == 'cor':
      # Aplicar coeficiente de correlación a cada transformación frente a la respuesta
        tablaCorr = pd.DataFrame(transf.apply(lambda x: np.corrcoef(x,target)[0,1]),columns=['Corr'])
      # Si queremos gráfico, muestra comparativa entre las posibilidades
        if graf: px.bar(tablaCorr,x=tablaCorr.Corr,title='Relaciones frente a ' + target.name).update_yaxes(categoryorder="total ascending").show()
      # identificar mejor transformación
        best = tablaCorr.query('Corr.abs() == Corr.abs().max()').index
        ser = transf[best[0]].squeeze()
  
    # Aquí distingue si se devuelve la variable transformada o solamente el nombre de la transformación
    if name:
        return(ser.name)
    else:
        return(ser)
