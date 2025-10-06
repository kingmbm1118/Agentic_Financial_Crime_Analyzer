"""
LLaMA-based Agent for Explainable Fraud Detection
Uses quantized LLaMA model via Transformers
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import json
import os
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Hugging Face token from environment
HF_TOKEN = os.getenv('HF_TOKEN', None)


class LLaMAAgent:
    """Base LLaMA agent with quantization support"""

    def __init__(self, model_name="meta-llama/Llama-3.2-3B-Instruct", use_quantization=True):
        """
        Initialize LLaMA agent with quantized model

        Args:
            model_name: HuggingFace model identifier
            use_quantization: Use 4-bit quantization to reduce memory
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"Loading LLaMA model: {model_name}")
        print(f"Device: {self.device}")

        # Configure quantization if enabled
        if use_quantization and self.device == "cuda":
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                llm_int8_enable_fp32_cpu_offload=False  # Keep everything on GPU
            )
            print("Using 4-bit quantization (optimized)")
        else:
            quantization_config = None
            print("Quantization disabled (CPU mode or disabled)")

        try:
            # Local model cache directory
            local_model_dir = f"./models/{model_name.replace('/', '_')}"

            # Check if model exists locally
            if os.path.exists(local_model_dir):
                print(f"Loading model from local cache: {local_model_dir}")
                self.tokenizer = AutoTokenizer.from_pretrained(local_model_dir)
                self.model = AutoModelForCausalLM.from_pretrained(
                    local_model_dir,
                    device_map="auto" if self.device == "cuda" else None,
                    low_cpu_mem_usage=True,
                    attn_implementation="sdpa"
                )
            else:
                # Download from HuggingFace (first time only)
                print(f"Downloading model from HuggingFace (first time setup)...")
                if HF_TOKEN:
                    print(f"Using HF token from .env file")
                    os.environ['HF_TOKEN'] = HF_TOKEN
                else:
                    print("No HF token found in .env file, trying cached credentials")

                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    token=HF_TOKEN if HF_TOKEN else None
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    token=HF_TOKEN if HF_TOKEN else None,
                    quantization_config=quantization_config,
                    device_map="auto" if self.device == "cuda" else None,
                    dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    low_cpu_mem_usage=True,
                    attn_implementation="sdpa"
                )

                # Save model locally for offline use
                print(f"Saving model locally to: {local_model_dir}")
                os.makedirs(local_model_dir, exist_ok=True)
                self.tokenizer.save_pretrained(local_model_dir)
                self.model.save_pretrained(local_model_dir)
                print("Model saved successfully for offline use!")

            if self.device == "cpu":
                self.model = self.model.to(self.device)

            print("Model loaded successfully!")

        except Exception as e:
            print(f"Error loading model: {e}")
            print("Falling back to mock mode for demonstration")
            self.model = None
            self.tokenizer = None

    def generate_response(self, prompt: str, max_length: int = 150, temperature: float = 0.7) -> str:
        """Generate response from LLaMA model - OPTIMIZED FOR SPEED"""
        if self.model is None:
            # Mock mode for demo when model can't be loaded
            return self._mock_response(prompt)

        try:
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,  # Reduced from 512 to 150
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    top_k=50,  # Speed optimization
                    repetition_penalty=1.1,  # Prevent loops
                    pad_token_id=self.tokenizer.eos_token_id,
                    use_cache=True,  # Use KV cache for speed
                    num_beams=1  # Greedy decoding for speed
                )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract only the generated part (after the prompt)
            if prompt in response:
                response = response.split(prompt)[-1].strip()

            return response

        except Exception as e:
            print(f"Error generating response: {e}")
            return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> str:
        """Mock response for demo purposes"""
        if "fraud" in prompt.lower() and "classify" in prompt.lower():
            return """Classification: FLAGGED - High Risk

Reasoning:
1. High ML fraud score (0.87) indicating suspicious pattern
2. Large transaction amount ($15,234) exceeding customer's average
3. Unusual merchant country (Russia) not matching customer's typical transaction profile
4. Transaction occurred at unusual hours (3:47 AM)
5. Velocity flag triggered - multiple transactions in short timeframe

Recommendation: FLAG for immediate investigation. High risk of fraudulent activity."""

        elif "investigate" in prompt.lower() or "analysis" in prompt.lower():
            return """Deep Analysis Results:

Risk Factors:
- Multiple login attempts from different countries within 24 hours
- New device fingerprint detected (never seen before)
- Transaction pattern deviation: 340% above customer average
- Merchant category (Crypto Exchange) flagged as high-risk
- No 2FA authentication on recent sessions

Customer Behavior:
- Account age: 45 days (relatively new)
- Previous fraud cases: 0
- Typical transaction location: USA
- Current transaction location: Russia

Conclusion: Strong indicators of account compromise. Recommend account freeze and customer contact."""

        return "Analysis in progress..."


class AlertingAgent(LLaMAAgent):
    """LLM Agent for initial alert classification with explainability"""

    def __init__(self, model_name="meta-llama/Llama-3.2-3B-Instruct", use_quantization=True):
        super().__init__(model_name, use_quantization)
        self.agent_type = "Alerting Agent"

    def classify_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify transaction and provide explainable reasoning

        Returns:
            {
                'classification': 'FLAGGED' | 'INVESTIGATE' | 'NON_FRAUD',
                'confidence': float,
                'reasoning': str,
                'risk_factors': List[str],
                'recommendation': str
            }
        """
        prompt = self._build_classification_prompt(transaction)
        response = self.generate_response(prompt, max_length=400)

        # Parse response to extract structured output
        result = self._parse_classification(response, transaction)

        return result

    def _build_classification_prompt(self, transaction: Dict[str, Any]) -> str:
        """Build prompt for transfer classification - OPTIMIZED SHORT VERSION"""
        # Shorter prompt = faster inference
        prompt = f"""Transfer Fraud Analysis:
Amount: {transaction['amount']} {transaction['currency']}
Beneficiary: {transaction.get('beneficiary_name', 'N/A')} in {transaction.get('beneficiary_country', transaction.get('merchant_country', 'N/A'))}
Transfer Type: {transaction.get('transfer_type', 'N/A')}
ML Score: {transaction['ml_fraud_score']}
Flags: Velocity={transaction['velocity_flag']}, Amount Anomaly={transaction['amount_anomaly']}, Geo={transaction['geo_anomaly']}

Classify as FLAGGED/INVESTIGATE/NON_FRAUD and explain why in 2-3 sentences:"""

        return prompt

    def _parse_classification(self, response: str, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured format"""

        # Determine classification from response
        response_upper = response.upper()
        if "FLAGGED" in response_upper or "HIGH RISK" in response_upper:
            classification = "FLAGGED"
            confidence = 0.85 if transaction['ml_fraud_score'] > 0.75 else 0.70
        elif "INVESTIGATE" in response_upper or "SUSPICIOUS" in response_upper:
            classification = "INVESTIGATE"
            confidence = 0.65
        elif "NON_FRAUD" in response_upper or "NORMAL" in response_upper or "LOW RISK" in response_upper:
            classification = "NON_FRAUD"
            confidence = 0.80
        else:
            # Fallback based on ML score
            if transaction['ml_fraud_score'] > 0.75:
                classification = "FLAGGED"
                confidence = transaction['ml_fraud_score']
            elif transaction['ml_fraud_score'] > 0.45:
                classification = "INVESTIGATE"
                confidence = transaction['ml_fraud_score']
            else:
                classification = "NON_FRAUD"
                confidence = 1 - transaction['ml_fraud_score']

        # Extract risk factors
        risk_factors = []
        if transaction['ml_fraud_score'] > 0.6:
            risk_factors.append(f"High ML fraud score: {transaction['ml_fraud_score']}")
        if transaction['velocity_flag']:
            risk_factors.append("Velocity flag triggered")
        if transaction['amount_anomaly']:
            risk_factors.append("Unusual transaction amount")
        if transaction['geo_anomaly']:
            risk_factors.append(f"Suspicious beneficiary location: {transaction.get('beneficiary_country', transaction.get('merchant_country', 'Unknown'))}")

        return {
            'transaction_id': transaction['transaction_id'],
            'classification': classification,
            'confidence': round(confidence, 2),
            'reasoning': response.strip(),
            'risk_factors': risk_factors,
            'recommendation': self._get_recommendation(classification),
            'timestamp': transaction['timestamp']
        }

    def _get_recommendation(self, classification: str) -> str:
        """Get action recommendation based on classification"""
        recommendations = {
            'FLAGGED': "Immediate investigation required. Consider account freeze and customer contact.",
            'INVESTIGATE': "Requires deeper analysis. Review customer behavior and auxiliary data sources.",
            'NON_FRAUD': "Transaction appears legitimate. Continue monitoring."
        }
        return recommendations.get(classification, "Review manually")


if __name__ == "__main__":
    # Test the agent
    print("Initializing LLaMA Alerting Agent...")
    agent = AlertingAgent(use_quantization=True)

    # Sample transaction
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

    print("\nTesting transaction classification...")
    result = agent.classify_transaction(sample_transaction)

    print(f"\n=== Classification Result ===")
    print(f"Classification: {result['classification']}")
    print(f"Confidence: {result['confidence']}")
    print(f"\nReasoning:\n{result['reasoning']}")
    print(f"\nRisk Factors:")
    for factor in result['risk_factors']:
        print(f"  - {factor}")
    print(f"\nRecommendation: {result['recommendation']}")
