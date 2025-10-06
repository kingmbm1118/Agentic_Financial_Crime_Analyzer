"""
Agentic Orchestrator
Coordinates all agents in the fraud detection workflow
"""
import pandas as pd
from typing import Dict, Any, List
from llm_agent import AlertingAgent
from monitoring_agent import MonitoringAgent
from investigator_agent import InvestigatorAgent
from report_generator import ReportGenerator
from word_report_generator import WordReportGenerator
from word_batch_report import WordBatchReportGenerator


class AgenticOrchestrator:
    """Main orchestrator coordinating all agents in the workflow"""

    def __init__(self,
                 model_name="meta-llama/Llama-3.2-3B-Instruct",
                 use_quantization=True,
                 data_dir='data'):
        """
        Initialize the agentic orchestrator with all agents

        Args:
            model_name: LLaMA model to use
            use_quantization: Whether to use 4-bit quantization
            data_dir: Directory containing auxiliary data
        """
        print("="*80)
        print("INITIALIZING AGENTIC FRAUD DETECTION SYSTEM")
        print("="*80)

        # Initialize all agents
        print("\n[1/4] Initializing Alerting Agent...")
        self.alerting_agent = AlertingAgent(model_name, use_quantization)

        print("\n[2/4] Initializing Monitoring Agent...")
        self.monitoring_agent = MonitoringAgent(model_name, use_quantization)

        print("\n[3/4] Initializing Investigator Agent...")
        self.investigator_agent = InvestigatorAgent(model_name, use_quantization, data_dir)

        print("\n[4/5] Initializing Report Generator...")
        self.report_generator = ReportGenerator()

        print("\n[5/5] Initializing Word Document Generators...")
        self.word_report_generator = WordReportGenerator(bank_name="Saudi National Bank")
        self.word_batch_generator = WordBatchReportGenerator(bank_name="Saudi National Bank")

        print("\n" + "="*80)
        print("ALL AGENTS INITIALIZED SUCCESSFULLY")
        print("="*80 + "\n")

    def process_transaction(self, transaction: Dict[str, Any], generate_reports: bool = True) -> Dict[str, Any]:
        """
        Process a single transfer through the complete agentic workflow

        Workflow:
        1. Alerting Agent: Classify transfer with explainability
        2. Monitoring Agent: Review classification and decide action
        3. Investigator Agent: Deep investigation if case created
        4. Report Generator: Generate explainable reports

        Args:
            transaction: Transfer data from SAS system
            generate_reports: Whether to generate text reports

        Returns:
            Complete processing results with all agent outputs
        """
        print(f"\n{'='*80}")
        print(f"PROCESSING TRANSFER: {transaction['transaction_id']}")
        print(f"{'='*80}")

        results = {
            'transaction': transaction,
            'workflow_steps': []
        }

        # Step 1: Alerting Agent Classification
        print("\n[STEP 1] Alerting Agent - Initial Classification")
        print("─"*80)
        classification = self.alerting_agent.classify_transaction(transaction)
        results['classification'] = classification
        results['workflow_steps'].append('alerting_agent')

        print(f"Classification: {classification['classification']}")
        print(f"Confidence: {classification['confidence']:.2%}")
        print(f"Risk Factors: {len(classification['risk_factors'])}")

        # Generate initial classification report
        if generate_reports:
            report = self.report_generator.generate_classification_report(transaction, classification)
            results['classification_report'] = report

        # Step 2: Monitoring Agent Review
        print("\n[STEP 2] Monitoring Agent - Case Review")
        print("─"*80)
        monitoring_review = self.monitoring_agent.review_classification(classification, transaction)
        results['monitoring_review'] = monitoring_review
        results['workflow_steps'].append('monitoring_agent')

        print(f"Action: {monitoring_review['action']}")

        # Step 3: Investigation if case created
        if monitoring_review['action'] in ['DISAGREE_CREATE_CASE', 'REQUEST_MORE_INFO']:
            print(f"Case ID: {monitoring_review.get('case_id', 'N/A')}")
            print(f"Priority: {monitoring_review.get('case_priority', 'N/A')}")

            print("\n[STEP 3] Investigator Agent - Deep Investigation")
            print("─"*80)

            investigation = self.investigator_agent.investigate_case(
                monitoring_review,
                transaction,
                classification
            )
            results['investigation'] = investigation
            results['workflow_steps'].append('investigator_agent')

            print(f"Final Status: {investigation['case_status']}")
            print(f"Classification: {investigation['final_classification']}")
            print(f"Confidence: {investigation['confidence']:.2%}")

            # Generate comprehensive investigation report
            if generate_reports:
                # Text report
                report = self.report_generator.generate_investigation_report(
                    transaction,
                    classification,
                    monitoring_review,
                    investigation
                )
                results['investigation_report'] = report

                # Word document report
                word_filename = f"Case_Report_{monitoring_review.get('case_id', 'CASE')}.docx"
                word_path = f"reports/{word_filename}"
                try:
                    self.word_report_generator.create_case_report(
                        transaction,
                        classification,
                        monitoring_review,
                        investigation,
                        word_path
                    )
                    print(f"Word report saved to: {word_path}")
                    results['word_report_path'] = word_path
                except Exception as e:
                    print(f"Warning: Could not generate Word report: {e}")

        else:
            print("Case closed without investigation.")
            results['investigation'] = None

        print(f"\n{'='*80}")
        print(f"TRANSFER PROCESSING COMPLETE")
        print(f"{'='*80}\n")

        return results

    def process_batch(self,
                     transactions_df: pd.DataFrame,
                     max_transactions: int = None,
                     generate_reports: bool = True) -> List[Dict[str, Any]]:
        """
        Process a batch of transfers from SAS system

        Args:
            transactions_df: DataFrame of transfers from SAS
            max_transactions: Maximum number to process (None = all)
            generate_reports: Whether to generate individual reports

        Returns:
            List of processing results for each transfer
        """
        if max_transactions:
            transactions_df = transactions_df.head(max_transactions)

        print(f"\n{'='*80}")
        print(f"BATCH PROCESSING: {len(transactions_df)} TRANSFERS")
        print(f"{'='*80}\n")

        all_results = []

        for idx, row in transactions_df.iterrows():
            transaction = row.to_dict()

            try:
                result = self.process_transaction(transaction, generate_reports=False)
                all_results.append(result)

                # Print summary for each transaction
                classification = result['classification']['classification']
                print(f"✓ {transaction['transaction_id']}: {classification}")

            except Exception as e:
                print(f"✗ {transaction['transaction_id']}: ERROR - {str(e)}")
                all_results.append({
                    'transaction': transaction,
                    'error': str(e)
                })

        # Generate summary report
        if generate_reports:
            summary_data = []
            for result in all_results:
                if 'classification' in result:
                    summary_data.append({
                        'transaction_id': result['transaction']['transaction_id'],
                        'classification': result['classification']['classification'],
                        'amount': result['transaction']['amount'],
                        'ml_fraud_score': result['transaction']['ml_fraud_score'],
                        'risk_factors': result['classification']['risk_factors']
                    })

            # Text summary report
            summary_report = self.report_generator.generate_summary_report(summary_data)
            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            self.report_generator.save_report(
                summary_report,
                f"batch_summary_{timestamp}.txt"
            )

            # Word batch report
            try:
                stats = self.get_statistics(all_results)
                word_batch_path = f"reports/Batch_Report_{timestamp}.docx"
                self.word_batch_generator.create_batch_report(
                    all_results,
                    stats,
                    word_batch_path
                )
                print(f"Word batch report saved to: {word_batch_path}")
            except Exception as e:
                print(f"Warning: Could not generate Word batch report: {e}")

            # Closed cases report
            try:
                closed_cases_path = f"reports/Closed_Cases_Report_{timestamp}.docx"
                self.word_batch_generator.create_closed_cases_report(
                    all_results,
                    closed_cases_path
                )
                print(f"Closed cases report saved to: {closed_cases_path}")
            except Exception as e:
                print(f"Warning: Could not generate closed cases report: {e}")

        print(f"\n{'='*80}")
        print(f"BATCH PROCESSING COMPLETE")
        print(f"Total Processed: {len(all_results)}")
        print(f"{'='*80}\n")

        return all_results

    def get_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics from batch processing results"""

        stats = {
            'total': len(results),
            'flagged': 0,
            'investigate': 0,
            'non_fraud': 0,
            'cases_created': 0,
            'confirmed_fraud': 0,
            'avg_ml_score': 0
        }

        ml_scores = []

        for result in results:
            if result is None or 'error' in result:
                continue

            if 'classification' not in result:
                continue

            classification = result['classification']['classification']
            if classification == 'FLAGGED':
                stats['flagged'] += 1
            elif classification == 'INVESTIGATE':
                stats['investigate'] += 1
            elif classification == 'NON_FRAUD':
                stats['non_fraud'] += 1

            monitoring_review = result.get('monitoring_review')
            if monitoring_review and monitoring_review.get('case_id'):
                stats['cases_created'] += 1

            investigation = result.get('investigation')
            if investigation and investigation.get('case_status') == 'CONFIRMED_FRAUD':
                stats['confirmed_fraud'] += 1

            if 'transaction' in result and result['transaction']:
                ml_scores.append(result['transaction']['ml_fraud_score'])

        if ml_scores:
            stats['avg_ml_score'] = sum(ml_scores) / len(ml_scores)

        return stats


if __name__ == "__main__":
    print("Testing Agentic Orchestrator...")

    # Initialize orchestrator
    orchestrator = AgenticOrchestrator(use_quantization=True, data_dir='data')

    # Sample high-risk transaction
    sample_transaction = {
        'transaction_id': 'TXN_00000001',
        'customer_id': 'CUST_000123',
        'timestamp': '2025-10-02 03:47:12',
        'amount': 15234.50,
        'currency': 'USD',
        'merchant_name': 'Crypto Exchange Ltd',
        'merchant_country': 'Russia',
        'merchant_category': 'Crypto Exchange',
        'transaction_type': 'Wire Transfer',
        'card_present': False,
        'ml_fraud_score': 0.87,
        'velocity_flag': True,
        'amount_anomaly': True,
        'geo_anomaly': True
    }

    # Process single transaction
    result = orchestrator.process_transaction(sample_transaction)

    print("\n=== FINAL RESULT ===")
    print(f"Workflow Steps: {' → '.join(result['workflow_steps'])}")
    if result.get('investigation'):
        print(f"Final Status: {result['investigation']['case_status']}")
