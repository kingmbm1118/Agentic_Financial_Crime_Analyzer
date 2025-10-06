"""
Monitoring Agent for Case Review
Reviews LLM classifications and makes recommendations
"""
from typing import Dict, Any, List
from llm_agent import LLaMAAgent


class MonitoringAgent(LLaMAAgent):
    """Agent for monitoring team to review and validate classifications"""

    def __init__(self, model_name="meta-llama/Llama-3.2-3B-Instruct", use_quantization=True):
        super().__init__(model_name, use_quantization)
        self.agent_type = "Monitoring Agent"

    def review_classification(self,
                            classification_result: Dict[str, Any],
                            transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review initial classification and provide recommendation

        Returns:
            {
                'action': 'AGREE_CLOSE' | 'DISAGREE_CREATE_CASE' | 'REQUEST_MORE_INFO',
                'reasoning': str,
                'case_priority': 'LOW' | 'MEDIUM' | 'HIGH',
                'additional_checks': List[str]
            }
        """

        # Auto-close obvious non-fraud cases
        if classification_result['classification'] == 'NON_FRAUD' and classification_result['confidence'] > 0.85:
            return {
                'action': 'AGREE_CLOSE',
                'reasoning': 'Low risk transaction with high confidence. No further action needed.',
                'case_priority': None,
                'additional_checks': [],
                'case_id': None
            }

        # Create case for flagged transactions
        if classification_result['classification'] == 'FLAGGED':
            case_id = f"CASE_{classification_result['transaction_id'].replace('TXN_', '')}"
            return {
                'action': 'DISAGREE_CREATE_CASE',
                'reasoning': f"High risk indicators present. Creating case for investigator review.",
                'case_priority': 'HIGH' if classification_result['confidence'] > 0.80 else 'MEDIUM',
                'additional_checks': ['customer_profile', 'login_history', 'device_fingerprint'],
                'case_id': case_id
            }

        # Request more analysis for investigate cases
        if classification_result['classification'] == 'INVESTIGATE':
            prompt = self._build_review_prompt(classification_result, transaction)
            response = self.generate_response(prompt, max_length=300)

            # Decide based on detailed review
            if 'create case' in response.lower() or 'investigate' in response.lower():
                case_id = f"CASE_{classification_result['transaction_id'].replace('TXN_', '')}"
                return {
                    'action': 'DISAGREE_CREATE_CASE',
                    'reasoning': response.strip(),
                    'case_priority': 'MEDIUM',
                    'additional_checks': ['login_history', 'transaction_history'],
                    'case_id': case_id
                }
            else:
                return {
                    'action': 'AGREE_CLOSE',
                    'reasoning': response.strip(),
                    'case_priority': 'LOW',
                    'additional_checks': [],
                    'case_id': None
                }

        # Create case for REQUEST_MORE_INFO as well
        case_id = f"CASE_{classification_result['transaction_id'].replace('TXN_', '')}"
        return {
            'action': 'REQUEST_MORE_INFO',
            'reasoning': 'Insufficient information for decision - requires further investigation',
            'case_priority': 'LOW',
            'additional_checks': ['customer_profile'],
            'case_id': case_id
        }

    def _build_review_prompt(self, classification: Dict[str, Any], transaction: Dict[str, Any]) -> str:
        """Build prompt for monitoring review - OPTIMIZED"""
        # Shorter prompt for speed
        prompt = f"""Review Alert:
Classification: {classification['classification']} ({classification['confidence']:.0%})
Amount: {transaction['amount']} {transaction['currency']}
ML Score: {transaction['ml_fraud_score']}

Decision (AGREE_CLOSE/CREATE_CASE/REQUEST_MORE_INFO) and why in 1 sentence:"""
        return prompt


if __name__ == "__main__":
    from llm_agent import AlertingAgent

    print("Testing Monitoring Agent...")

    # Initialize agents
    alerting_agent = AlertingAgent(use_quantization=True)
    monitoring_agent = MonitoringAgent(use_quantization=True)

    # Sample transaction
    sample_transaction = {
        'transaction_id': 'TXN_00000042',
        'customer_id': 'CUST_000123',
        'timestamp': '2025-10-02 14:23:11',
        'amount': 1234.50,
        'currency': 'USD',
        'merchant_name': 'Amazon.com',
        'merchant_country': 'USA',
        'merchant_category': 'Online Retail',
        'transaction_type': 'Purchase',
        'ml_fraud_score': 0.52,
        'velocity_flag': False,
        'amount_anomaly': False,
        'geo_anomaly': False
    }

    # Classify transaction
    print("\n=== Initial Classification ===")
    classification = alerting_agent.classify_transaction(sample_transaction)
    print(f"Classification: {classification['classification']}")
    print(f"Confidence: {classification['confidence']}")

    # Review classification
    print("\n=== Monitoring Review ===")
    review = monitoring_agent.review_classification(classification, sample_transaction)
    print(f"Action: {review['action']}")
    print(f"Reasoning: {review['reasoning']}")
    if review['case_id']:
        print(f"Case ID: {review['case_id']}")
        print(f"Priority: {review['case_priority']}")
