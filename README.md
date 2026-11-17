# Building Energy Explorer — complete ES 335 project

Predict simulated heating and cooling loads for building shapes absent from training. This repository includes executable analysis and a static interactive website. No API key, database, paid service or JavaScript build tool is required.

## 1. Install
Install Python 3.11 or newer. Open this folder in VS Code, then open its terminal.

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```
Windows PowerShell:
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```
If PowerShell blocks activation, invoke `.venv\Scripts\python.exe` instead of `python` in the remaining commands. No activation is then needed.

For the exact direct package versions used in the supplied verified run, install `requirements-lock.txt` instead of `requirements.txt`. Full installed dependency versions are in `results/pip-freeze.txt`.

## 2. Train and evaluate
From this project's top-level folder:
```bash
python src/train.py
python src/verify_results.py
```
The script uses `data/ENB2012_data.xlsx` if present. Otherwise it downloads the UCI ZIP using Python's standard library. If downloading fails, manually download and extract the Excel file from https://archive.ics.uci.edu/dataset/242/energy+efficiency into `data/`, then rerun. Alternatively:
```bash
python src/train.py --data /absolute/path/to/ENB2012_data.xlsx
```
Training can take several minutes. Do not change the split or parameter grid to improve test results after viewing them. Rerunning the unchanged script for reproduction is fine.

## 3. Open the website
```bash
python -m http.server 8000 --directory docs
```
Visit http://localhost:8000 in a browser. Keep the terminal running; Ctrl+C stops it. Do not double-click index.html: browsers may block fetching local JSON files.

Use the shape/orientation/glazing/distribution filters to pick an observed configuration, then switch model and target. Values are precomputed held-out predictions. The worst-error table ranks all held-out rows for the selected model/target, independently of configuration filters.

## 4. Understand and inspect the code
Read `src/train.py` in order: load/audit data; identify geometry groups; save split; plot development data; construct pipelines; tune using grouped folds; evaluate final models; export evidence and website data.

- Eight predictors only. Neither target nor shape ID is used as a predictor.
- Unique combinations of X1–X5 identify the expected 12 groups; unexpected group counts stop execution.
- Fixed seed 42 selects three whole test shapes; nine shapes remain for development.
- Three-fold GroupKFold keeps each development shape together.
- Separate heating/cooling models: mean baseline, scaled Ridge, Random Forest.
- Orientation and glazing distribution are one-hot encoded. Training-fold-only scaling/encoding is enforced by pipelines.
- GridSearchCV selects by MAE. Forest uses 300 trees, depth [None, 5, 10], minimum leaf size [1, 2, 4]. Ridge alpha is [0.1, 1, 10, 100].
- Final test MAE/RMSE are reported separately per target. Baseline mean minimises squared training error; MAE remains the prespecified selection/reporting metric.
- Reported validation fold scores belong to the tuning procedure, so they are descriptive, not independent unbiased estimates. Fold SD is not a confidence interval.

## 5. Evidence files
- `results/data_audit.json`: missing values, duplicates, categories, group counts and input SHA-256.
- `results/split_assignments.csv`: zero-based original data row IDs, shape IDs, development/test labels.
- `results/shape_definitions.csv`: each arbitrary shape ID's geometry.
- `results/cv_assignments.csv`: development row membership in validation folds.
- `results/search_*.csv`: every hyperparameter candidate and fold score.
- `results/best_parameters.json`: chosen settings.
- `results/cv_results.csv`: selected settings' validation-fold MAE.
- `results/test_metrics.csv`: final metrics.
- `results/per_shape_metrics.csv`: test MAE by shape.
- `results/test_predictions.csv`: held-out inputs, targets and predictions.
- `results/largest_errors.csv`: five largest errors per target/model, including input configurations.
- `results/environment.json`: Python and direct package versions.
- `docs/figures/`: development plots and final actual-versus-predicted plots.
- `docs/data/`: JSON used by the website.

## 6. Review before submission
The website now contains a complete evidence-based narrative, representative error cases and the supplied repository link. Review all wording and scores yourself and ensure the AI disclosure remains accurate. Personal identity is not inferred from the repository URL. If adding student identity, use your confirmed name and roll number. Edit narrative structure in `src/site_template.html` or computed interpretations in `src/build_report.py`, then regenerate the report; direct edits to `docs/index.html` will be overwritten.

Viva preparation: explain the row meaning, why this is regression, why random row splitting does not answer the unseen-shape question, why geometry grouping works, why Ridge inputs are scaled, how pipelines prevent leakage, MAE versus RMSE, forest extrapolation limits, and why simulated evidence does not validate real buildings.

## 7. Publish on GitHub Pages
Create a public repository named `building-energy-explorer`. Upload all project folders and files (including docs/data and docs/figures), excluding `.venv/` and caches. You can use GitHub's Upload files interface. With Git installed, from this folder:
```bash
git init
git add .
git commit -m "Add reproducible energy analysis and explorer"
git branch -M main
git remote add origin https://github.com/rokkalababu-dotcom/Rokkala-Mithesh-25110274.git
git push -u origin main
```
The confirmed destination is https://github.com/rokkalababu-dotcom/Rokkala-Mithesh-25110274. Publish the website from main /docs using GitHub Pages settings. Authenticate using GitHub's normal flow; never put credentials in source files.

Repository Settings → Pages → Deploy from a branch → main → /docs → Save. GitHub shows the published URL, normally https://YOUR_USERNAME.github.io/building-energy-explorer/. Verify filters, figures, result values and links on that URL. Submit the live website and source repository links as required by your portal.

## Data, attribution and limitations
Source: Tsanas, A. & Xifara, A. (2012). Energy Efficiency [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C51307. Dataset licence: CC BY 4.0; attribution is required. Original study: Accurate quantitative estimation of energy performance of residential buildings using statistical machine learning tools, Energy and Buildings 49 (2012).

UCI reports 768 simulations, eight inputs, two numerical targets and 12 underlying building shapes. Its variable table does not specify target units, so this project labels metrics as dataset target units. Orientation/distribution use original category codes rather than unsupported compass labels.

Limited shape diversity and only three final test shapes constrain conclusions. The data is simulated, not real-building measurement. Related rows are not independent evidence of 768 different shapes. No causal claims or real deployment guarantees are supported.

AI assistance: ChatGPT/Codex assisted with planning, code, text and debugging. Independently review and explain all outputs, cite any additional external material and update the disclosure to match your actual work.


## 8. Notebook and report regeneration
`notebooks/analysis.ipynb` contains an executed walkthrough of data quality, exact splits, result verification, model comparison and representative errors. It reads the authoritative saved results rather than maintaining a separate training implementation. Optional notebook dependencies:
```bash
python -m pip install jupyterlab
python -m jupyterlab
```
Open the notebook. Run All works from the repository root or notebooks directory. To retrain from scratch use `python src/train.py`; this invokes both verification and report generation. To regenerate only the report and evidence downloads from unchanged results:
```bash
python src/verify_results.py
python src/build_report.py
```
The generated `docs/index.html` includes tables and reasoning without requiring JavaScript. JavaScript adds the explorer. `docs/evidence/reproducibility.zip` includes the code, dataset, executed notebook, result files and static website; there is no recursive evidence ZIP inside it.

## 9. Full experiment inventory
Completed experiments are exactly two targets × three methods. For each target, four Ridge candidates, nine forest candidates and the fixed mean baseline were evaluated with three grouped development folds. All candidates and fold scores are preserved in `results/search_*.csv`. Selected settings are alpha 100 for Ridge, maximum depth 5 and minimum leaf size 1 for the forest, for both targets. The forest uses 300 trees.

No random-row comparison, ablation, alternate-seed search, real-building validation, significance test or uncertainty-calibration experiment was performed. Potential extensions on the website are labelled as future work. The present update adds descriptive analyses of saved predictions; it does not retune after viewing test results.

## 10. Grader evidence map
| Assessment question | Website evidence | Verification files |
|---|---|---|
| What is predicted and when? | Question / prediction-time information | src/train.py input columns |
| What does a row mean? | Data section and variable dictionary | data/ENB2012_data.xlsx |
| Why these transformations? | Preprocessing rationale | Pipeline definitions in src/train.py |
| Why these models? | Method objectives and assumptions | Search grids and search_*.csv |
| How is leakage avoided? | Grouped evaluation explanation | split_assignments.csv, cv_assignments.csv |
| What happened? | Final metrics, plot, per-shape table | test_predictions.csv, test_metrics.csv |
| Where does it fail? | Representative failures and shape discussion | largest_errors.csv, representative_cases.json |
| What can be claimed? | Limitations and qualified conclusion | Full saved validation/test evidence |
| Can it be reproduced? | Reproduction commands and evidence links | This README, notebook, environment and verification files |

AI-use detail: AI_USE.md. Sources and software: CITATIONS.md. Keep the data attribution when redistributing.

## Visual interface
The final interface returns to the original research-report design, recoloured in warm ivory, charcoal, muted olive and bronze, with a compact study overview, sticky section navigation, consistently styled tables and clearly separated report sections. The explorer uses dependent filters and comparison cards. All reasoning is present directly in HTML; app.js supplies the prediction interaction. Fonts use DM Sans from Google Fonts with system fallbacks. No introductory slideshow or decorative animation is required to read the study.

## Sidebar and interpretation update
The report now separates the question, dataset, preprocessing, methods, evaluation, results, interpretation, explorer, errors, limitations, conclusion, reproduction and disclosure. Desktop navigation stays on the left; mobile navigation expands from the contents control and collapses after choosing a section. Current-section highlighting follows scrolling.

`src/interpret_models.py` refits only the already-selected Ridge model on development shapes, verifies that its test predictions match the saved predictions, then writes `results/ridge_coefficients.csv`. This is descriptive model interpretation, not another tuning experiment or causal analysis. `src/train.py` invokes it automatically. To regenerate interpretation alone, run `python src/interpret_models.py` and `python src/build_report.py`.



## Confirmed submission repository
The project destination is https://github.com/rokkalababu-dotcom/Rokkala-Mithesh-25110274. It was verified accessible on November 17, 2026. Existing Assignment1.md and Lab_0.md are unrelated coursework and must be retained. For GitHub Pages, publish main /docs; the project homepage is docs/index.html. The profile-only links and earlier repository-access notes above are superseded by this verified destination.

## Phone and desktop usability update
The current opening page uses a simple navy, blue and white palette. Phone layouts use 15–16 px text, full-width controls, stacked comparison cards, labelled result cards, an expandable contents menu and bottom quick-navigation links. Wide data tables remain horizontally scrollable within their containers; per-shape scores can be expanded on demand. Desktop layouts retain the left sidebar and multi-column evidence tables. The full report remains available; no results or evaluation choices changed.
