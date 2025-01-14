import matplotlib.pyplot as plt
import numpy as np

def plot_classification_report_from_dict(report_dict):
    # Extract metrics and classes from the dictionary
    classes = list(report_dict.keys())
    metrics = ['precision', 'recall', 'f1-score']
    
    # Prepare data for plotting
    data = np.array([[report_dict[cls][metric] for metric in metrics] for cls in classes])
    
    # Create a bar plot
    x = np.arange(len(classes))  # the label locations
    width = 0.2  # the width of the bars

    fig, ax = plt.subplots(figsize=(14, 8))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Colors for each metric

    for i, metric in enumerate(metrics):
        bars = ax.bar(x + i * width, data[:, i], width, label=metric, color=colors[i], edgecolor='black')

        # Add annotations on top of the bars
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.02, f'{yval:.2f}', ha='center', va='bottom', fontsize=10)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Scores', fontsize=14)
    ax.set_title('Classification Report', fontsize=16)
    ax.set_xticks(x + width)
    ax.set_xticklabels(classes, fontsize=12)
    ax.legend(fontsize=12)
    
    # Add gridlines
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)

    plt.ylim(0, 1)  # Set y-axis limits to [0, 1] for better visualization
    plt.tight_layout()
    plt.savefig('classification_report.png')  # Save the figure
    plt.show()  # Show the plot
    
# Example usage
classification_report_dict = {
    'Strong Buy': {'precision': 0.85, 'recall': 0.80, 'f1-score': 0.82},
    'Weak Buy': {'precision': 0.75, 'recall': 0.70, 'f1-score': 0.72},
    'Weak Sell': {'precision': 0.65, 'recall': 0.60, 'f1-score': 0.62},
    'Strong Sell': {'precision': 0.90, 'recall': 0.88, 'f1-score': 0.89}
}

plot_classification_report_from_dict(classification_report_dict)