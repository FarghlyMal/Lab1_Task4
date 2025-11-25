#!/usr/bin/env python3
"""
ML Model Training Script for DDoS Detection
Trains various ML models on flow features extracted by FlowMeter

Supports:
- Random Forest
- Decision Tree
- Gradient Boosting
- XGBoost (if available)
- Neural Network (MLP)

Outputs:
- Trained model (.pkl file)
- Model evaluation metrics
- Feature importance analysis
"""

import os
import sys
import argparse
import pickle
import json
from datetime import datetime

try:
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.metrics import (
        classification_report, 
        confusion_matrix, 
        accuracy_score,
        precision_score,
        recall_score,
        f1_score,
        roc_auc_score
    )
    from sklearn.utils import shuffle
except ImportError as e:
    print(f"Error: Missing required package - {e}")
    print("Install with: pip3 install numpy pandas scikit-learn --break-system-packages")
    sys.exit(1)

# Try to import XGBoost (optional)
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


# Features to use for training (must match FlowMeter output)
FEATURE_COLUMNS = [
    'flow_duration',
    'total_fwd_packets',
    'total_bwd_packets',
    'total_packets',
    'total_fwd_bytes',
    'total_bwd_bytes',
    'total_bytes',
    'fwd_pkt_len_min',
    'fwd_pkt_len_max',
    'fwd_pkt_len_mean',
    'fwd_pkt_len_std',
    'bwd_pkt_len_min',
    'bwd_pkt_len_max',
    'bwd_pkt_len_mean',
    'bwd_pkt_len_std',
    'pkt_len_min',
    'pkt_len_max',
    'pkt_len_mean',
    'pkt_len_std',
    'pkt_len_var',
    'flow_bytes_per_sec',
    'flow_packets_per_sec',
    'fwd_packets_per_sec',
    'bwd_packets_per_sec',
    'fwd_iat_total',
    'fwd_iat_mean',
    'fwd_iat_std',
    'fwd_iat_min',
    'fwd_iat_max',
    'bwd_iat_total',
    'bwd_iat_mean',
    'bwd_iat_std',
    'bwd_iat_min',
    'bwd_iat_max',
    'flow_iat_mean',
    'flow_iat_std',
    'flow_iat_min',
    'flow_iat_max',
    'syn_flag_count',
    'ack_flag_count',
    'fin_flag_count',
    'rst_flag_count',
    'psh_flag_count',
    'urg_flag_count',
    'down_up_ratio',
    'avg_pkt_size',
    'fwd_seg_size_avg',
    'bwd_seg_size_avg',
]


class DDoSModelTrainer:
    """Trains and evaluates ML models for DDoS detection"""
    
    def __init__(self, model_type='random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = None
        self.metrics = {}
        
    def _create_model(self):
        """Create the specified model type"""
        models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'decision_tree': DecisionTreeClassifier(
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=10,
                learning_rate=0.1,
                random_state=42
            ),
            'mlp': MLPClassifier(
                hidden_layer_sizes=(128, 64, 32),
                activation='relu',
                solver='adam',
                max_iter=500,
                random_state=42
            ),
        }
        
        if self.model_type == 'xgboost':
            if XGBOOST_AVAILABLE:
                return XGBClassifier(
                    n_estimators=100,
                    max_depth=10,
                    learning_rate=0.1,
                    random_state=42,
                    use_label_encoder=False,
                    eval_metric='logloss'
                )
            else:
                print("⚠ XGBoost not available, using Random Forest instead")
                return models['random_forest']
        
        return models.get(self.model_type, models['random_forest'])
    
    def load_data(self, file_path, label_column='label'):
        """Load and prepare dataset"""
        print(f"\n📂 Loading data from: {file_path}")
        
        # Load CSV
        df = pd.read_csv(file_path)
        print(f"   Total samples: {len(df)}")
        
        # Check for label column
        if label_column not in df.columns:
            # Try common alternative label column names before failing
            alternatives = [label_column,
                            'label', 'Label', 'labelled', 'Labelled',
                            'attack', 'Attack', 'class', 'Class',
                            'flow_label', 'FlowLabel', 'Category', 'category']

            found_label = None
            for alt in alternatives:
                if alt in df.columns:
                    found_label = alt
                    break

            if found_label:
                print(f"⚠ Warning: label column '{label_column}' not found. Using '{found_label}' instead.")
                label_column = found_label
            else:
                print("   Available columns:")
                print(list(df.columns))
                raise ValueError(f"Label column '{label_column}' not found in dataset")
        
        # Get available features
        available_features = [col for col in FEATURE_COLUMNS if col in df.columns]
        print(f"   Features found: {len(available_features)}/{len(FEATURE_COLUMNS)}")
        
        if len(available_features) == 0:
            print("   Available columns:", list(df.columns))
            raise ValueError("No matching feature columns found!")
        
        self.feature_columns = available_features
        
        # Prepare features and labels
        X = df[available_features].copy()
        y = df[label_column].copy()
        
        # Handle missing values
        X = X.fillna(0)
        
        # Handle infinite values
        X = X.replace([np.inf, -np.inf], 0)
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Print class distribution
        print(f"\n📊 Class Distribution:")
        for label, count in zip(*np.unique(y, return_counts=True)):
            print(f"   {label}: {count} samples ({count/len(y)*100:.1f}%)")
        
        return X, y_encoded, y
    
    def train(self, X, y, test_size=0.2):
        """Train the model"""
        print(f"\n🏋️ Training {self.model_type} model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"   Training samples: {len(X_train)}")
        print(f"   Testing samples: {len(X_test)}")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Create and train model
        self.model = self._create_model()
        
        start_time = datetime.now()
        self.model.fit(X_train_scaled, y_train)
        training_time = (datetime.now() - start_time).total_seconds()
        
        print(f"   Training time: {training_time:.2f} seconds")
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = None
        
        if hasattr(self.model, 'predict_proba'):
            y_pred_proba = self.model.predict_proba(X_test_scaled)
        
        # Calculate metrics
        self.metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1_score': f1_score(y_test, y_pred, average='weighted'),
            'training_time': training_time,
            'model_type': self.model_type,
            'n_features': len(self.feature_columns),
            'n_train_samples': len(X_train),
            'n_test_samples': len(X_test),
        }
        
        # AUC if binary classification
        if len(np.unique(y)) == 2 and y_pred_proba is not None:
            self.metrics['auc_roc'] = roc_auc_score(y_test, y_pred_proba[:, 1])
        
        return X_test_scaled, y_test, y_pred
    
    def evaluate(self, y_true, y_pred):
        """Print evaluation metrics"""
        print("\n" + "=" * 60)
        print("📈 MODEL EVALUATION RESULTS")
        print("=" * 60)
        
        print(f"\n✓ Accuracy:  {self.metrics['accuracy']*100:.2f}%")
        print(f"✓ Precision: {self.metrics['precision']*100:.2f}%")
        print(f"✓ Recall:    {self.metrics['recall']*100:.2f}%")
        print(f"✓ F1-Score:  {self.metrics['f1_score']*100:.2f}%")
        
        if 'auc_roc' in self.metrics:
            print(f"✓ AUC-ROC:   {self.metrics['auc_roc']*100:.2f}%")
        
        print("\n📊 Classification Report:")
        print("-" * 60)
        
        target_names = self.label_encoder.classes_
        print(classification_report(y_true, y_pred, target_names=target_names))
        
        print("\n📊 Confusion Matrix:")
        print("-" * 60)
        cm = confusion_matrix(y_true, y_pred)
        print(cm)
        
        # Feature importance (for tree-based models)
        if hasattr(self.model, 'feature_importances_'):
            print("\n📊 Top 10 Important Features:")
            print("-" * 60)
            
            importances = self.model.feature_importances_
            indices = np.argsort(importances)[::-1][:10]
            
            for i, idx in enumerate(indices):
                print(f"   {i+1}. {self.feature_columns[idx]}: {importances[idx]:.4f}")
    
    def save_model(self, output_path='ddos_model.pkl'):
        """Save trained model and preprocessing objects"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_columns': self.feature_columns,
            'metrics': self.metrics,
            'model_type': self.model_type,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(output_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\n✓ Model saved to: {output_path}")
        
        # Also save metrics as JSON
        metrics_path = output_path.replace('.pkl', '_metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"✓ Metrics saved to: {metrics_path}")
    
    @staticmethod
    def load_model(model_path):
        """Load a trained model"""
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        return model_data


def create_sample_dataset(output_file='sample_dataset.csv', n_samples=1000):
    """Create a sample dataset for testing (simulated data)"""
    print(f"📝 Creating sample dataset with {n_samples} samples...")
    
    np.random.seed(42)
    
    # Generate normal traffic features
    n_normal = n_samples // 2
    normal_data = {
        'flow_duration': np.random.uniform(1000, 60000000, n_normal),  # 1ms to 60s
        'total_fwd_packets': np.random.randint(1, 100, n_normal),
        'total_bwd_packets': np.random.randint(1, 100, n_normal),
        'total_fwd_bytes': np.random.randint(100, 50000, n_normal),
        'total_bwd_bytes': np.random.randint(100, 50000, n_normal),
        'flow_packets_per_sec': np.random.uniform(1, 100, n_normal),
        'flow_bytes_per_sec': np.random.uniform(100, 10000, n_normal),
        'pkt_len_mean': np.random.uniform(200, 1000, n_normal),
        'pkt_len_std': np.random.uniform(50, 300, n_normal),
        'syn_flag_count': np.random.randint(0, 5, n_normal),
        'ack_flag_count': np.random.randint(1, 100, n_normal),
        'label': ['BENIGN'] * n_normal
    }
    
    # Generate attack traffic features (higher rates, more SYNs, smaller packets)
    n_attack = n_samples - n_normal
    attack_data = {
        'flow_duration': np.random.uniform(100, 5000000, n_attack),  # Shorter
        'total_fwd_packets': np.random.randint(100, 10000, n_attack),  # More packets
        'total_bwd_packets': np.random.randint(0, 50, n_attack),  # Less responses
        'total_fwd_bytes': np.random.randint(5000, 500000, n_attack),
        'total_bwd_bytes': np.random.randint(0, 5000, n_attack),
        'flow_packets_per_sec': np.random.uniform(500, 10000, n_attack),  # High rate
        'flow_bytes_per_sec': np.random.uniform(50000, 1000000, n_attack),  # High bandwidth
        'pkt_len_mean': np.random.uniform(40, 100, n_attack),  # Small packets
        'pkt_len_std': np.random.uniform(0, 20, n_attack),
        'syn_flag_count': np.random.randint(50, 5000, n_attack),  # Many SYNs
        'ack_flag_count': np.random.randint(0, 10, n_attack),  # Few ACKs
        'label': ['DDoS'] * n_attack
    }
    
    # Combine and add remaining features
    all_features = list(FEATURE_COLUMNS) + ['label']
    
    df_normal = pd.DataFrame(normal_data)
    df_attack = pd.DataFrame(attack_data)
    
    df = pd.concat([df_normal, df_attack], ignore_index=True)
    
    # Add missing columns with default values
    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            if 'count' in col or 'packets' in col:
                df[col] = np.random.randint(0, 100, len(df))
            else:
                df[col] = np.random.uniform(0, 1000, len(df))
    
    # Calculate derived features
    df['total_packets'] = df['total_fwd_packets'] + df['total_bwd_packets']
    df['total_bytes'] = df['total_fwd_bytes'] + df['total_bwd_bytes']
    df['avg_pkt_size'] = df['total_bytes'] / (df['total_packets'] + 1)
    
    # Shuffle
    df = shuffle(df, random_state=42)
    
    # Save
    df.to_csv(output_file, index=False)
    print(f"✓ Sample dataset saved to: {output_file}")
    
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Train ML Model for DDoS Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Train with default settings (Random Forest)
  python3 train_model.py -d dataset.csv -o ddos_model.pkl
  
  # Train with specific model
  python3 train_model.py -d dataset.csv -m gradient_boosting -o model.pkl
  
  # Create sample dataset and train
  python3 train_model.py --create-sample -o ddos_model.pkl
  
Available models:
  - random_forest (default)
  - decision_tree
  - gradient_boosting
  - xgboost (if installed)
  - mlp (neural network)
        '''
    )
    
    parser.add_argument('-d', '--dataset', type=str,
                        help='Path to training dataset (CSV)')
    parser.add_argument('-o', '--output', default='ddos_model.pkl',
                        help='Output model file (default: ddos_model.pkl)')
    parser.add_argument('-m', '--model', default='random_forest',
                        choices=['random_forest', 'decision_tree', 'gradient_boosting', 'xgboost', 'mlp'],
                        help='Model type (default: random_forest)')
    parser.add_argument('-l', '--label', default='label',
                        help='Label column name (default: label)')
    parser.add_argument('--test-size', type=float, default=0.2,
                        help='Test set size (default: 0.2)')
    parser.add_argument('--create-sample', action='store_true',
                        help='Create a sample dataset for testing')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🤖 DDoS Detection Model Training")
    print("=" * 60)
    
    # Create sample dataset if requested
    if args.create_sample:
        dataset_path = create_sample_dataset()
    elif args.dataset:
        dataset_path = args.dataset
    else:
        print("❌ Error: Please provide a dataset with -d or use --create-sample")
        sys.exit(1)
    
    # Check if dataset exists
    if not os.path.exists(dataset_path):
        print(f"❌ Error: Dataset not found: {dataset_path}")
        sys.exit(1)
    
    # Create trainer
    trainer = DDoSModelTrainer(model_type=args.model)
    
    # Load data
    X, y, y_original = trainer.load_data(dataset_path, label_column=args.label)
    
    # Train model
    X_test, y_test, y_pred = trainer.train(X, y, test_size=args.test_size)
    
    # Evaluate
    trainer.evaluate(y_test, y_pred)
    
    # Save model
    trainer.save_model(args.output)
    
    print("\n" + "=" * 60)
    print("✅ Training Complete!")
    print("=" * 60)
    print(f"\nTo use this model for detection:")
    print(f"   python3 ddos_detector.py -i eth0 -m {args.output}")
    print("=" * 60)


if __name__ == '__main__':
    main()
