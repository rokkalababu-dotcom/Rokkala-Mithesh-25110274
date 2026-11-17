"""Explain fixed Ridge models using development-only refits; no model selection."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from train import FEATURES,TARGETS,preprocessing
ROOT=Path(__file__).resolve().parents[1]
def interpret():
    raw=pd.read_excel(ROOT/'data/ENB2012_data.xlsx')[[f'X{i}' for i in range(1,9)]+['Y1','Y2']].dropna(how='all').reset_index(drop=True)
    raw.columns=FEATURES+TARGETS
    split=pd.read_csv(ROOT/'results/split_assignments.csv')
    dev=split.loc[split.split=='development','row_id'];test=split.loc[split.split=='test','row_id']
    params=json.loads((ROOT/'results/best_parameters.json').read_text())
    saved=pd.read_csv(ROOT/'results/test_predictions.csv').set_index('row_id')
    rows=[]
    for target in TARGETS:
        model=Pipeline([('preprocess',preprocessing(True)),('model',Ridge(alpha=params[target+'/ridge']['model__alpha']))])
        model.fit(raw.loc[dev,FEATURES],raw.loc[dev,target])
        prediction=model.predict(raw.loc[test,FEATURES])
        assert np.allclose(prediction,saved.loc[test,target+'_ridge'],rtol=1e-8,atol=1e-8)
        for name,value in zip(model.named_steps['preprocess'].get_feature_names_out(),model.named_steps['model'].coef_):
            rows.append({'target':target,'feature':name.split('__')[1],'kind':'standardised numerical' if name.startswith('numeric__') else 'category indicator','coefficient':float(value)})
    pd.DataFrame(rows).to_csv(ROOT/'results/ridge_coefficients.csv',index=False)
    print('Fixed Ridge refits match saved test predictions; coefficients exported.')
if __name__=='__main__':interpret()
