import json
import os

NOTEBOOK_DIR = "notebooks"
os.makedirs(NOTEBOOK_DIR, exist_ok=True)

def create_notebook(filename, title, description, code_cells):
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [f"# {title}\n", f"**Description**: {description}"]
        }
    ]
    
    for code in code_cells:
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [code]
        })
        
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.11.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    with open(os.path.join(NOTEBOOK_DIR, filename), "w") as f:
        json.dump(notebook, f, indent=2)

notebooks_config = [
    {
        "filename": "01_EDA.ipynb",
        "title": "Exploratory Data Analysis (EDA)",
        "description": "Analyze dataset overview, statistics, missing values, feature distributions, and correlations.",
        "code_cells": [
            "import pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport seaborn as sns\n\n# Load raw data\n# df = pd.read_csv('../datasets/raw/data.csv')",
            "def perform_eda(df):\n    print('--- Dataset Info ---')\n    print(df.info())\n    print('\\n--- Missing Values ---')\n    print(df.isnull().sum())\n    print('\\n--- Summary Statistics ---')\n    print(df.describe())\n\n# perform_eda(df)",
            "# Heatmap for correlation\n# plt.figure(figsize=(10,8))\n# sns.heatmap(df.corr(), annot=True, cmap='coolwarm')\n# plt.title('Feature Correlation Matrix')\n# plt.show()"
        ]
    },
    {
        "filename": "02_Data_Cleaning.ipynb",
        "title": "Data Cleaning",
        "description": "Handle missing values, duplicates, invalid records, and parse dates.",
        "code_cells": [
            "import pandas as pd\nimport numpy as np\n\n# Load data\n# df = pd.read_csv('../datasets/raw/data.csv')",
            "def clean_data(df):\n    # Drop duplicates\n    df = df.drop_duplicates()\n    \n    # Impute missing values for numeric columns with median\n    num_cols = df.select_dtypes(include=[np.number]).columns\n    df[num_cols] = df[num_cols].fillna(df[num_cols].median())\n    \n    # Forward fill categorical data\n    cat_cols = df.select_dtypes(include=['object']).columns\n    df[cat_cols] = df[cat_cols].fillna(method='ffill')\n    \n    return df\n\n# df_cleaned = clean_data(df)\n# df_cleaned.to_csv('../datasets/cleaned/cleaned_data.csv', index=False)"
        ]
    },
    {
        "filename": "03_Feature_Engineering.ipynb",
        "title": "Feature Engineering",
        "description": "Create new features, perform encoding, scaling, and feature selection.",
        "code_cells": [
            "import pandas as pd\nfrom sklearn.preprocessing import StandardScaler, LabelEncoder\n\n# Load cleaned data\n# df = pd.read_csv('../datasets/cleaned/cleaned_data.csv')",
            "def engineer_features(df):\n    # Date parsing and rolling features example\n    # df['date'] = pd.to_datetime(df['date'])\n    # df['month'] = df['date'].dt.month\n    \n    # Encoding categorical variables\n    cat_cols = df.select_dtypes(include=['object']).columns\n    for col in cat_cols:\n        le = LabelEncoder()\n        df[col] = le.fit_transform(df[col])\n        \n    # Scaling numerical features\n    scaler = StandardScaler()\n    num_cols = df.select_dtypes(include=['float64', 'int64']).columns\n    # Exclude target if needed\n    df[num_cols] = scaler.fit_transform(df[num_cols])\n    \n    return df\n\n# df_processed = engineer_features(df)\n# df_processed.to_csv('../datasets/processed/processed_data.csv', index=False)"
        ]
    },
    {
        "filename": "04_Model_Training.ipynb",
        "title": "Model Training",
        "description": "Train multiple models (Random Forest, XGBoost, LightGBM) and log experiments with MLflow.",
        "code_cells": [
            "import pandas as pd\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.ensemble import RandomForestClassifier\nimport xgboost as xgb\nimport lightgbm as lgb\nimport mlflow\nimport mlflow.sklearn\n\n# Load processed data\n# df = pd.read_csv('../datasets/processed/processed_data.csv')\n# X = df.drop('target', axis=1)\n# y = df['target']\n# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)",
            "def train_xgboost(X_train, y_train):\n    with mlflow.start_run(run_name='XGBoost_Baseline'):\n        model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')\n        model.fit(X_train, y_train)\n        mlflow.sklearn.log_model(model, 'xgboost_model')\n        print('XGBoost model trained and logged to MLflow.')\n        return model\n\n# model = train_xgboost(X_train, y_train)"
        ]
    },
    {
        "filename": "05_Model_Evaluation.ipynb",
        "title": "Model Evaluation",
        "description": "Evaluate models using Accuracy, Precision, Recall, F1 Score, ROC AUC, and plot curves.",
        "code_cells": [
            "import pandas as pd\nimport matplotlib.pyplot as plt\nfrom sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score, roc_curve\nimport seaborn as sns\n\n# Assuming model and X_test, y_test are loaded",
            "def evaluate_model(model, X_test, y_test):\n    y_pred = model.predict(X_test)\n    y_prob = model.predict_proba(X_test)[:, 1]\n    \n    print('Accuracy:', accuracy_score(y_test, y_pred))\n    print('ROC AUC:', roc_auc_score(y_test, y_prob))\n    print('\\nClassification Report:\\n', classification_report(y_test, y_pred))\n    \n    # Confusion Matrix\n    cm = confusion_matrix(y_test, y_pred)\n    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')\n    plt.title('Confusion Matrix')\n    plt.show()\n\n# evaluate_model(model, X_test, y_test)"
        ]
    },
    {
        "filename": "06_Hyperparameter_Tuning.ipynb",
        "title": "Hyperparameter Tuning",
        "description": "Optimize hyperparameters using Optuna (Bayesian Optimization).",
        "code_cells": [
            "import optuna\nimport xgboost as xgb\nfrom sklearn.metrics import accuracy_score\nfrom sklearn.model_selection import train_test_split\n\n# Assuming X, y are loaded",
            "def objective(trial):\n    # Define search space\n    param = {\n        'max_depth': trial.suggest_int('max_depth', 3, 9),\n        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),\n        'n_estimators': trial.suggest_int('n_estimators', 50, 300),\n        'subsample': trial.suggest_float('subsample', 0.6, 1.0)\n    }\n    \n    # Split data\n    # X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2)\n    \n    # Train\n    # model = xgb.XGBClassifier(**param, use_label_encoder=False, eval_metric='logloss')\n    # model.fit(X_train, y_train)\n    \n    # Validate\n    # preds = model.predict(X_val)\n    # return accuracy_score(y_val, preds)\n    return 0.95 # Mock return\n\n# study = optuna.create_study(direction='maximize')\n# study.optimize(objective, n_trials=50)\n# print('Best params:', study.best_params)"
        ]
    },
    {
        "filename": "07_Explainable_AI.ipynb",
        "title": "Explainable AI (SHAP & LIME)",
        "description": "Generate Global and Local explanations using SHAP feature importance.",
        "code_cells": [
            "import shap\nimport matplotlib.pyplot as plt\n\n# Assuming model and X_test are loaded",
            "def explain_model_shap(model, X_test):\n    # Initialize JS visualization\n    shap.initjs()\n    \n    # Create explainer\n    explainer = shap.TreeExplainer(model)\n    shap_values = explainer.shap_values(X_test)\n    \n    # Global Explanation: Summary Plot\n    print('--- Global Feature Importance ---')\n    shap.summary_plot(shap_values, X_test)\n    \n    # Local Explanation: Force Plot for the first prediction\n    print('\\n--- Local Explanation (First Instance) ---')\n    # shap.force_plot(explainer.expected_value, shap_values[0,:], X_test.iloc[0,:])\n    \n# explain_model_shap(model, X_test)"
        ]
    },
    {
        "filename": "08_Error_Analysis.ipynb",
        "title": "Error Analysis",
        "description": "Analyze False Positives and False Negatives to understand model limitations.",
        "code_cells": [
            "import pandas as pd\nimport numpy as np\n\n# Assuming model, X_test, y_test are loaded",
            "def analyze_errors(model, X_test, y_test):\n    # y_pred = model.predict(X_test)\n    # df_results = X_test.copy()\n    # df_results['Actual'] = y_test\n    # df_results['Predicted'] = y_pred\n    \n    # False Positives\n    # fp = df_results[(df_results['Actual'] == 0) & (df_results['Predicted'] == 1)]\n    # print(f'False Positives: {len(fp)}')\n    \n    # False Negatives\n    # fn = df_results[(df_results['Actual'] == 1) & (df_results['Predicted'] == 0)]\n    # print(f'False Negatives: {len(fn)}')\n    \n    # Explore feature distributions of errors\n    # display(fp.describe())\n    pass\n\n# analyze_errors(model, X_test, y_test)"
        ]
    }
]

for cfg in notebooks_config:
    create_notebook(cfg['filename'], cfg['title'], cfg['description'], cfg['code_cells'])

print("Successfully generated all notebooks.")
