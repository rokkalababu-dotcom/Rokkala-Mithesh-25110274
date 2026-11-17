
"""Verify saved evidence independently without fitting or tuning any model."""
from pathlib import Path
import hashlib,json
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def verify():
    s=json.loads((ROOT/'docs/data/summary.json').read_text())
    audit=json.loads((ROOT/'results/data_audit.json').read_text())
    raw=pd.read_excel(ROOT/'data/ENB2012_data.xlsx')[[f'X{i}' for i in range(1,9)]+['Y1','Y2']].dropna(how='all').reset_index(drop=True)
    assert len(raw)==768 and not raw.isna().any().any()
    assert hashlib.sha256((ROOT/'data/ENB2012_data.xlsx').read_bytes()).hexdigest()==audit['sha256']
    shapes=raw.groupby([f'X{i}' for i in range(1,6)],sort=True).ngroup()
    split=pd.read_csv(ROOT/'results/split_assignments.csv')
    assert split.row_id.is_unique and set(split.row_id)==set(range(768))
    assert np.array_equal(shapes.to_numpy(),split.sort_values('row_id').shape_id.to_numpy())
    development=split[split.split=='development'];test=split[split.split=='test']
    assert len(development)==576 and len(test)==192
    assert set(development.shape_id).isdisjoint(test.shape_id)
    folds=pd.read_csv(ROOT/'results/cv_assignments.csv')
    assert folds.row_id.is_unique and set(folds.row_id)==set(development.row_id)
    assert folds.groupby('shape_id').validation_fold.nunique().eq(1).all()
    assert set(folds.validation_fold)=={0,1,2}
    pred=pd.read_csv(ROOT/'results/test_predictions.csv')
    web=pd.DataFrame(json.loads((ROOT/'docs/data/predictions.json').read_text()))
    assert set(pred.row_id)==set(test.row_id) and pred.row_id.is_unique
    assert np.allclose(pred.select_dtypes('number'),web[pred.columns].select_dtypes('number'))
    for target,source in [('heating_load','Y1'),('cooling_load','Y2')]:
        assert np.allclose(pred[target],raw.loc[pred.row_id,source])
        assert np.allclose(pred[target+'_baseline'],raw.loc[development.row_id,source].mean())
    metrics=pd.read_csv(ROOT/'results/test_metrics.csv')
    for m in metrics.to_dict('records'):
        err=pred[m['target']+'_'+m['model']]-pred[m['target']]
        assert np.isclose(err.abs().mean(),m['mae'])
        assert np.isclose(np.sqrt((err**2).mean()),m['rmse'])
        web_m=next(x for x in s['metrics'] if x['target']==m['target'] and x['model']==m['model'])
        assert np.isclose(web_m['mae'],m['mae']) and np.isclose(web_m['rmse'],m['rmse'])
    for m in pd.read_csv(ROOT/'results/per_shape_metrics.csv').to_dict('records'):
        subset=pred[pred.shape_id==m['shape_id']]
        assert np.isclose((subset[m['target']+'_'+m['model']]-subset[m['target']]).abs().mean(),m['mae'])
    check={'status':'passed','checks':['source SHA-256 matches audit','768 complete rows and original geometry grouping verified','576 development / 192 test rows; no shape overlap','three validation folds with shape separation','prediction targets match source rows','baseline equals development target mean','all six MAE and RMSE values recomputed','per-shape MAE recomputed','website JSON matches saved predictions'], 'scope':'Artifact consistency checks, not a claim of student understanding or independent model replication.'}
    (ROOT/'results/verification.json').write_text(json.dumps(check,indent=2))
    print(json.dumps(check,indent=2))
    return check
if __name__=='__main__':verify()
