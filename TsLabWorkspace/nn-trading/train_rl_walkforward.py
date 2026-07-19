"""DQN walk-forward validation with hybrid ensemble integration."""
import random
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Subset
from collections import deque

from dataset import TimeSeriesDataset, auto_select_features, fit_scaler
from model import build_model, Ensemble, HybridEnsemble, build_sklearn_models
from train import train
from rl_agent import DuelingDQN, ReplayBuffer, TradingEnv, train_dqn, evaluate_dqn


class WalkForwardDQN:
    """DQN with walk-forward validation and ensemble integration."""
    
    def __init__(self, config, device="cpu", use_ensemble=True):
        self.config = config
        self.device = torch.device(device)
        self.use_ensemble = use_ensemble
        self.neural_models = []
        self.sklearn_wrappers = []
        
    def train_step(self, train_df, val_df, test_df, feature_cols):
        """Train one walk-forward step with hybrid approach."""
        
        # 1. Train neural ensemble (same as standard walk-forward)
        scaler = fit_scaler(train_df, feature_cols)
        
        train_ds_full = TimeSeriesDataset(
            train_df, self.config.window, feature_cols=feature_cols, scaler=scaler
        )
        
        # Split train into train/val
        val_split = int(len(train_ds_full) * 0.85)
        train_indices = list(range(0, val_split))
        val_indices = list(range(val_split, len(train_ds_full)))
        
        train_ds = Subset(train_ds_full, train_indices)
        val_ds = Subset(train_ds_full, val_indices)
        
        # Train neural models
        seeds = [42, 43, 44]  # 3 models
        base_models = []
        
        for seed in seeds:
            torch.manual_seed(seed)
            random.seed(seed)
            np.random.seed(seed)
            
            model = build_model(self.config, len(feature_cols))
            model = train(model, train_ds, val_ds, self.config, self.device, quiet=True)
            base_models.append(model)
        
        self.neural_models = base_models
        
        # Train sklearn models
        X_train_flat = []
        y_train = []
        for i in range(len(train_ds)):
            x, label = train_ds[i]
            X_train_flat.append(x.numpy().flatten())
            y_train.append(label.item())
        X_train_flat = np.array(X_train_flat)
        y_train = np.array(y_train)
        
        self.sklearn_wrappers = build_sklearn_models(
            X_train_flat, y_train,
            window=self.config.window,
            n_features=len(feature_cols),
            n_cpu=self.config.n_cpu_threads,
        )
        
        # Build hybrid ensemble
        all_neural = base_models
        all_sklearn = [w for _, w in self.sklearn_wrappers]
        self.ensemble = HybridEnsemble(all_neural, all_sklearn)
        
        # 2. Train DQN agent on ensemble predictions
        # Get ensemble predictions for DQN training
        train_probs = self._get_ensemble_probs(train_df, feature_cols, scaler)
        val_probs = self._get_ensemble_probs(val_df, feature_cols, scaler)
        
        # Prepare DQN data
        train_prices = train_df["Close"].values.astype(np.float64)
        val_prices = val_df["Close"].values.astype(np.float64)
        
        return train_probs, val_probs, train_prices, val_prices, scaler
        
    def _get_ensemble_probs(self, df, feature_cols, scaler):
        """Get ensemble probabilities for a dataframe."""
        dataset = TimeSeriesDataset(df, self.config.window, feature_cols=feature_cols, scaler=scaler)
        
        self.ensemble.eval()
        loader = torch.utils.data.DataLoader(dataset, batch_size=256, shuffle=False)
        
        probs = []
        with torch.no_grad():
            for x, _ in loader:
                x = x.to(self.device)
                logits = self.ensemble(x)
                prob = torch.sigmoid(logits).cpu().numpy().flatten()
                probs.extend(prob)
                
        return np.array(probs)


def walk_forward_dqn(df, config, device="cpu", n_folds=5, feature_cols=None):
    """
    Walk-forward validation with DQN ensemble integration.
    
    For each fold:
    1. Train hybrid neural+sklearn ensemble on train set
    2. Train DQN agent on ensemble predictions
    3. Test ensemble + DQN on validation set
    4. Repeat
    """
    from config import Config
    
    if feature_cols is None:
        feature_cols = auto_select_features(df, df["label"], max_features=config.max_features)
    
    total = len(df)
    test_size = total // (n_folds + 1)
    min_train_size = total // (n_folds + 1)
    embargo = 7
    
    wf_dqn = WalkForwardDQN(config, device)
    
    print(f"\n{'='*60}")
    print(f"WALK-FORWARD DQN: {n_folds} folds")
    print(f"Total: {total} | Test fold: {test_size} | Features: {len(feature_cols)}")
    print(f"{'='*60}")
    
    for fold in range(n_folds):
        train_end = min_train_size + fold * test_size
        test_start = train_end + embargo
        test_end = min(test_start + test_size, total)
        
        if test_end <= test_start:
            break
            
        print(f"\nFold {fold+1}/{n_folds}")
        print(f"  Train: 0-{train_end} | Test: {test_start}-{test_end}")
        
        # Split data
        train_df = df.iloc[:train_end]
        test_df = df.iloc[test_start:test_end]
        
        # Train ensemble and get predictions
        train_probs, val_probs, train_prices, val_prices, scaler = wf_dqn.train_step(
            train_df, test_df, test_df, feature_cols
        )
        
        # Train DQN on ensemble predictions
        # Use ensemble probs as features for DQN
        state_size = config.window * len(feature_cols)
        
        dqn_env = TradingEnv(
            train_prices, train_probs.reshape(-1, 1),
            window=config.window, commission=0.001, stop_loss=0.03, take_profit=0.09
        )
        
        dqn_agent = train_dqn(
            train_prices, train_probs.reshape(-1, 1),
            window=config.window, episodes=50,  # Fewer episodes for faster training
            commission=0.001, stop_loss=0.03, take_profit=0.09, min_confidence=0.5,
            n_cpu=config.n_cpu_threads, quiet=True
        )
        
        # Evaluate
        result = evaluate_dqn(
            dqn_agent, val_prices, val_probs.reshape(-1, 1),
            window=config.window, commission=0.001, stop_loss=0.03, 
            take_profit=0.09, min_confidence=0.5
        )
        
        print(f"  DQN: Return {result['total_return_pct']:+.2f}% | "
              f"Trades {result['n_trades']} | Win {result['win_rate_pct']:.1f}%")
    
    return wf_dqn


if __name__ == "__main__":
    import json
    
    # Load BTC data
    cache = "data/binance_BTCUSDT_15m.csv"
    df = pd.read_csv(cache, index_col=0, parse_dates=True)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Prepare features
    from features import prepare_features
    from dataset import auto_select_features
    
    cfg = Config()
    cfg.window = 30
    cfg.model_type = "attention"
    cfg.hidden_size = 32
    cfg.num_layers = 1
    cfg.dropout = 0.2
    cfg.max_features = 30
    
    df = prepare_features(df, cfg)
    feature_cols = auto_select_features(df, df["label"], max_features=cfg.max_features)
    
    # Run walk-forward DQN
    wf_dqn = walk_forward_dqn(df, cfg, "cpu", n_folds=3, feature_cols=feature_cols)
    
    print("\nWalk-forward DQN completed!")
