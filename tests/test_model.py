"""Checks on the dataset and the trained model (run after train.py)."""
import json
from pathlib import Path
import pandas as pd

CONFIG = json.loads(Path('config.json').read_text())
METRICS_FILE = Path('artifacts/metrics.json')

def test_config_is_mine():
    assert CONFIG['student_id'] == 'FA23-BDS-025'

def test_dataset_has_required_columns():
    df = pd.read_csv('dataset/train.csv')
    assert set(CONFIG['features'] + ['label']).issubset(df.columns)
    assert len(df) >= 100
    assert df['label'].nunique() == 2

def test_metrics_file_written():
    assert METRICS_FILE.exists(), 'run train.py first'
    m = json.loads(METRICS_FILE.read_text())
    for key in ['student_id', 'accuracy', 'training_rows', 'model_version', 'git_sha']:
        assert key in m
    assert m['student_id'] == 'FA23-BDS-025'

def test_metrics_match_current_dataset():
    m = json.loads(METRICS_FILE.read_text())
    assert m['training_rows'] == len(pd.read_csv('dataset/train.csv'))

def test_accuracy_is_reasonable():
    m = json.loads(METRICS_FILE.read_text())
    assert 0.6 <= m['accuracy'] <= 1.0
