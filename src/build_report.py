
"""Regenerate the complete static report and downloadable evidence from saved results.
This script does not train, tune or select models; all error analysis is descriptive.
"""
from pathlib import Path
import hashlib
import json
import html
import zipfile
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
NAMES={'baseline':'Mean baseline','ridge':'Ridge','forest':'Random Forest'}
def table(headers, rows):
    esc=lambda s:html.escape(str(s))
    return '<div class="scroll"><table><thead><tr>'+''.join('<th scope="col">'+esc(c)+'</th>' for c in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(c)+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def tr(values):
    return '<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in values)+'</tr>'
def build():
    s=json.loads((ROOT/'docs/data/summary.json').read_text())
    preds=pd.read_csv(ROOT/'results/test_predictions.csv')
    splits=pd.read_csv(ROOT/'results/split_assignments.csv')
    folds=pd.read_csv(ROOT/'results/cv_assignments.csv')
    assert set(splits.loc[splits.split=='development','shape_id']).isdisjoint(splits.loc[splits.split=='test','shape_id'])
    assert folds.groupby('shape_id').validation_fold.nunique().eq(1).all()
    assert set(preds.row_id)==set(splits.loc[splits.split=='test','row_id'])
    for m in s['metrics']:
        e=preds[f"{m['target']}_{m['model']}"]-preds[m['target']]
        assert np.isclose(e.abs().mean(),m['mae']) and np.isclose(np.sqrt((e**2).mean()),m['rmse'])
    df=pd.read_excel(ROOT/'data/ENB2012_data.xlsx').iloc[:,:10].dropna(how='all')
    assert hashlib.sha256((ROOT/'data/ENB2012_data.xlsx').read_bytes()).hexdigest()==s['audit']['sha256']
    dev=df.iloc[splits.loc[splits.split=='development','row_id']]
    descriptions=[('X1','Relative compactness','Numerical'),('X2','Surface area','Numerical'),('X3','Wall area','Numerical'),('X4','Roof area','Numerical'),('X5','Overall height','Numerical'),('X6','Orientation','Category'),('X7','Glazing area','Numerical'),('X8','Glazing distribution','Category'),('Y1','Heating load','Target'),('Y2','Cooling load','Target')]
    data_rows=[]
    for col,label,kind in descriptions:
        vals=dev[col]
        data_rows.append([col,label,kind,', '.join(map(str,sorted(vals.unique()))) if kind=='Category' else f'{vals.min():g} to {vals.max():g}'])
    data='<h3>What is known at prediction time?</h3><p>The intended use is a fast estimate from design specifications before running an energy simulation. Only X1–X8 are available to the predictor. Neither load target, the row ID nor the shape ID enters a model. A useful result is lower held-out error than the mean baseline, with failures and scope stated explicitly; this is not an energy-bill forecast.</p>'
    data+='<h3>Variable dictionary and development-data coverage</h3>'+table(['Source column','Meaning','Treatment','Development range / codes'],data_rows)
    data+='<p>Access: the public Excel file is included with attribution under CC BY 4.0, and the training script also supplies the UCI download route. The meaningful source columns have no missing values and no exact duplicate rows. However, repeated configurations of each geometry are related observations: the 768 rows are not 768 independent shapes. Each of the 12 verified geometry groups contains 64 configurations. All eight input features are retained; no feature selection or target transformation is performed.</p>'
    # Describe development patterns numerically without consulting final test targets.
    corr=dev[['X1','X2','X3','X4','X5','X7','Y1','Y2']].corr()
    data+=f'<p><strong>Reading the development plots:</strong> relative compactness and surface area have correlation {corr.loc["X1","X2"]:.3f}; geometry features therefore contain overlapping information, motivating a regularised linear comparison. The glazing scatter contains different loads at the same glazing value, so glazing alone cannot identify the target. The histograms describe target coverage, not evidence of real-world representativeness.</p>'
    method='<h3>Why these preprocessing choices?</h3><ul><li><strong>No imputation:</strong> the required values are complete; introducing an imputation step is unnecessary. Unexpected missing values stop the workflow rather than being silently filled.</li><li><strong>No outlier deletion:</strong> there is no independent evidence that high or low simulated loads are data errors. Removing difficult rows because of their targets would alter the question.</li><li><strong>One-hot categories:</strong> orientation and glazing-distribution codes are labels, not quantities with equally spaced effects. Unknown fold categories are handled without consulting validation rows.</li><li><strong>Scaling only for Ridge:</strong> standardisation prevents numerical measurement scales from determining the strength of Ridge’s penalty. Tree threshold decisions do not need that scaling.</li><li><strong>Pipeline isolation:</strong> means, standard deviations and learned category sets are fitted within each training fold. The final test targets do not influence cleaning, tuning or model choice.</li></ul>'
    method+='<h3>Why a grouped split?</h3><p>A random row split could place different glazing/orientation configurations of the same geometry on both sides. That would evaluate unfamiliar configurations of familiar shapes, whereas the question concerns unfamiliar shapes. Grouping by the first five geometry columns gives 12 distinct shapes. The split is selected from geometry groups with seed 42, without using load values; each complete group stays together.</p><p>With nine development shapes, each of three validation folds holds out three shapes (192 configurations) and fits on six shapes (384 configurations). After tuning, the chosen estimator is refitted on all 576 development rows. Three untouched test shapes provide 192 final predictions per target and model. The split and search grid were defined before score comparison; later error analysis does not change them.</p>'
    method+='<h3>Selected settings and their interpretation</h3>'+table(['Target','Ridge alpha','Forest depth','Minimum leaf size','Trees'],[[t.replace('_',' '),s['parameters'][f'{t}/ridge']['model__alpha'],s['parameters'][f'{t}/forest']['model__max_depth'],s['parameters'][f'{t}/forest']['model__min_samples_leaf'],300] for t in ['heating_load','cooling_load']])
    method+='<p>GridSearchCV evaluates all four Ridge settings and nine forest settings per target. The setting with minimum mean validation MAE is chosen within each model family. Ridge’s best alpha is at the largest value in the predefined grid; this identifies the best tested setting, not a global optimum. The grid was not expanded after seeing final test results.</p><h3>What do the metrics measure?</h3><p><code>MAE = mean(|prediction − simulated value|)</code>; <code>RMSE = sqrt(mean((prediction − simulated value)²))</code>. MAE is the primary metric because it gives an interpretable average absolute error in target units. RMSE complements it by penalising large errors more strongly. These are regression errors, not percentage accuracy. Row-averaged MAE gives each configuration equal weight; all test shapes have 64 rows, so it also equals the equally weighted mean of the three shape MAEs.</p><p>The mean baseline is the constant that minimises squared training error, not absolute training error (whose optimal constant is a median). It remains the predefined simple comparator for both MAE and RMSE. No statistical significance test or calibrated prediction interval is claimed.</p>'
    metrics='';findings=[]; result_rows=[]
    for m in s['metrics']:
        values=[v['mae'] for v in s['cv'] if v['target']==m['target'] and v['model']==m['model']]
        metrics+=tr([m['target'].replace('_',' '),NAMES[m['model']],f"{m['mae']:.3f}",f"{m['rmse']:.3f}",f'{np.mean(values):.3f} ± {np.std(values,ddof=1):.3f}'])
    for target in ['heating_load','cooling_load']:
        ms=[m for m in s['metrics'] if m['target']==target]
        base=next(m for m in ms if m['model']=='baseline'); ridge=next(m for m in ms if m['model']=='ridge'); forest=next(m for m in ms if m['model']=='forest')
        gain=100*(base['mae']-ridge['mae'])/base['mae']
        findings.append(f"For {target.replace('_',' ')}, Ridge's MAE is {ridge['mae']:.3f} versus {base['mae']:.3f} for the baseline: a {gain:.1f}% reduction in MAE.")
        result_rows.append([target.replace('_',' '),f'{gain:.1f}%',f"{forest['mae']-ridge['mae']:.3f}"])
    reasoning='<h3>What do the comparisons establish?</h3>'+table(['Target','Ridge MAE reduction vs baseline','Forest MAE minus Ridge MAE'],result_rows)
    reasoning+='<p>Both learned methods beat the constant baseline on both targets: the design inputs carry useful predictive information for this held-out split. Ridge’s lower aggregate test error shows that extra model complexity is not automatically helpful. This is compatible with a regularised additive relationship transferring more reliably across these shapes, but the experiment does not isolate that mechanism. The forest has much greater fold-to-fold validation variation, showing sensitivity to which shapes are absent from training.</p><p>For Ridge, cooling error exceeds heating error in the source target units. Without normalising the target scales, this does not prove cooling is intrinsically harder. RMSE exceeds MAE for every model, indicating uneven error magnitudes; the representative failures below show why reporting only an average is insufficient.</p>'
    analysis='<h3>Where does the overall ranking break down?</h3><p>Ridge wins in aggregate, but not on every shape. On shape 0, the forest’s heating MAE is 2.336 versus Ridge’s 3.694; its cooling MAE is 4.975 versus Ridge’s 5.606. On shape 10, forest heating MAE rises to 5.098 while Ridge achieves 1.986. Thus the aggregate ranking hides a tradeoff across shapes. We cannot conclude that Ridge dominates every unfamiliar geometry.</p>'
    shape_defs=pd.read_csv(ROOT/'results/shape_definitions.csv')
    analysis+='<p>Shape 0 has compactness 0.62 and surface area 808.5, while development compactness spans 0.64–0.98 and surface area 514.5–784. These two inputs lie outside development coverage. This identifies a concrete extrapolation challenge for that shape, though it does not prove the cause of any individual error.</p>'
    cases=[];case_json=[]
    for target in ['heating_load','cooling_load']:
        for model in ['ridge','forest']:
            err=preds[f'{target}_{model}']-preds[target]
            idx=err.abs().idxmax(); r=preds.loc[idx]
            case={'target':target,'model':model,'row_id':int(r.row_id),'shape_id':int(r.shape_id),'actual':float(r[target]),'prediction':float(r[f'{target}_{model}']),'signed_error':float(err.loc[idx]),'absolute_error':float(abs(err.loc[idx]))}
            case_json.append(case)
            cases.append([target.replace('_',' '),NAMES[model],int(r.row_id),int(r.shape_id),f'{r[target]:.3f}',f'{r[f"{target}_{model}"]:.3f}',f'{err.loc[idx]:+.3f}',f'{abs(err.loc[idx]):.3f}',f"{int(r.orientation)} / {r.glazing_area:g} / {int(r.glazing_distribution)}"])
    analysis+='<h3>Representative large failures</h3>'+table(['Target','Model','Row','Shape','Simulated','Predicted','Signed error','Absolute error','Orientation / glazing / distribution'],cases)
    analysis+='<p>These cases are selected by the largest absolute error for each learned model and target, not hand-picked to favour a model. Positive signed error means overprediction; negative means underprediction. Row IDs are zero-based. The explorer permits comparison with other configurations, and the repository includes all 192 test configurations, not just these cases. The cases show where estimates fail; they do not establish causal explanations or justify retraining against the test set.</p>'
    limits='<h3>What would strengthen the evidence?</h3><p>A future study could predefine an outer leave-one-shape-out evaluation to assess variation across more held-out geometries, and evaluate independently collected real-building data. Those are proposed extensions, not experiments performed here. We did not compare random-row and grouped evaluation, run ablations or construct prediction intervals. The complete experiment inventory contains the two targets, three methods, and all predefined tuning candidates.</p>'
    conclusion=' '.join(findings)+' Therefore, design-based prediction improves on the predefined constant comparator for these unseen test shapes, with Ridge the best aggregate method among those tested. The per-shape exceptions and limited simulation coverage prevent a claim of universal superiority or real-building reliability.'
    reproduce='<h3>Verify the complete study</h3><p><a href="https://github.com/rokkalababu-dotcom/Rokkala-Mithesh-25110274">Source repository: Rokkala-Mithesh-25110274</a> · <a href="evidence/reproducibility.zip" download>Download code, notebook, dataset and full results</a> · <a href="evidence/README.md">Setup and run instructions</a></p><p>The evidence download is a self-contained copy of the analysis materials. It is available directly from the website so assessment does not depend on access to another service. The repository must contain the same source, inputs, results and website files.</p><pre><code>python -m venv .venv\n# Activate .venv using your operating system\npython -m pip install -r requirements.txt\npython src/train.py\npython src/verify_results.py\npython -m http.server 8000 --directory docs</code></pre><p>The training command regenerates predictions, figures, the report and its downloadable evidence. The verification command independently checks metrics against predictions, predictions against test targets, grouping, fold separation and data provenance. The notebook reads saved artifacts and documents the same reasoning; training remains in a single source script to avoid hidden notebook state.</p><ul><li><a href="evidence/test_metrics.csv">Full final metrics</a></li><li><a href="evidence/per_shape_metrics.csv">Per-shape errors</a></li><li><a href="evidence/largest_errors.csv">Largest-error configurations</a></li><li><a href="evidence/best_parameters.json">Selected hyperparameters</a></li><li><a href="evidence/split_assignments.csv">Exact development/test assignments</a></li><li><a href="evidence/cv_assignments.csv">Exact validation-fold assignments</a></li><li><a href="evidence/verification.json">Verification record</a></li></ul>'
    coefficient_path=ROOT/'results/ridge_coefficients.csv'
    coeff=pd.read_csv(coefficient_path)
    numeric=coeff[coeff.kind=='standardised numerical']
    interpretation='<p>The following coefficients come from Ridge with its already selected alpha (100), refitted only on the nine development shapes. The refitted predictions match the saved test predictions within numerical tolerance. This is a descriptive analysis of the fixed model, not another tuning experiment.</p>'
    coefficient_rows=[]
    for feature in numeric.feature.unique():
        vals=numeric[numeric.feature==feature].set_index('target').coefficient
        coefficient_rows.append([feature.replace('_',' '),f'{vals["heating_load"]:+.3f}',f'{vals["cooling_load"]:+.3f}'])
    interpretation+=table(['Numerical input','Heating coefficient','Cooling coefficient'],coefficient_rows)
    interpretation+='<p>A numerical coefficient describes the predicted target change for a one-development-standard-deviation increase in that input, holding the encoded inputs fixed. Signs show direction within the fitted model; magnitudes are not percentages. Categorical indicator coefficients are exported separately in the complete coefficient CSV and should not be ranked directly against standardised numerical coefficients.</p>'
    for target in ['heating_load','cooling_load']:
        ranked=numeric[numeric.target==target].copy()
        strongest=ranked.loc[ranked.coefficient.abs().idxmax()]
        interpretation+=f'<p>For {target.replace("_"," ")}, the largest absolute standardised numerical coefficient is {strongest.feature.replace("_"," ")} ({strongest.coefficient:+.3f}). This identifies a strong conditional association in this fitted model, not the most causally important design feature.</p>'
    interpretation+='<p><strong>Why interpretation needs care:</strong> geometry inputs are highly correlated, so their coefficients share credit and a hypothetical change in one input with every other geometry value fixed may not describe a physically possible building. Regularisation and the training shapes affect the values. No ablation or permutation-importance experiment was performed, so we do not claim a unique importance ranking. <a href="evidence/ridge_coefficients.csv">Download every coefficient</a>.</p>'
    overview='<aside class="key-findings" aria-label="Key findings"><p class="eyebrow">THE ANSWER AT A GLANCE</p><h2>Better than the baseline.<br>Different errors across shapes.</h2><div class="finding-grid">'
    for target,label in [('heating_load','Heating MAE'),('cooling_load','Cooling MAE')]:
        val=next(m for m in s['metrics'] if m['target']==target and m['model']=='ridge')
        base=next(m for m in s['metrics'] if m['target']==target and m['model']=='baseline')
        overview+=f'<div><span>{label} · Ridge</span><strong>{val["mae"]:.3f}</strong><small>Baseline {base["mae"]:.3f} · held-out shapes</small></div>'
    overview+='<div><span>The important exception</span><strong>Shape 0</strong><small>Forest beats Ridge on both targets</small></div></div><p>MAE is in dataset target units, not percentage accuracy. Both target scores use the same three held-out shapes. Read the error analysis for the exceptions.</p></aside>'
    preprocess_reasoning, evaluation_reasoning=method.split('<h3>Why a grouped split?</h3>',1)
    method='<h3>Why a grouped split?</h3>'+evaluation_reasoning
    replacements={'AUDIT':'Verified 768 configurations, eight predictors, two targets, 12 geometry groups of 64 rows, zero missing values and zero duplicate source rows.','SPLIT':f"Development: {s['development_rows']} rows from shapes {s['development_shapes']}. Final test: {s['test_rows']} rows from shapes {s['test_shapes']}. Seed 42.",'OVERVIEW':overview,'PREPROCESSING':preprocess_reasoning,'INTERPRETATION':interpretation,'DATA_REASONING':data,'METHOD_REASONING':method,'METRICS':metrics,'FINDING':' '.join(findings),'RESULT_REASONING':reasoning,'SHAPES':''.join(tr([m['target'].replace('_',' '),NAMES[m['model']],m['shape_id'],f"{m['mae']:.3f}"]) for m in s['per_shape']),'ERROR_ANALYSIS':analysis,'CONCLUSION':conclusion,'LIMIT_REASONING':limits,'REPRODUCE':reproduce}
    template=(ROOT/'src/site_template.html').read_text()
    for key,val in replacements.items():template=template.replace('{{'+key+'}}',val)
    assert '{{' not in template
    (ROOT/'docs/index.html').write_text(template)
    (ROOT/'results/representative_cases.json').write_text(json.dumps(case_json,indent=2))
    evidence=ROOT/'docs/evidence';evidence.mkdir(exist_ok=True)
    for filename in ['test_metrics.csv','per_shape_metrics.csv','largest_errors.csv','best_parameters.json','split_assignments.csv','cv_assignments.csv','verification.json','ridge_coefficients.csv']:
        f=ROOT/'results'/filename
        if f.exists():(evidence/filename).write_bytes(f.read_bytes())
    for name in ['AI_USE.md','CITATIONS.md']:
        (evidence/name).write_bytes((ROOT/name).read_bytes())
    (evidence/'README.md').write_bytes((ROOT/'README.md').read_bytes())
    with zipfile.ZipFile(evidence/'reproducibility.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for folder in ['src','results','data','notebooks']:
            for f in sorted((ROOT/folder).rglob('*')):
                if f.is_file() and '__pycache__' not in f.parts:archive.write(f,f.relative_to(ROOT))
        for name in ['README.md','requirements.txt','requirements-lock.txt','AI_USE.md','CITATIONS.md']:
            if (ROOT/name).exists():archive.write(ROOT/name,name)
        for f in sorted((ROOT/'docs').rglob('*')):
            if f.is_file() and 'evidence' not in f.relative_to(ROOT/'docs').parts:archive.write(f,f.relative_to(ROOT))
    print('Built complete static report and downloadable evidence without retraining.')
if __name__=='__main__':build()
