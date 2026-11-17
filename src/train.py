"""Run from any directory: python src/train.py. No notebook state required."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import platform
import urllib.request
import zipfile
import importlib.metadata
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupShuffleSplit, GroupKFold, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[1]
SEED = 42
FEATURES = ["relative_compactness", "surface_area", "wall_area", "roof_area", "overall_height", "orientation", "glazing_area", "glazing_distribution"]
TARGETS = ["heating_load", "cooling_load"]
NUMERIC = FEATURES[:5] + ["glazing_area"]
CATEGORICAL = ["orientation", "glazing_distribution"]
URL = "https://archive.ics.uci.edu/static/public/242/energy+efficiency.zip"

def preprocessing(scale):
    return ColumnTransformer([
        ("numeric", StandardScaler() if scale else "passthrough", NUMERIC),
        ("category", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL)
    ])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, help="Optional path to downloaded ENB2012_data.xlsx")
    args = parser.parse_args()
    results = ROOT / "results"
    web = ROOT / "docs" / "data"
    figures = ROOT / "docs" / "figures"
    for directory in [results, web, figures, ROOT / "data"]:
        directory.mkdir(parents=True, exist_ok=True)
    path = args.data or ROOT / "data" / "ENB2012_data.xlsx"
    if not path.exists():
        if args.data:
            raise FileNotFoundError(path)
        print("Downloading public UCI data...", flush=True)
        request = urllib.request.Request(URL, headers={"User-Agent": "BuildingEnergyExplorer/1.0"})
        with urllib.request.urlopen(request, timeout=60) as response:
            archive = zipfile.ZipFile(io.BytesIO(response.read()))
        member = next(n for n in archive.namelist() if n.endswith("ENB2012_data.xlsx"))
        path.write_bytes(archive.read(member))
    raw = pd.read_excel(path)
    required = [f"X{i}" for i in range(1, 9)] + ["Y1", "Y2"]
    if not set(required).issubset(raw.columns):
        raise ValueError(f"Expected columns {required}, found {list(raw.columns)}")
    df = raw[required].copy()
    empty_rows = int(df.isna().all(axis=1).sum())
    df = df.dropna(how="all").reset_index(drop=True)
    df.columns = FEATURES + TARGETS
    if len(df) != 768 or df.isna().any().any():
        raise ValueError("Unexpected row count or missing values; inspect data before modelling")
    if not all(pd.api.types.is_numeric_dtype(df[c]) for c in df):
        raise ValueError("Unexpected nonnumeric source values")
    df.insert(0, "row_id", np.arange(len(df)))
    df["shape_id"] = df.groupby(FEATURES[:5], sort=True).ngroup()
    if df.shape_id.nunique() != 12:
        raise ValueError("Geometry does not identify the expected 12 shapes")
    groups = df.shape_id
    dev, test = next(GroupShuffleSplit(n_splits=1, test_size=3, random_state=SEED).split(df, groups=groups))
    assert set(groups.iloc[dev]).isdisjoint(groups.iloc[test])
    assignments = df[["row_id", "shape_id"]].copy()
    assignments["split"] = "development"
    assignments.loc[test, "split"] = "test"
    assignments.to_csv(results / "split_assignments.csv", index=False)
    df[["shape_id"] + FEATURES[:5]].drop_duplicates().to_csv(results / "shape_definitions.csv", index=False)
    audit = {"rows":len(df), "features":len(FEATURES), "empty_spreadsheet_rows_removed":empty_rows,
             "missing":df[FEATURES+TARGETS].isna().sum().to_dict(),
             "duplicate_source_rows":int(df[FEATURES+TARGETS].duplicated().sum()),
             "shape_counts":df.groupby("shape_id").size().to_dict(),
             "categories":{c:sorted(df[c].unique().tolist()) for c in CATEGORICAL},
             "sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
    (results / "data_audit.json").write_text(json.dumps(audit, indent=2))
    # Only development rows inform exploratory plots and modelling decisions.
    development = df.iloc[dev]
    development[FEATURES+TARGETS].describe().to_csv(results / "development_summary.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, target in zip(axes, TARGETS):
        ax.hist(development[target], bins=20, color="#187b71", edgecolor="white")
        ax.set(title=target.replace("_", " ").title(), xlabel="Dataset target units", ylabel="Development rows")
    fig.tight_layout(); fig.savefig(figures / "distributions.png", dpi=160); plt.close(fig)
    corr = development[NUMERIC+TARGETS].corr()
    fig, ax = plt.subplots(figsize=(9, 7))
    im=ax.imshow(corr, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(len(corr)), corr.columns, rotation=60, ha="right")
    ax.set_yticks(range(len(corr)), corr.columns)
    fig.colorbar(im, ax=ax); fig.tight_layout(); fig.savefig(figures/"correlations.png",dpi=160); plt.close(fig)
    fig, axes=plt.subplots(1,2,figsize=(10,4))
    for ax,target in zip(axes,TARGETS):
        ax.scatter(development.glazing_area,development[target],s=12,alpha=.35,color="#187b71")
        ax.set(xlabel="Glazing area (source feature)",ylabel="Dataset target units",title=target.replace('_',' ').title())
    fig.tight_layout();fig.savefig(figures/'glazing.png',dpi=160);plt.close(fig)
    X = df[FEATURES]
    cv = list(GroupKFold(n_splits=3).split(X.iloc[dev], groups=groups.iloc[dev]))
    for train_fold, valid_fold in cv:
        assert set(groups.iloc[dev].iloc[train_fold]).isdisjoint(groups.iloc[dev].iloc[valid_fold])
    fold_ids=np.full(len(dev),-1)
    for i,(_,valid_fold) in enumerate(cv): fold_ids[valid_fold]=i
    pd.DataFrame({'row_id':df.iloc[dev].row_id,'shape_id':groups.iloc[dev],'validation_fold':fold_ids}).to_csv(results/'cv_assignments.csv',index=False)
    metrics=[]; cv_rows=[]; params={}; records=df.iloc[test][["row_id","shape_id"]+FEATURES+TARGETS].to_dict("records")
    by_shape=[]
    for target in TARGETS:
        y = df[target]
        candidates = {
            "baseline": (DummyRegressor(strategy="mean"), {}),
            "ridge": (Pipeline([("preprocess",preprocessing(True)),("model",Ridge())]), {"model__alpha":[.1,1,10,100]}),
            "forest": (Pipeline([("preprocess",preprocessing(False)),("model",RandomForestRegressor(n_estimators=300,random_state=SEED,n_jobs=1))]),
                       {"model__max_depth":[None,5,10],"model__min_samples_leaf":[1,2,4]})
        }
        for name,(estimator,grid) in candidates.items():
            print(f"Fitting {target}: {name}",flush=True)
            search=GridSearchCV(estimator,grid,cv=cv,scoring="neg_mean_absolute_error",n_jobs=1,refit=True)
            search.fit(X.iloc[dev],y.iloc[dev])
            model=search.best_estimator_
            params[f"{target}/{name}"]=search.best_params_
            pd.DataFrame(search.cv_results_).to_csv(results/f"search_{target}_{name}.csv",index=False)
            # Descriptive scores on folds also used for tuning, not an independent test estimate.
            for i in range(3):
                cv_rows.append({"target":target,"model":name,"fold":i,"mae":-float(search.cv_results_[f"split{i}_test_score"][search.best_index_])})
            prediction=model.predict(X.iloc[test])
            metrics.append({"target":target,"model":name,"mae":float(mean_absolute_error(y.iloc[test],prediction)),"rmse":float(np.sqrt(mean_squared_error(y.iloc[test],prediction)))})
            for record,pred in zip(records,prediction): record[f"{target}_{name}"]=float(pred)
            errors=pd.DataFrame({"shape_id":groups.iloc[test].to_numpy(),"absolute_error":np.abs(y.iloc[test].to_numpy()-prediction)})
            for shape,rows in errors.groupby("shape_id"):
                by_shape.append({"target":target,"model":name,"shape_id":int(shape),"mae":float(rows.absolute_error.mean())})
    pd.DataFrame(metrics).to_csv(results/"test_metrics.csv",index=False)
    pd.DataFrame(cv_rows).to_csv(results/"cv_results.csv",index=False)
    pd.DataFrame(by_shape).to_csv(results/"per_shape_metrics.csv",index=False)
    (results/"best_parameters.json").write_text(json.dumps(params,indent=2))
    predictions=pd.DataFrame(records)
    predictions.to_csv(results/"test_predictions.csv",index=False)
    error_rows=[]
    for target in TARGETS:
        for name in ["baseline","ridge","forest"]:
            ranked=predictions.copy()
            ranked['target']=target;ranked['model']=name
            ranked['actual']=ranked[target];ranked['prediction']=ranked[f'{target}_{name}']
            ranked['absolute_error']=(ranked.actual-ranked.prediction).abs()
            error_rows.append(ranked.nlargest(5,'absolute_error')[["row_id","shape_id"]+FEATURES+["target","model","actual","prediction","absolute_error"]])
    pd.concat(error_rows).to_csv(results/'largest_errors.csv',index=False)
    fig,axes=plt.subplots(2,3,figsize=(13,8))
    for i,target in enumerate(TARGETS):
        for j,name in enumerate(["baseline","ridge","forest"]):
            ax=axes[i,j]; actual=predictions[target];pred=predictions[f'{target}_{name}']
            low=min(actual.min(),pred.min());high=max(actual.max(),pred.max())
            ax.scatter(actual,pred,s=12,alpha=.5,color='#187b71');ax.plot([low,high],[low,high],'k--',lw=1)
            ax.set(title=f'{target}: {name}',xlabel='Simulated load',ylabel='Predicted load')
    fig.tight_layout();fig.savefig(figures/'predictions.png',dpi=160);plt.close(fig)
    summary={"seed":SEED,"development_rows":len(dev),"test_rows":len(test),
             "development_shapes":sorted(groups.iloc[dev].unique().tolist()),"test_shapes":sorted(groups.iloc[test].unique().tolist()),
             "metrics":metrics,"cv":cv_rows,"per_shape":by_shape,"parameters":params,"audit":audit}
    (web/"summary.json").write_text(json.dumps(summary,indent=2,allow_nan=False))
    (web/"predictions.json").write_text(json.dumps(records,indent=2,allow_nan=False))
    versions={name:importlib.metadata.version(name) for name in ['pandas','numpy','scikit-learn','matplotlib','openpyxl']}
    (results/'environment.json').write_text(json.dumps({'python':platform.python_version(),'packages':versions},indent=2))
    (ROOT/'requirements-lock.txt').write_text('\n'.join(f'{name}=={version}' for name,version in versions.items())+'\n')
    from interpret_models import interpret
    interpret()
    from verify_results import verify
    from build_report import build
    verify()
    build()
    print(pd.DataFrame(metrics).to_string(index=False))
    print("Finished. Serve docs with: python -m http.server 8000 --directory docs")

if __name__ == "__main__":
    main()
