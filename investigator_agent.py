"""
Investigator Agent for Deep Analysis
Accesses multiple data sources for comprehensive fraud investigation
"""
import pandas as pd
from typing import Dict, Any, List, Optional
from llm_agent import LLaMAAgent


class InvestigatorAgent(LLaMAAgent):
    """Agent for deep investigation using multiple data sources"""

    def __init__(self,
                 model_name="meta-llama/Llama-3.2-3B-Instruct",
                 use_quantization=True,
                 data_dir='data'):
        super().__init__(model_name, use_quantization)
        self.agent_type = "Investigator Agent"
        self.data_dir = data_dir

        # Load auxiliary data sources
        self._load_data_sources()

    def _load_data_sources(self):
        """Load all auxiliary data sources"""
        try:
            self.login_data = pd.read_csv(f'{self.data_dir}/login_data.csv')
            self.customer_profiles = pd.read_csv(f'{self.data_dir}/customer_profiles.csv')
            self.device_data = pd.read_csv(f'{self.data_dir}/device_fingerprints.csv')
            print(f"Loaded auxiliary data sources from {self.data_dir}/")
        except Exception as e:
            print(f"Warning: Could not load data sources: {e}")
            self.login_data = pd.DataFrame()
            self.customer_profiles = pd.DataFrame()
            self.device_data = pd.DataFrame()

    def investigate_case(self,
                        case: Dict[str, Any],
                        transaction: Dict[str, Any],
                        classification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform deep investigation using multiple data sources

        Returns comprehensive investigation report
        """
        print(f"\n=== Starting Investigation for {case['case_id']} ===")

        # Gather data from all sources
        customer_id = transaction['customer_id']

        customer_profile = self._get_customer_profile(customer_id)
        login_history = self._get_login_history(customer_id)
        device_info = self._get_device_info(customer_id)

        # Analyze patterns
        behavioral_analysis = self._analyze_behavior(
            transaction, customer_profile, login_history, device_info
        )

        # Generate comprehensive analysis using LLM
        investigation_report = self._generate_investigation_report(
            transaction,
            classification,
            customer_profile,
            login_history,
            device_info,
            behavioral_analysis
        )

        return investigation_report

    def _get_customer_profile(self, customer_id: str) -> Dict[str, Any]:
        """Retrieve customer profile data"""
        if self.customer_profiles.empty:
            return {}

        profile = self.customer_profiles[
            self.customer_profiles['customer_id'] == customer_id
        ]

        if profile.empty:
            return {}

        return profile.iloc[0].to_dict()

    def _get_login_history(self, customer_id: str) -> List[Dict[str, Any]]:
        """Retrieve recent login history"""
        if self.login_data.empty:
            return []

        logins = self.login_data[
            self.login_data['customer_id'] == customer_id
        ].sort_values('login_timestamp', ascending=False).head(10)

        return logins.to_dict('records')

    def _get_device_info(self, customer_id: str) -> List[Dict[str, Any]]:
        """Retrieve device fingerprint data"""
        if self.device_data.empty:
            return []

        devices = self.device_data[
            self.device_data['customer_id'] == customer_id
        ]

        return devices.to_dict('records')

    def _analyze_behavior(self,
                         transaction: Dict[str, Any],
                         profile: Dict[str, Any],
                         logins: List[Dict[str, Any]],
                         devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze behavioral patterns"""

        analysis = {
            'profile_risk': 'UNKNOWN',
            'login_risk': 'UNKNOWN',
            'device_risk': 'UNKNOWN',
            'behavioral_anomalies': []
        }

        # Profile analysis
        if profile:
            if profile.get('customer_risk_level') == 'High':
                analysis['profile_risk'] = 'HIGH'
                analysis['behavioral_anomalies'].append('Customer flagged as high risk')

            if profile.get('previous_fraud_cases', 0) > 0:
                analysis['behavioral_anomalies'].append(
                    f"Previous fraud cases: {profile['previous_fraud_cases']}"
                )

            if not profile.get('kyc_verified', True):
                analysis['behavioral_anomalies'].append('KYC not verified')

            # Transaction amount comparison
            avg_amount = profile.get('avg_transaction_amount', 0)
            if avg_amount > 0 and transaction['amount'] > avg_amount * 3:
                analysis['behavioral_anomalies'].append(
                    f"Transaction amount {transaction['amount']} is {round(transaction['amount']/avg_amount, 1)}x above average"
                )

        # Login analysis
        if logins:
            countries = set([login.get('country', 'Unknown') for login in logins])

            if len(countries) > 3:
                analysis['login_risk'] = 'HIGH'
                analysis['behavioral_anomalies'].append(
                    f'Multiple login countries: {", ".join(list(countries)[:5])}'
                )

            failed_logins = sum(1 for login in logins if not login.get('login_successful', True))
            if failed_logins > 2:
                analysis['behavioral_anomalies'].append(
                    f'{failed_logins} failed login attempts detected'
                )

            # Check for logins without 2FA
            no_2fa = sum(1 for login in logins if not login.get('two_factor_used', False))
            if no_2fa > len(logins) * 0.5:
                analysis['behavioral_anomalies'].append(
                    'Majority of logins without 2FA'
                )

        # Device analysis
        if devices:
            suspicious_devices = [d for d in devices if d.get('suspicious_behavior', False)]
            if suspicious_devices:
                analysis['device_risk'] = 'HIGH'
                analysis['behavioral_anomalies'].append(
                    f'{len(suspicious_devices)} suspicious devices detected'
                )

            untrusted_devices = [d for d in devices if not d.get('is_trusted', True)]
            if untrusted_devices:
                analysis['behavioral_anomalies'].append(
                    f'{len(untrusted_devices)} untrusted devices'
                )

        return analysis

    def _generate_investigation_report(self,
                                      transaction: Dict[str, Any],
                                      classification: Dict[str, Any],
                                      profile: Dict[str, Any],
                                      logins: List[Dict[str, Any]],
                                      devices: List[Dict[str, Any]],
                                      behavioral_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive investigation report using LLM"""

        prompt = self._build_investigation_prompt(
            transaction, classification, profile, logins, devices, behavioral_analysis
        )

        llm_analysis = self.generate_response(prompt, max_length=600)

        # Determine final decision
        final_decision = self._determine_final_decision(
            transaction, behavioral_analysis, llm_analysis
        )

        report = {
            'case_status': final_decision['status'],
            'final_classification': final_decision['classification'],
            'confidence': final_decision['confidence'],
            'investigation_summary': llm_analysis,
            'data_sources_checked': ['transaction', 'customer_profile', 'login_history', 'device_fingerprints'],
            'behavioral_analysis': behavioral_analysis,
            'customer_profile_summary': self._summarize_profile(profile),
            'login_summary': self._summarize_logins(logins),
            'device_summary': self._summarize_devices(devices),
            'recommended_actions': final_decision['actions'],
            'investigator_notes': final_decision['notes']
        }

        return report

    def _build_investigation_prompt(self,
                                   transaction: Dict[str, Any],
                                   classification: Dict[str, Any],
                                   profile: Dict[str, Any],
                                   logins: List[Dict[str, Any]],
                                   devices: List[Dict[str, Any]],
                                   behavioral_analysis: Dict[str, Any]) -> str:
        """Build investigation prompt - OPTIMIZED SHORT VERSION"""

        # Shorter prompt = much faster inference
        anomalies = behavioral_analysis.get('behavioral_anomalies', [])
        anomaly_text = ', '.join(anomalies[:3]) if anomalies else 'None'

        prompt = f"""Deep Analysis:
Amount: {transaction['amount']} {transaction['currency']}, ML: {transaction['ml_fraud_score']}
Customer: {profile.get('account_age_days', 0)}d old, KYC: {profile.get('kyc_verified', False)}, Prev Fraud: {profile.get('previous_fraud_cases', 0)}
Logins: {len(logins)} recent, Countries: {len(set([l.get('country', 'Unknown') for l in logins]))}
Anomalies: {anomaly_text}

Risk (HIGH/MEDIUM/LOW) and why in 2 sentences:"""

        return prompt

    def _determine_final_decision(self,
                                 transaction: Dict[str, Any],
                                 behavioral_analysis: Dict[str, Any],
                                 llm_analysis: str) -> Dict[str, Any]:
        """Determine final decision based on all evidence"""

        # Count risk factors
        risk_score = 0

        if transaction['ml_fraud_score'] > 0.75:
            risk_score += 3
        elif transaction['ml_fraud_score'] > 0.50:
            risk_score += 2

        if len(behavioral_analysis['behavioral_anomalies']) > 3:
            risk_score += 2
        elif len(behavioral_analysis['behavioral_anomalies']) > 1:
            risk_score += 1

        if 'HIGH' in llm_analysis.upper() or 'FRAUD' in llm_analysis.upper():
            risk_score += 2

        # Determine classification
        if risk_score >= 5:
            status = 'CONFIRMED_FRAUD'
            classification = 'FRAUD'
            confidence = 0.90
            actions = [
                'Block transaction immediately',
                'Freeze customer account',
                'Contact customer for verification',
                'File fraud report',
                'Initiate chargeback if applicable'
            ]
            notes = 'Multiple strong fraud indicators present. Immediate action required.'
        elif risk_score >= 3:
            status = 'SUSPECTED_FRAUD'
            classification = 'SUSPICIOUS'
            confidence = 0.70
            actions = [
                'Place temporary hold on account',
                'Request additional customer verification',
                'Monitor account closely for 48 hours',
                'Review with fraud specialist'
            ]
            notes = 'Significant suspicious activity. Enhanced monitoring recommended.'
        else:
            status = 'NO_FRAUD_DETECTED'
            classification = 'LEGITIMATE'
            confidence = 0.85
            actions = [
                'Clear transaction',
                'Continue standard monitoring',
                'Update customer risk profile if needed'
            ]
            notes = 'Investigation shows low fraud risk. Transaction appears legitimate.'

        return {
            'status': status,
            'classification': classification,
            'confidence': confidence,
            'actions': actions,
            'notes': notes
        }

    def _summarize_profile(self, profile: Dict[str, Any]) -> str:
        """Summarize customer profile"""
        if not profile:
            return "No profile data available"

        return (f"Customer since {profile.get('customer_since', 'N/A')}, "
                f"Risk Level: {profile.get('customer_risk_level', 'N/A')}, "
                f"KYC: {'Verified' if profile.get('kyc_verified') else 'Not Verified'}")

    def _summarize_logins(self, logins: List[Dict[str, Any]]) -> str:
        """Summarize login history"""
        if not logins:
            return "No recent login data"

        countries = set([login.get('country', 'Unknown') for login in logins])
        return f"{len(logins)} recent logins from {len(countries)} countries: {', '.join(list(countries)[:3])}"

    def _summarize_devices(self, devices: List[Dict[str, Any]]) -> str:
        """Summarize device information"""
        if not devices:
            return "No device data available"

        trusted = len([d for d in devices if d.get('is_trusted', False)])
        return f"{len(devices)} devices registered, {trusted} trusted"


if __name__ == "__main__":
    print("Testing Investigator Agent...")

    # Initialize agent
    investigator = InvestigatorAgent(use_quantization=True, data_dir='data')

    # Sample case
    sample_case = {
        'case_id': 'CASE_00000001',
        'priority': 'HIGH'
    }

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
        'classification': 'FLAGGED',
        'confidence': 0.85,
        'risk_factors': ['High ML score', 'Unusual location', 'Large amount']
    }

    # Perform investigation
    print("\nInvestigating case...")
    report = investigator.investigate_case(sample_case, sample_transaction, sample_classification)

    print(f"\n=== Investigation Report ===")
    print(f"Status: {report['case_status']}")
    print(f"Classification: {report['final_classification']}")
    print(f"Confidence: {report['confidence']}")
    print(f"\nRecommended Actions:")
    for action in report['recommended_actions']:
        print(f"  - {action}")
