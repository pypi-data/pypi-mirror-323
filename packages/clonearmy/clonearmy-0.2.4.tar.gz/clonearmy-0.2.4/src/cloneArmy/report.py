from typing import Dict, List, Set, Tuple
import json
from pathlib import Path
import base64
from io import BytesIO, StringIO
import datetime
import logging
from collections import defaultdict
import shutil
import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from jinja2 import Template

# Configure plotting styles properly
sns.set_theme(style="whitegrid")  # This sets up seaborn's styling
plt.style.use('default')  # Use matplotlib's default style as a base

logger = logging.getLogger(__name__)

def get_mutations_from_haplotype(haplotype: str, reference_seq: str, count: int) -> List[dict]:
    """Extract mutations from a haplotype sequence."""
    mutations = []
    for pos, (ref, var) in enumerate(zip(reference_seq.upper(), haplotype)):
        if var.islower() or var == '-':  # Mutation or deletion
            mutations.append({
                'position': pos + 1,
                'reference_base': ref,
                'mutation': var.upper(),
                'count': count
            })
    return mutations

def fig_to_base64() -> str:
    """Convert matplotlib figure to base64 string."""
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    buf.seek(0)
    plt.close()
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"

def create_mutation_frequency_plot(results_df: pd.DataFrame, reference_seq: str) -> str:
    """Create an interactive mutation frequency plot using Plotly."""
    if results_df.empty:
        return ""
        
    # Process mutations from all haplotypes
    all_mutations = []
    total_reads = results_df['count'].sum()
    
    for _, row in results_df.iterrows():
        mutations = get_mutations_from_haplotype(row['haplotype'], reference_seq, row['count'])
        all_mutations.extend(mutations)
    
    # Aggregate mutation frequencies
    mutation_freq = defaultdict(int)
    for mut in all_mutations:
        key = f"{mut['position']} {mut['reference_base']}→{mut['mutation']}"
        mutation_freq[key] += mut['count']
    
    # Convert to percentages and sort by position
    positions = []
    frequencies = []
    labels = []
    
    for key, count in sorted(mutation_freq.items(), key=lambda x: int(x[0].split()[0])):
        positions.append(key)
        freq = (count / total_reads) * 100
        frequencies.append(freq)
        labels.append(f"{key}: {freq:.2f}%")
    
    # Create Plotly figure
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=positions,
        y=frequencies,
        marker_color='rgb(31, 119, 180)',
        hovertext=labels,
        name='Mutation Frequency'
    ))
    
    fig.update_layout(
        title='Mutation Frequencies',
        xaxis=dict(
            title='Position and Mutation',
            tickangle=45,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title='Frequency (%)',
            range=[0, max(frequencies) * 1.1]
        ),
        margin=dict(b=100, l=60, r=20, t=40),
        width=max(800, len(positions) * 50),
        height=500,
        template='plotly_white'
    )
    
    # Convert to HTML
    plot_html = fig.to_html(
        full_html=False,
        include_plotlyjs='cdn',
        config={'displayModeBar': True}
    )
    
    return plot_html

def create_mutation_spectrum(results: Dict[str, pd.DataFrame], reference_seq: str) -> str:
    """Create mutation spectrum analysis."""
    mutation_types = defaultdict(int)
    total_mutations = 0
    double_mutations = defaultdict(int)
    
    # Normalize reference sequence once
    reference_seq = reference_seq.upper()
    
    for df in results.values():
        if df.empty:
            continue
            
        for _, row in df.iterrows():
            haplotype = row['haplotype']
            count = row['count']
            
            # Track positions with mutations for linked analysis
            mutation_positions = []
            
            for i, (ref, var) in enumerate(zip(reference_seq, haplotype)):
                if var.islower():  # This identifies a mutation
                    # Create mutation string with both bases in uppercase
                    mutation = f"{ref}>{var.upper()}"
                    # Only count if they're actually different after normalization
                    if ref != var.upper():
                        mutation_types[mutation] += count
                        total_mutations += count
                        mutation_positions.append((i + 1, ref, var.upper()))
            
            # Process linked mutations
            for i in range(len(mutation_positions)):
                for j in range(i + 1, len(mutation_positions)):
                    pos1, ref1, mut1 = mutation_positions[i]
                    pos2, ref2, mut2 = mutation_positions[j]
                    double_key = f"({pos1}{ref1}>{mut1}, {pos2}{ref2}>{mut2})"
                    double_mutations[double_key] += count
    
    if not mutation_types:
        return ""
        
    # Create single mutation spectrum
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    types = sorted(mutation_types.keys())
    counts = [mutation_types[t] for t in types]
    percentages = [100 * c / total_mutations for c in counts]
    
    sns.barplot(x=types, y=percentages)
    plt.title('Single Mutation Spectrum')
    plt.xlabel('Mutation Type')
    plt.ylabel('Percentage of Total Mutations')
    plt.xticks(rotation=45)
    
    # Create linked mutation spectrum (top 10 most frequent)
    plt.subplot(1, 2, 2)
    if double_mutations:
        sorted_doubles = sorted(double_mutations.items(), key=lambda x: x[1], reverse=True)[:10]
        double_types, double_counts = zip(*sorted_doubles)
        double_percentages = [100 * c / total_mutations for c in double_counts]
        
        sns.barplot(x=list(range(len(double_types))), y=double_percentages)
        plt.title('Top 10 Linked Mutations')
        plt.xlabel('Mutation Pair')
        plt.ylabel('Percentage of Total Mutations')
        plt.xticks(range(len(double_types)), double_types, rotation=45, ha='right')
    
    plt.tight_layout()
    return fig_to_base64()

def create_position_mutation_plot(results_df: pd.DataFrame, reference_seq: str) -> str:
    """Create a plot showing number of different mutations at each position."""
    if results_df.empty:
        return ""
    
    # Track unique mutations at each position
    position_mutations = defaultdict(set)
    
    # Process each haplotype
    for _, row in results_df.iterrows():
        haplotype = row['haplotype']
        for pos, (ref, var) in enumerate(zip(reference_seq.upper(), haplotype)):
            if var.islower():  # This is a mutation
                mutation = f"{ref}>{var.upper()}"
                position_mutations[pos + 1].add(mutation)  # 1-based position
    
    # Convert to plot data
    positions = sorted(position_mutations.keys())
    mutation_counts = [len(position_mutations[pos]) for pos in positions]
    
    # Create Plotly figure
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=positions,
        y=mutation_counts,
        marker_color='rgb(158,202,225)',
        hovertemplate="Position: %{x}<br>" +
                     "Different mutations: %{y}<br>" +
                     "Mutations: %{customdata}<extra></extra>",
        customdata=[list(position_mutations[pos]) for pos in positions]
    ))
    
    fig.update_layout(
        title='Mutation Diversity by Position',
        xaxis=dict(
            title='Position in Sequence',
            tickmode='linear'
        ),
        yaxis=dict(
            title='Number of Different Mutations',
            range=[0, max(mutation_counts) * 1.1]
        ),
        margin=dict(b=50, l=60, r=20, t=40),
        width=800,
        height=400,
        template='plotly_white'
    )
    
    # Convert to HTML
    plot_html = fig.to_html(
        full_html=False,
        include_plotlyjs='cdn',
        config={'displayModeBar': True}
    )
    
    return plot_html

def format_summary_table(results: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Format complete summary table with all mutation statistics."""
    summary_data = []
    
    for sample, df in results.items():
        if df.empty:
            continue
            
        # Basic stats
        total_reads = df['count'].sum()
        unique_haplotypes = len(df)
        max_freq = (df['count'].max() / total_reads * 100) if total_reads > 0 else 0.0
        avg_mutations = (df['mutations'] * df['count']).sum() / total_reads if total_reads > 0 else 0.0
        
        # Full length statistics
        full_length_reads = df[df['is_full_length']]['count'].sum()
        full_length_percent = (full_length_reads / total_reads * 100) if total_reads > 0 else 0.0
        
        # Single mutation statistics
        single_mut_reads = df[df['mutations'] == 1]['count'].sum()
        single_mut_percent = (single_mut_reads / total_reads * 100) if total_reads > 0 else 0.0
        
        # Full length single mutations
        full_length_single = df[(df['mutations'] == 1) & (df['is_full_length'])]['count'].sum()
        full_length_single_percent = (full_length_single / total_reads * 100) if total_reads > 0 else 0.0
        
        summary_data.append({
            'sample': sample,
            'total_reads': total_reads,
            'unique_haplotypes': unique_haplotypes,
            'max_frequency': max_freq,
            'avg_mutations': avg_mutations,
            'full_length_reads': full_length_reads,
            'full_length_percent': full_length_percent,
            'single_mutations': single_mut_reads,
            'single_mutation_percent': single_mut_percent,
            'full_length_single_mutations': full_length_single,
            'full_length_single_percent': full_length_single_percent
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Format for display
    if not summary_df.empty:
        # Round percentages to 2 decimal places
        percentage_cols = ['max_frequency', 'full_length_percent', 
                         'single_mutation_percent', 'full_length_single_percent']
        summary_df[percentage_cols] = summary_df[percentage_cols].round(2)
        
        # Round avg_mutations to 2 decimal places
        summary_df['avg_mutations'] = summary_df['avg_mutations'].round(2)
    
    return summary_df


def generate_report(results: Dict[str, pd.DataFrame], 
                   summary: pd.DataFrame, 
                   output_path: Path,
                   reference_seq: str):
    """Generate HTML report with summary table and mutation plots."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Format full summary table
        summary = format_summary_table(results)
        
        # Generate mutation spectrum plot
        mutation_spectrum = create_mutation_spectrum(results, reference_seq)
        
        # Generate single sample mutation frequency plots and position mutation plots
        mutation_plots = {}
        position_plots = {}
        for sample, df in results.items():
            if not df.empty:
                mutation_plots[sample] = create_mutation_frequency_plot(df, reference_seq)
                position_plots[sample] = create_position_mutation_plot(df, reference_seq)
        
        # Calculate additional statistics
        stats_data = {}
        for sample, df in results.items():
            if df.empty:
                continue
                
            mutation_rates = df.groupby('mutations')['count'].sum() / df['count'].sum() * 100
            stats_data[sample] = {
                'mutation_rates': mutation_rates.to_dict(),
                'total_reads': df['count'].sum(),
                'unique_haplotypes': len(df),
                'full_length_percent': (df[df['is_full_length']]['count'].sum() / df['count'].sum() * 100)
            }
        
        # Generate HTML
        template = Template(HTML_TEMPLATE)
        report_html = template.render(
            date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            summary=summary.to_html(
                classes=['table', 'table-striped', 'table-bordered', 'table-hover'],
                index=False,
                float_format=lambda x: '{:,.2f}'.format(x) if isinstance(x, float) else '{:,}'.format(x) if isinstance(x, int) else x
            ),
            mutation_spectrum=mutation_spectrum,
            mutation_plots=mutation_plots,
            position_plots=position_plots,
            stats=stats_data,
            has_data=bool(results and any(not df.empty for df in results.values()))
        )
        
        # Write report
        with output_path.open('w') as f:
            f.write(report_html)
            
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>CloneArmy Analysis Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.datatables.net/1.11.5/css/dataTables.bootstrap5.min.css" rel="stylesheet">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.11.5/js/dataTables.bootstrap5.min.js"></script>
    <style>
        body { padding: 20px; }
        .plot-container { margin: 20px 0; }
        .table {
            font-size: 0.9rem;
            width: 100% !important;
        }
        .plot-description {
            font-size: 0.9rem;
            color: #666;
            margin-top: 10px;
        }
        .dataTables_wrapper {
            padding: 10px 0;
        }
        .card-body {
            overflow-x: auto;
        }
        th, td {
            white-space: nowrap;
        }
        .text-end {
            text-align: right;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="mb-4">CloneArmy Analysis Report</h1>
        <p class="text-muted">Generated on: {{ date }}</p>

        <!-- Sample Summary -->
        <div class="card mb-4">
            <div class="card-header">
                <h2 class="h4 mb-0">Sample Summary</h2>
            </div>
            <div class="card-body">
                {{ summary }}
                <p class="plot-description">
                    Overview of sequencing results and mutation statistics for each sample.
                </p>
            </div>
        </div>

        <!-- Mutation Spectrum -->
        {% if mutation_spectrum %}
        <div class="card mb-4">
            <div class="card-header">
                <h2 class="h4 mb-0">Overall Mutation Spectrum</h2>
            </div>
            <div class="card-body">
                <img src="{{ mutation_spectrum }}" class="img-fluid" alt="Mutation Spectrum">
                <p class="plot-description">
                    Left: Distribution of single mutation types (e.g., A>T, G>C). Shows the percentage 
                    of each mutation type among all observed mutations.<br>
                    Right: Top 10 most frequent linked mutations showing co-occurring mutation pairs.
                </p>
            </div>
        </div>
        {% endif %}

        <!-- Per-Sample Statistics and Plots -->
        {% for sample, stats in stats.items() %}
        <div class="card mb-4">
            <div class="card-header">
                <h2 class="h4 mb-0">{{ sample }} Details</h2>
            </div>
            <div class="card-body">
                <!-- Mutation Frequency Plot -->
                {% if mutation_plots[sample] %}
                <div class="plot-container">
                    {{ mutation_plots[sample] | safe }}
                    <p class="plot-description">
                        Distribution of individual mutation frequencies across the sequence.
                        Each bar represents the percentage of reads containing a specific mutation.
                    </p>
                </div>
                {% endif %}
                
                <!-- Position Mutation Plot -->
                {% if position_plots[sample] %}
                <div class="plot-container">
                    {{ position_plots[sample] | safe }}
                    <p class="plot-description">
                        Number of different mutations observed at each position.
                        Hover over bars to see the specific mutations at each position.
                    </p>
                </div>
                {% endif %}
                
                <div class="row mt-4">
                    <div class="col-md-6">
                        <h3 class="h5">Basic Statistics</h3>
                        <ul>
                            <li>Total Reads: {{ "{:,}".format(stats.total_reads) }}</li>
                            <li>Unique Haplotypes: {{ "{:,}".format(stats.unique_haplotypes) }}</li>
                            <li>Full Length Sequences: {{ "%.2f"|format(stats.full_length_percent) }}%</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h3 class="h5">Mutation Rates</h3>
                        <ul>
                            {% for mutations, rate in stats.mutation_rates.items() %}
                            <li>{{ mutations }} mutation(s): {{ "%.2f"|format(rate) }}%</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}

        <footer class="mt-5 pt-3 border-top text-muted">
            <small>Generated by CloneArmy | Data processed: {{ date }}</small>
        </footer>
    </div>

    <script>
        $(document).ready(function() {
            $('.table').DataTable({
                pageLength: 25,
                order: [[1, 'desc']],
                dom: 'Bfrtip',
                buttons: ['copy', 'csv', 'excel']
            });
        });
    </script>
</body>
</html>
"""