import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class Algorithmic_Trading_Visuals:
    def __init__(self):
        self.objects = None
        
    def plot_pnl_heatmaps(self, data):
        """
        Plot Total PnL heatmaps with different Z-Score Thresholds, comparing strategies.
        Colormap centered at 0.00
        """
        sns.set(style="whitegrid")
        z_scores = sorted(data['Z-Score Threshold'].unique())

        # Subplots
        fig, axes = plt.subplots(nrows=len(z_scores), ncols=2, figsize=(14, len(z_scores)*3))
        fig.suptitle('Total PnL Heatmaps by Z-Score Threshold and Trend Alignment', fontsize=16)
        # Determine the range for the colormap to center at zero
        all_pnls = pd.concat([data['Total PnL'], data['Total PnL Trend Alignment']])
        vmin = all_pnls.min()
        vmax = all_pnls.max()
        max_abs_pnl = max(abs(vmin), abs(vmax))

        # Iterate Z-Score
        for i, z_score in enumerate(z_scores):
            # Filter Data
            df_no_trend = data[data['Z-Score Threshold'] == z_score]
            df_trend = data[data['Z-Score Threshold Trend Alignment'] == z_score]
            # Pivot Tables for Heatmaps
            pivot_no_trend = df_no_trend.pivot_table(index='Profit Target', columns='Stop Loss', values='Total PnL',
                                                     aggfunc='mean')
            pivot_trend = df_trend.pivot_table(index='Profit Target Trend Alignment', columns='Stop Loss Trend Alignment',
                                               values='Total PnL Trend Alignment', aggfunc='mean')
            # Sort the indices for consistent plotting
            pivot_no_trend = pivot_no_trend.sort_index().sort_index(axis=1)
            pivot_trend = pivot_trend.sort_index().sort_index(axis=1)

            # Plot Heatmaps
            sns.heatmap(pivot_no_trend, ax=axes[i, 0], annot=True, fmt=".4f", cmap="RdYlGn", center=0.0,
                        vmin=-max_abs_pnl, vmax=max_abs_pnl, cbar_kws={'label': 'Total PnL'})
            sns.heatmap(pivot_trend, ax=axes[i, 1], annot=True, fmt=".4f", cmap="RdYlGn", center=0.0,
                        vmin=-max_abs_pnl, vmax=max_abs_pnl, cbar={"label": "Total PnL"})

            # Set titles and labels
            axes[i, 0].set_title(f'Z-Score {z_score} - Without Trend Alignment')
            axes[i, 1].set_title(f'Z-Score {z_score} - With Trend Alignment')
            axes[i, 0].set_xlabel('Stop Loss')
            axes[i, 0].set_ylabel('Profit Target')
            axes[i, 1].set_xlabel('Stop Loss')
            axes[i, 1].set_ylabel('Profit Target')

        # Adjust layout
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()