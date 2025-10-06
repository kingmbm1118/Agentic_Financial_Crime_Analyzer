"""
Main Demo Script
Demonstrates complete fraud detection workflow with explainable AI
"""
import argparse
import pandas as pd
from data_generator import DataGenerator
from agentic_orchestrator import AgenticOrchestrator


def setup_demo_data(num_transactions=50):
    """Generate demo data if not exists"""
    print("Setting up demo data...")
    generator = DataGenerator(num_transactions=num_transactions)
    data = generator.save_all_data()
    return data


def process_all_transfers(orchestrator, transfers_df):
    """Process all transfers sequentially"""
    print("\n" + "="*80)
    print(f"PROCESSING {len(transfers_df)} TRANSFERS")
    print("="*80)

    results = []

    for idx, row in transfers_df.iterrows():
        transfer = row.to_dict()

        try:
            result = orchestrator.process_transaction(transfer, generate_reports=True)
            results.append(result)

            # Show classification
            classification = result['classification']['classification']
            print(f"✓ {transfer['transaction_id']}: {classification}")

        except Exception as e:
            print(f"✗ {transfer['transaction_id']}: ERROR - {str(e)}")
            results.append({
                'transaction': transfer,
                'error': str(e)
            })

    # Display statistics
    stats = orchestrator.get_statistics(results)

    print("\n" + "="*80)
    print("PROCESSING STATISTICS")
    print("="*80)
    print(f"Total Transfers: {stats['total']}")
    print(f"  ├─ Flagged (High Risk): {stats['flagged']} ({stats['flagged']/stats['total']*100:.1f}%)")
    print(f"  ├─ Needs Investigation: {stats['investigate']} ({stats['investigate']/stats['total']*100:.1f}%)")
    print(f"  └─ Non-Fraud (Low Risk): {stats['non_fraud']} ({stats['non_fraud']/stats['total']*100:.1f}%)")
    print(f"\nCases Created: {stats['cases_created']}")
    print(f"Confirmed Fraud: {stats['confirmed_fraud']}")
    print(f"Average ML Score: {stats['avg_ml_score']:.3f}")

    # Generate summary reports
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')

    # Word reports
    try:
        word_batch_path = f"reports/Summary_Report_{timestamp}.docx"
        orchestrator.word_batch_generator.create_batch_report(
            results,
            stats,
            word_batch_path
        )
        print(f"\nWord summary report: {word_batch_path}")
    except Exception as e:
        print(f"Warning: Could not generate Word summary report: {e}")

    # Closed cases report
    try:
        closed_cases_path = f"reports/Closed_Cases_Report_{timestamp}.docx"
        orchestrator.word_batch_generator.create_closed_cases_report(
            results,
            closed_cases_path
        )
        print(f"Closed cases report: {closed_cases_path}")
    except Exception as e:
        print(f"Warning: Could not generate closed cases report: {e}")

    return results, stats


def show_analysis_details(result):
    """Display detailed analysis breakdown"""
    print("\n" + "="*80)
    print("DETAILED ANALYSIS BREAKDOWN")
    print("="*80)

    if not result:
        print("No result available")
        return

    print("\n1. INITIAL CLASSIFICATION REASONING")
    print("─"*80)
    print(result['classification']['reasoning'])

    print("\n2. RISK FACTORS IDENTIFIED")
    print("─"*80)
    for i, factor in enumerate(result['classification']['risk_factors'], 1):
        print(f"  {i}. {factor}")

    if result.get('investigation'):
        print("\n3. BEHAVIORAL ANALYSIS")
        print("─"*80)
        behavioral = result['investigation']['behavioral_analysis']
        print(f"Profile Risk: {behavioral['profile_risk']}")
        print(f"Login Risk: {behavioral['login_risk']}")
        print(f"Device Risk: {behavioral['device_risk']}")

        print("\n4. ANOMALIES DETECTED")
        print("─"*80)
        for i, anomaly in enumerate(behavioral['behavioral_anomalies'], 1):
            print(f"  {i}. {anomaly}")

        print("\n5. DATA SOURCES ANALYZED")
        print("─"*80)
        for source in result['investigation']['data_sources_checked']:
            print(f"  ✓ {source.replace('_', ' ').title()}")

        print("\n6. FINAL RECOMMENDATION")
        print("─"*80)
        for i, action in enumerate(result['investigation']['recommended_actions'], 1):
            print(f"  {i}. {action}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Saudi Bank Fraud Detection System with Explainable AI'
    )
    parser.add_argument(
        '--num-transactions',
        type=int,
        default=50,
        help='Number of transfers to generate and process (default: 50)'
    )
    parser.add_argument(
        '--no-quantization',
        action='store_true',
        help='Disable model quantization (requires more memory)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='meta-llama/Llama-3.2-3B-Instruct',
        help='LLM model to use (default: Llama-3.2-3B-Instruct)'
    )
    parser.add_argument(
        '--skip-data-generation',
        action='store_true',
        help='Skip data generation (use existing data)'
    )

    args = parser.parse_args()

    print("="*80)
    print("SAUDI BANK FRAUD DETECTION SYSTEM")
    print("AI-Powered Transfer Monitoring & Investigation")
    print("="*80)

    # Step 1: Setup data
    if not args.skip_data_generation:
        data = setup_demo_data(args.num_transactions)
        transfers_df = data['transfers']
    else:
        print("Loading existing data...")
        transfers_df = pd.read_csv('data/sas_transfers.csv')

    # Step 2: Initialize orchestrator
    print("\nInitializing Agentic Orchestrator...")
    orchestrator = AgenticOrchestrator(
        model_name=args.model,
        use_quantization=not args.no_quantization,
        data_dir='data'
    )

    # Step 3: Process transfers
    try:
        # Process all transfers sequentially
        results, stats = process_all_transfers(orchestrator, transfers_df)

        # Show detailed analysis for first investigated case (if any)
        investigated_result = None
        for result in results:
            if result.get('investigation'):
                investigated_result = result
                break

        if investigated_result:
            show_analysis_details(investigated_result)

        # Final summary
        print("\n" + "="*80)
        print("PROCESSING COMPLETE")
        print("="*80)
        print("\nReports Generated:")
        print(f"  ✓ Individual case reports (Word .docx)")
        print(f"  ✓ Summary report (Word .docx)")
        print(f"  ✓ Closed cases report (Word .docx)")
        print(f"  ✓ Text reports (.txt)")
        print("\nAll reports saved to: ./reports/")

    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user")
    except Exception as e:
        print(f"\n\nError during processing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
