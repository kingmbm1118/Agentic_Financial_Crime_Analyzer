"""
Explainable Report Generator
Creates comprehensive, human-readable reports for case management team
"""
from typing import Dict, Any, List
from datetime import datetime
import json


class ReportGenerator:
    """Generate explainable reports for fraud analysis"""

    def __init__(self, use_ascii=None):
        self.report_template_version = "1.0"

        # Auto-detect Windows for ASCII mode
        if use_ascii is None:
            import sys
            import platform
            use_ascii = platform.system() == 'Windows'

        # Use ASCII-safe characters for Windows compatibility
        if use_ascii:
            self.line_double = '=' * 80
            self.line_single = '-' * 80
            self.check_mark = '[OK]'
            self.x_mark = '[X]'
            self.warning_mark = '[!]'
        else:
            self.line_double = '═' * 80
            self.line_single = '─' * 80
            self.check_mark = '✓'
            self.x_mark = '✗'
            self.warning_mark = '⚠'

    def generate_classification_report(self,
                                      transaction: Dict[str, Any],
                                      classification: Dict[str, Any]) -> str:
        """Generate initial classification report"""

        report = f"""
{self.line_double}
FRAUD DETECTION ALERT - INITIAL CLASSIFICATION REPORT
{self.line_double}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Report Type: Initial Alert Classification

TRANSFER INFORMATION
{self.line_single}
Transaction ID    : {transaction['transaction_id']}
Customer ID       : {transaction['customer_id']}
Timestamp         : {transaction['timestamp']}
Amount            : {transaction['amount']:,.2f} {transaction['currency']}
Beneficiary       : {transaction.get('beneficiary_name', transaction.get('merchant_name', 'N/A'))}
Beneficiary Bank  : {transaction.get('beneficiary_bank', 'N/A')}
Beneficiary Country: {transaction.get('beneficiary_country', transaction.get('merchant_country', 'N/A'))}
Transfer Type     : {transaction.get('transfer_type', transaction.get('transaction_type', 'N/A'))}
Transfer Purpose  : {transaction.get('transfer_purpose', 'N/A')}

MACHINE LEARNING ANALYSIS
{self.line_single}
ML Fraud Score    : {transaction['ml_fraud_score']:.3f} (0.000 = Low Risk, 1.000 = High Risk)
Velocity Flag     : {f'{self.warning_mark} TRIGGERED' if transaction['velocity_flag'] else f'{self.check_mark} Normal'}
Amount Anomaly    : {f'{self.warning_mark} DETECTED' if transaction['amount_anomaly'] else f'{self.check_mark} Normal'}
Geographic Anomaly: {f'{self.warning_mark} DETECTED' if transaction['geo_anomaly'] else f'{self.check_mark} Normal'}

EXPLAINABLE AI CLASSIFICATION
{self.line_single}
Classification    : {classification['classification']}
Confidence Level  : {classification['confidence']:.2%}

RISK FACTORS IDENTIFIED:
"""
        if classification['risk_factors']:
            for i, factor in enumerate(classification['risk_factors'], 1):
                report += f"  {i}. {factor}\n"
        else:
            report += "  None identified\n"

        report += f"""
REASONING & EXPLANATION:
{self.line_single}
{classification['reasoning']}

RECOMMENDATION:
{self.line_single}
{classification['recommendation']}

{self.line_double}
END OF INITIAL CLASSIFICATION REPORT
{self.line_double}
"""
        return report

    def generate_investigation_report(self,
                                     transaction: Dict[str, Any],
                                     classification: Dict[str, Any],
                                     monitoring_review: Dict[str, Any],
                                     investigation: Dict[str, Any]) -> str:
        """Generate comprehensive investigation report"""

        report = f"""
{self.line_double}
COMPREHENSIVE FRAUD INVESTIGATION REPORT
{self.line_double}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Case ID: {monitoring_review.get('case_id', 'N/A')}
Priority: {monitoring_review.get('case_priority', 'N/A')}

EXECUTIVE SUMMARY
{self.line_single}
Final Status         : {investigation['case_status']}
Final Classification : {investigation['final_classification']}
Confidence Level     : {investigation['confidence']:.2%}

{investigation.get('investigator_notes', 'No additional notes')}

TRANSFER DETAILS
{self.line_single}
Transaction ID    : {transaction['transaction_id']}
Customer ID       : {transaction['customer_id']}
Timestamp         : {transaction['timestamp']}
Amount            : {transaction['amount']:,.2f} {transaction['currency']}
Beneficiary       : {transaction.get('beneficiary_name', transaction.get('merchant_name', 'N/A'))}
Beneficiary Bank  : {transaction.get('beneficiary_bank', 'N/A')}
Beneficiary Country: {transaction.get('beneficiary_country', transaction.get('merchant_country', 'N/A'))}
Transfer Type     : {transaction.get('transfer_type', transaction.get('transaction_type', 'N/A'))}
Transfer Purpose  : {transaction.get('transfer_purpose', 'N/A')}
ML Fraud Score    : {transaction['ml_fraud_score']:.3f}

INVESTIGATION WORKFLOW
{self.line_single}
1. Initial Alert Classification
   └─ Classification: {classification['classification']}
   └─ Confidence: {classification['confidence']:.2%}
   └─ Risk Factors: {len(classification.get('risk_factors', []))} identified

2. Monitoring Team Review
   └─ Action: {monitoring_review['action']}
   └─ Case Created: {monitoring_review.get('case_id', 'N/A')}
   └─ Priority: {monitoring_review.get('case_priority', 'N/A')}

3. Deep Investigation
   └─ Data Sources Analyzed: {len(investigation['data_sources_checked'])}
   └─ Behavioral Anomalies: {len(investigation['behavioral_analysis']['behavioral_anomalies'])}

DATA SOURCES ANALYZED
{self.line_single}
"""
        for source in investigation['data_sources_checked']:
            report += f"{self.check_mark} {source.replace('_', ' ').title()}\n"

        report += f"""
CUSTOMER PROFILE ANALYSIS
{self.line_single}
{investigation['customer_profile_summary']}

LOGIN ACTIVITY ANALYSIS
{self.line_single}
{investigation['login_summary']}

DEVICE FINGERPRINT ANALYSIS
{self.line_single}
{investigation['device_summary']}

BEHAVIORAL ANALYSIS
{self.line_single}
Profile Risk: {investigation['behavioral_analysis']['profile_risk']}
Login Risk  : {investigation['behavioral_analysis']['login_risk']}
Device Risk : {investigation['behavioral_analysis']['device_risk']}

Anomalies Detected:
"""
        if investigation['behavioral_analysis']['behavioral_anomalies']:
            for i, anomaly in enumerate(investigation['behavioral_analysis']['behavioral_anomalies'], 1):
                report += f"  {i}. {anomaly}\n"
        else:
            report += "  None detected\n"

        report += f"""
DETAILED INVESTIGATION SUMMARY
{self.line_single}
{investigation['investigation_summary']}

RECOMMENDED ACTIONS
{self.line_single}
"""
        for i, action in enumerate(investigation['recommended_actions'], 1):
            report += f"  {i}. {action}\n"

        report += f"""
{self.line_double}
END OF COMPREHENSIVE INVESTIGATION REPORT
{self.line_double}

This report was generated using explainable AI to provide transparency in the
fraud detection decision-making process. All classifications and recommendations
are based on multiple data sources and risk factors as documented above.

For questions or additional investigation, contact the Fraud Investigation Team.
"""
        return report

    def generate_summary_report(self, cases: List[Dict[str, Any]]) -> str:
        """Generate summary report for multiple cases"""

        total_cases = len(cases)
        flagged = sum(1 for c in cases if c.get('classification') == 'FLAGGED')
        investigate = sum(1 for c in cases if c.get('classification') == 'INVESTIGATE')
        non_fraud = sum(1 for c in cases if c.get('classification') == 'NON_FRAUD')

        report = f"""
{self.line_double}
FRAUD DETECTION BATCH SUMMARY REPORT
{self.line_double}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Transactions Analyzed: {total_cases}

CLASSIFICATION BREAKDOWN
{self.line_single}
Flagged (High Risk)        : {flagged:3d} ({flagged/total_cases*100:5.1f}%)
Needs Investigation        : {investigate:3d} ({investigate/total_cases*100:5.1f}%)
Non-Fraud (Low Risk)       : {non_fraud:3d} ({non_fraud/total_cases*100:5.1f}%)

HIGH PRIORITY CASES REQUIRING IMMEDIATE ATTENTION
{self.line_single}
"""
        high_priority = [c for c in cases if c.get('classification') == 'FLAGGED'][:10]

        if high_priority:
            for i, case in enumerate(high_priority, 1):
                report += f"\n{i}. Transaction ID: {case.get('transaction_id', 'N/A')}\n"
                report += f"   Amount: ${case.get('amount', 0):,.2f}\n"
                report += f"   ML Score: {case.get('ml_fraud_score', 0):.3f}\n"
                report += f"   Risk Factors: {len(case.get('risk_factors', []))}\n"
        else:
            report += "\nNo high priority cases detected.\n"

        report += f"""
{self.line_double}
END OF SUMMARY REPORT
{self.line_double}
"""
        return report

    def save_report(self, report: str, filename: str, output_dir: str = 'reports'):
        """Save report to file"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        filepath = f"{output_dir}/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"Report saved to: {filepath}")
        return filepath

    def export_to_json(self, data: Dict[str, Any], filename: str, output_dir: str = 'reports'):
        """Export structured data to JSON for system integration"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        filepath = f"{output_dir}/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"JSON export saved to: {filepath}")
        return filepath


if __name__ == "__main__":
    print("Testing Report Generator...")

    generator = ReportGenerator()

    # Sample data
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
        'ml_fraud_score': 0.87,
        'velocity_flag': True,
        'amount_anomaly': True,
        'geo_anomaly': True
    }

    sample_classification = {
        'transaction_id': 'TXN_00000001',
        'classification': 'FLAGGED',
        'confidence': 0.85,
        'reasoning': 'High ML fraud score combined with suspicious merchant location and unusual transaction patterns.',
        'risk_factors': [
            'High ML fraud score: 0.87',
            'Suspicious location: Russia',
            'Unusual transaction amount',
            'Velocity flag triggered'
        ],
        'recommendation': 'Immediate investigation required. Consider account freeze.'
    }

    # Generate classification report
    print("\n=== Generating Classification Report ===")
    report = generator.generate_classification_report(sample_transaction, sample_classification)
    print(report)

    # Save report
    generator.save_report(report, "sample_classification_report.txt")
