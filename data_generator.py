"""
Generate dummy data for fraud detection system
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import json
import random

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)


class DataGenerator:
    """Generate dummy data for all systems"""

    def __init__(self, num_transactions=100):
        self.num_transactions = num_transactions
        self.customer_ids = [f"SA{str(i).zfill(8)}" for i in range(1, 501)]  # Saudi customer IDs

        # Saudi Arabia and common transaction countries
        self.countries = ['Saudi Arabia', 'UAE', 'Kuwait', 'Bahrain', 'Qatar', 'Oman',
                         'Egypt', 'Jordan', 'Lebanon', 'Turkey', 'India', 'Pakistan',
                         'UK', 'USA', 'Germany', 'France']

        # High-risk countries for Saudi banking (based on SAMA AML guidelines)
        self.risk_countries = ['Iran', 'Yemen', 'Syria', 'Unknown', 'North Korea', 'Nigeria']

        # Saudi cities
        self.saudi_cities = ['Riyadh', 'Jeddah', 'Mecca', 'Medina', 'Dammam', 'Khobar',
                            'Dhahran', 'Taif', 'Buraidah', 'Tabuk', 'Abha', 'Jubail']

        # Arabic names (common Saudi names)
        self.arabic_names = [
            'Mohammed Ahmed', 'Abdullah Khalid', 'Fahad Salem', 'Khalid Ibrahim',
            'Sultan Mansour', 'Faisal Omar', 'Nasser Ali', 'Saad Abdullah',
            'Turki Fahad', 'Bandar Mohammed', 'Sarah Ahmed', 'Noura Abdullah',
            'Lama Khalid', 'Maha Salem', 'Reem Ibrahim'
        ]

    def generate_sas_transfer_data(self):
        """Generate SAS system TRANSFER data with beneficiary info and ML fraud scores"""
        transfers = []

        for i in range(self.num_transactions):
            customer_id = random.choice(self.customer_ids)
            amount = round(random.uniform(500, 100000), 2)

            # Generate fraud patterns
            is_high_risk = random.random() < 0.15  # 15% high risk
            is_medium_risk = random.random() < 0.25  # 25% medium risk

            if is_high_risk:
                # High risk patterns: large amounts, suspicious countries, unusual times
                amount = round(random.uniform(10000, 100000), 2)
                fraud_score = round(random.uniform(0.75, 0.98), 3)
                beneficiary_country = random.choice(self.risk_countries)
                beneficiary_name = fake.name()  # Foreign name for high risk
            elif is_medium_risk:
                fraud_score = round(random.uniform(0.45, 0.74), 3)
                beneficiary_country = random.choice(self.countries)
                beneficiary_name = random.choice(self.arabic_names) if random.random() < 0.5 else fake.name()
            else:
                fraud_score = round(random.uniform(0.01, 0.44), 3)
                beneficiary_country = random.choice(['Saudi Arabia', 'UAE', 'Kuwait', 'Bahrain', 'Qatar'])
                beneficiary_name = random.choice(self.arabic_names)

            timestamp = datetime.now() - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            # Transfer types
            if beneficiary_country == 'Saudi Arabia':
                transfer_type = random.choice(['Local Transfer', 'SADAD', 'Instant Transfer'])
            else:
                transfer_type = random.choice(['International Wire Transfer', 'SWIFT Transfer', 'Cross-Border Transfer'])

            transfer = {
                'transaction_id': f"SA-TXN-{str(i+1).zfill(10)}",
                'customer_id': customer_id,
                'customer_name': random.choice(self.arabic_names),
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'amount': amount,
                'currency': 'SAR',  # Saudi Riyal

                # Beneficiary Information
                'beneficiary_name': beneficiary_name,
                'beneficiary_account': f"SA{random.randint(1000000000000000, 9999999999999999)}" if beneficiary_country == 'Saudi Arabia' else fake.iban(),
                'beneficiary_bank': fake.company() + ' Bank',
                'beneficiary_country': beneficiary_country,
                'beneficiary_city': random.choice(self.saudi_cities) if beneficiary_country == 'Saudi Arabia' else fake.city(),

                # Transfer Details
                'transfer_type': transfer_type,
                'transfer_purpose': random.choice([
                    'Family Support', 'Business Payment', 'Salary Transfer', 'Investment',
                    'Property Purchase', 'Education Fee', 'Medical Treatment', 'Gift',
                    'Trade Payment', 'Loan Repayment', 'Personal Savings', 'Other'
                ]),
                'transfer_channel': random.choice(['Mobile Banking', 'Internet Banking', 'Branch', 'ATM']),
                'payment_reference': f"REF-{fake.uuid4()[:8].upper()}",

                # Risk Indicators
                'ml_fraud_score': fraud_score,
                'velocity_flag': random.choice([True, False]) if fraud_score > 0.5 else False,
                'amount_anomaly': random.choice([True, False]) if fraud_score > 0.6 else False,
                'geo_anomaly': beneficiary_country in self.risk_countries,
                'sama_aml_flag': beneficiary_country in self.risk_countries or amount > 20000,  # SAMA AML threshold
                'customer_nationality': 'Saudi' if random.random() < 0.7 else 'Expatriate',
                'new_beneficiary': random.choice([True, False]) if fraud_score > 0.5 else False,
                'relationship_with_beneficiary': random.choice(['Family', 'Friend', 'Business Partner', 'Employee', 'Self', 'Other'])
            }

            transfers.append(transfer)

        return pd.DataFrame(transfers)

    def generate_login_data(self):
        """Generate login/authentication system data"""
        login_data = []

        for customer_id in self.customer_ids[:200]:  # Not all customers have recent logins
            num_logins = random.randint(1, 20)

            for _ in range(num_logins):
                timestamp = datetime.now() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23)
                )

                # Mostly Saudi-based logins
                country = random.choice(self.countries) if random.random() < 0.3 else 'Saudi Arabia'
                city = random.choice(self.saudi_cities) if country == 'Saudi Arabia' else fake.city()

                login = {
                    'customer_id': customer_id,
                    'login_timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'ip_address': fake.ipv4(),
                    'country': country,
                    'city': city,
                    'device_type': random.choice(['Mobile', 'Desktop', 'Tablet']),
                    'device_id': fake.uuid4(),
                    'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
                    'login_successful': random.choice([True, True, True, False]),  # Mostly successful
                    'two_factor_used': random.choice([True, False]),
                    'session_duration_minutes': random.randint(1, 120),
                    'login_method': random.choice(['Mobile App', 'Web Portal', 'ATM'])
                }

                login_data.append(login)

        return pd.DataFrame(login_data)

    def generate_customer_profile_data(self):
        """Generate customer profile data"""
        profiles = []

        for customer_id in self.customer_ids:
            nationality = random.choice(['Saudi', 'Saudi', 'Saudi', 'Expatriate'])
            account_age = random.randint(30, 3650)

            profile = {
                'customer_id': customer_id,
                'customer_name': random.choice(self.arabic_names),
                'account_age_days': account_age,
                'customer_since': (datetime.now() - timedelta(days=account_age)).strftime('%Y-%m-%d'),
                'home_country': 'Saudi Arabia' if nationality == 'Saudi' else random.choice(self.countries),
                'nationality': nationality,
                'residence_city': random.choice(self.saudi_cities),
                'avg_monthly_transactions': random.randint(5, 100),
                'avg_transaction_amount': round(random.uniform(200, 8000), 2),  # SAR amounts
                'customer_risk_level': random.choice(['Low', 'Low', 'Low', 'Medium', 'High']),
                'kyc_verified': random.choice([True, True, True, False]),
                'kyc_expiry_date': (datetime.now() + timedelta(days=random.randint(-30, 365))).strftime('%Y-%m-%d'),
                'employment_status': random.choice(['Employed', 'Self-Employed', 'Retired', 'Student', 'Business Owner']),
                'employer_type': random.choice(['Government', 'Private Sector', 'Self-Employed', 'Not Employed']),
                'account_balance': round(random.uniform(500, 500000), 2),  # SAR
                'pep_status': random.choice([False, False, False, False, True]),  # Politically Exposed Person
                'previous_fraud_cases': random.choice([0, 0, 0, 0, 1, 2]),
                'sama_watchlist': random.choice([False, False, False, True]),  # SAMA watchlist
                'account_type': random.choice(['Individual', 'Corporate', 'Joint'])
            }

            profiles.append(profile)

        return pd.DataFrame(profiles)

    def generate_device_fingerprint_data(self):
        """Generate device fingerprinting data"""
        devices = []

        for customer_id in random.sample(self.customer_ids, 300):
            num_devices = random.randint(1, 5)

            for _ in range(num_devices):
                device = {
                    'customer_id': customer_id,
                    'device_id': fake.uuid4(),
                    'device_fingerprint': fake.sha256(),
                    'first_seen': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
                    'last_seen': (datetime.now() - timedelta(days=random.randint(0, 7))).strftime('%Y-%m-%d'),
                    'device_type': random.choice(['Mobile', 'Desktop', 'Tablet']),
                    'os': random.choice(['iOS', 'Android', 'Windows', 'MacOS', 'Linux']),
                    'is_trusted': random.choice([True, True, True, False]),
                    'location_changes': random.randint(0, 20),
                    'suspicious_behavior': random.choice([False, False, False, True])
                }

                devices.append(device)

        return pd.DataFrame(devices)

    def save_all_data(self, output_dir='data'):
        """Generate and save all dummy data"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        print("Generating SAS transfer data (with beneficiary info)...")
        sas_data = self.generate_sas_transfer_data()
        sas_data.to_csv(f'{output_dir}/sas_transfers.csv', index=False)
        print(f"Generated {len(sas_data)} transfers")

        print("Generating login data...")
        login_data = self.generate_login_data()
        login_data.to_csv(f'{output_dir}/login_data.csv', index=False)
        print(f"Generated {len(login_data)} login records")

        print("Generating customer profiles...")
        profile_data = self.generate_customer_profile_data()
        profile_data.to_csv(f'{output_dir}/customer_profiles.csv', index=False)
        print(f"Generated {len(profile_data)} customer profiles")

        print("Generating device fingerprint data...")
        device_data = self.generate_device_fingerprint_data()
        device_data.to_csv(f'{output_dir}/device_fingerprints.csv', index=False)
        print(f"Generated {len(device_data)} device records")

        print(f"\nAll data saved to '{output_dir}/' directory")

        return {
            'transfers': sas_data,
            'logins': login_data,
            'profiles': profile_data,
            'devices': device_data
        }


if __name__ == "__main__":
    generator = DataGenerator(num_transactions=100)
    data = generator.save_all_data()

    print("\n=== Sample Transfer Data ===")
    print(data['transfers'].head(3))
