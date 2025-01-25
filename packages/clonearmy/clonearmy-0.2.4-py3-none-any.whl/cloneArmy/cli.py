import sys
from pathlib import Path
from typing import Optional
import time
import logging

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import print as rprint
from Bio import SeqIO

from . import process_samples, summarize_results, validate_input, __version__
from .report import generate_report
from .comparison import run_comparative_analysis

console = Console()

def load_reference_sequence(reference_path: Path) -> str:
    """Load the reference sequence from a FASTA file."""
    try:
        with open(reference_path) as handle:
            record = next(SeqIO.parse(handle, "fasta"))
            return str(record.seq)
    except Exception as e:
        console.print(f"[bold red]Error loading reference sequence:[/] {str(e)}")
        sys.exit(1)

def print_version(ctx, param, value):
    """Print version and exit."""
    if not value or ctx.resilient_parsing:
        return
    console.print(f"CloneArmy version [bold cyan]{__version__}[/]")
    ctx.exit()

@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help="Show version and exit.")
@click.option('--debug/--no-debug', default=False, help="Enable debug logging.")
def cli(debug: bool):
    """
    CloneArmy: Analyze haplotypes from Illumina paired-end amplicon sequencing.
    
    This tool processes FASTQ files to identify and quantify sequence variants
    and haplotypes in amplicon sequencing data.
    """
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

@cli.command()
@click.argument('fastq_dir', type=click.Path(exists=True))
@click.argument('reference', type=click.Path(exists=True))
@click.option('--threads', '-t', default=8, help='Number of threads to use')
@click.option('--output', '-o', type=click.Path(), help='Output directory')
@click.option('--min-base-quality', '-q', default=20, 
              help='Minimum base quality score')
@click.option('--min-mapping-quality', '-Q', default=30,
              help='Minimum mapping quality score')
@click.option('--min-read-count', '-r', default=10,
              help='Minimum number of reads to consider a haplotype')
@click.option('--max-file-size', '-m', default=10_000_000_000,
              help='Maximum file size in bytes (default: 10GB)')
@click.option('--report/--no-report', default=True,
              help='Generate HTML report')
def run(fastq_dir: str, reference: str, threads: int, output: Optional[str],
        min_base_quality: int, min_mapping_quality: int, min_read_count: int,
        max_file_size: int, report: bool):
    """Process amplicon sequencing data."""
    
    # Show welcome message
    console.print(Panel.fit(
        "[bold blue]CloneArmy[/] - Amplicon Analysis Tool",
        subtitle=f"Version {__version__}"
    ))

    # Load reference sequence
    reference_path = Path(reference)
    ref_seq = load_reference_sequence(reference_path)

    # Validate input
    with console.status("[bold yellow]Validating input..."):
        warnings = validate_input(fastq_dir, reference)
        if warnings:
            console.print("\n[bold red]Validation Warnings:[/]")
            for warning in warnings:
                console.print(f"⚠️  {warning}")
            if not click.confirm("Continue anyway?"):
                sys.exit(1)

    # Process samples
    start_time = time.time()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Processing samples...", total=None)
        
        try:
            results = process_samples(
                fastq_dir=fastq_dir,
                reference=reference,
                output_dir=output,
                threads=threads,
                min_base_quality=min_base_quality,
                min_mapping_quality=min_mapping_quality,
                min_read_count=min_read_count,
                max_file_size=max_file_size
            )
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"\n[bold red]Error:[/] {str(e)}")
            sys.exit(1)

    # Generate complete summary
    from .report import format_summary_table
    summary = format_summary_table(results)
    
    # Display results
    console.print("\n[bold green]Analysis Complete![/]")
    
    # Create rich table
    table = Table(title="Sample Summary")
    table.add_column("Sample", style="cyan")
    table.add_column("Total Reads", justify="right", style="green")
    table.add_column("Unique Haplotypes", justify="right", style="blue")
    table.add_column("Max Frequency (%)", justify="right", style="magenta")
    table.add_column("Avg Mutations", justify="right", style="yellow")
    
    for _, row in summary.iterrows():
        table.add_row(
            row['sample'],
            f"{row['total_reads']:,}",
            f"{row['unique_haplotypes']:,}",
            f"{row['max_frequency']:.2f}",
            f"{row['avg_mutations']:.2f}"
        )
    
    console.print(table)
    
    # Generate report if requested
    if report:
        output_dir = Path(output) if output else Path(fastq_dir) / 'results'
        report_path = output_dir / 'report.html'
        
        with console.status("[bold yellow]Generating report..."):
            generate_report(
                results=results,
                summary=summary,
                output_path=report_path,
                reference_seq=ref_seq
            )
        
        console.print(f"\nReport generated: [blue]{report_path}[/]")
    
    # Show completion message
    elapsed = time.time() - start_time
    console.print(f"\nTotal processing time: [bold]{elapsed:.1f}[/] seconds")

@cli.command()
@click.argument('fastq_dir1', type=click.Path(exists=True))
@click.argument('fastq_dir2', type=click.Path(exists=True))
@click.argument('reference', type=click.Path(exists=True))
@click.option('--threads', '-t', default=8, help='Number of threads to use')
@click.option('--output', '-o', type=click.Path(), help='Output directory')
@click.option('--min-base-quality', '-q', default=20, 
              help='Minimum base quality score')
@click.option('--min-mapping-quality', '-Q', default=30,
              help='Minimum mapping quality score')
@click.option('--min-read-count', '-r', default=10,
              help='Minimum number of reads to consider a haplotype')
@click.option('--max-file-size', '-m', default=10_000_000_000,
              help='Maximum file size in bytes (default: 10GB)')
@click.option('--full-length-only', '-f', is_flag=True,
              help='Only consider sequences that cover the entire reference')
def compare(fastq_dir1: str, fastq_dir2: str, reference: str, threads: int, 
           output: Optional[str], min_base_quality: int, min_mapping_quality: int,
           min_read_count: int, max_file_size: int, full_length_only: bool):
    """Compare mutation frequencies between two samples."""
    
    console.print(Panel.fit(
        "[bold blue]CloneArmy[/] - Comparative Analysis",
        subtitle=f"Version {__version__}"
    ))
    
    # Load reference sequence
    reference_path = Path(reference)
    ref_seq = load_reference_sequence(reference_path)
    
    # Set up output directory
    output_dir = Path(output) if output else Path('comparison_results')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process both samples
    with console.status("[bold yellow]Processing sample 1..."):
        results1 = process_samples(
            fastq_dir=fastq_dir1,
            reference=reference,
            output_dir=output_dir / 'sample1',
            threads=threads,
            min_base_quality=min_base_quality,
            min_mapping_quality=min_mapping_quality,
            min_read_count=min_read_count,
            max_file_size=max_file_size
        )
    
    with console.status("[bold yellow]Processing sample 2..."):
        results2 = process_samples(
            fastq_dir=fastq_dir2,
            reference=reference,
            output_dir=output_dir / 'sample2',
            threads=threads,
            min_base_quality=min_base_quality,
            min_mapping_quality=min_mapping_quality,
            min_read_count=min_read_count,
            max_file_size=max_file_size
        )
    
    # Check if we have valid results
    if not results1 or not results2:
        console.print("[bold red]No valid results found in one or both samples[/]")
        return
    
    # Run comparative analysis
    with console.status(
        f"[bold yellow]Performing comparative analysis{'(full-length only)' if full_length_only else ''}..."
    ):
        try:
            comparison_results = run_comparative_analysis(
                results1=results1,
                results2=results2,
                reference_seq=ref_seq,
                output_path=output_dir / 'comparison_results.csv',
                full_length_only=full_length_only
            )
            
            if comparison_results.empty:
                console.print("[bold yellow]No mutations found for comparison[/]")
                return
                
            # In the compare function, update the success message:
            if not comparison_results.empty:
                console.print(f"\nResults saved to: [blue]{output_dir}/comparison_results.csv[/]")
                console.print(f"Interactive plot saved to: [blue]{output_dir}/mutation_comparison_plot.html[/]")

            # Display results table
            table = Table(title="Significant Mutations (FDR < 0.05)")
            
            # Add columns
            table.add_column("Position", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Ref→Mut", style="green")
            table.add_column("Sample 1 %", justify="right", style="blue")
            table.add_column("Sample 2 %", justify="right", style="blue")
            table.add_column("FDR p-value", justify="right", style="magenta")
            
            # Add rows (show only significant results)
            if 'fdr_pvalue' in comparison_results.columns:
                significant = comparison_results[comparison_results['fdr_pvalue'] < 0.05]
                if not significant.empty:
                    for _, row in significant.iterrows():
                        table.add_row(
                            str(row['position']),
                            row.get('mutation_type', 'substitution'),
                            f"{row['reference_base']}→{row['mutation']}",
                            f"{row['sample1_percent']:.4f}",
                            f"{row['sample2_percent']:.4f}",
                            f"{row['fdr_pvalue']:.6f}"
                        )
                    console.print(table)
                    
                    # Show output locations
                    console.print(f"\nResults saved to: [blue]{output_dir}/comparison_results.csv[/]")
                    console.print(f"Interactive plot saved to: [blue]{output_dir}/mutation_comparison_plot.html[/]")
                else:
                    console.print("[bold yellow]No significant mutations found (FDR < 0.05)[/]")
            else:
                console.print("[bold yellow]No statistical results available[/]")
                
        except Exception as e:
            console.print(f"[bold red]Error in comparative analysis:[/] {str(e)}")
            raise

if __name__ == '__main__':
    cli()