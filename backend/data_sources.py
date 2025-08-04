import asyncio
import aiohttp
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class DataSourceManager:
    def __init__(self):
        self.fred_api_key = os.getenv('FRED_API_KEY')
        self.sources = {
            'fed_funds_rate': {
                'url': 'https://api.stlouisfed.org/fred/series/observations',
                'params': {'series_id': 'FEDFUNDS', 'api_key': self.fred_api_key, 'file_type': 'json', 'limit': 1, 'sort_order': 'desc'},
                'parser': self._parse_fred_data,
                'unit': 'percent',
                'description': 'Federal Funds Rate'
            },
            '10_year_treasury': {
                'url': 'https://api.stlouisfed.org/fred/series/observations',
                'params': {'series_id': 'GS10', 'api_key': self.fred_api_key, 'file_type': 'json', 'limit': 1, 'sort_order': 'desc'},
                'parser': self._parse_fred_data,
                'unit': 'percent',
                'description': '10-Year Treasury Constant Maturity Rate'
            },
            'cpi_inflation': {
                'url': 'https://api.stlouisfed.org/fred/series/observations',
                'params': {'series_id': 'CPIAUCSL', 'api_key': self.fred_api_key, 'file_type': 'json', 'limit': 2, 'sort_order': 'desc'},
                'parser': self._parse_cpi_data,
                'unit': 'percent_annual',
                'description': 'Consumer Price Index - All Urban Consumers'
            },
            'construction_cost_index': {
                'url': 'https://api.stlouisfed.org/fred/series/observations',
                'params': {'series_id': 'WPUSI012011', 'api_key': self.fred_api_key, 'file_type': 'json', 'limit': 1, 'sort_order': 'desc'},
                'parser': self._parse_fred_data,
                'unit': 'index',
                'description': 'Producer Price Index: Construction Materials and Components'
            },
            'commercial_electricity_rate': {
                'url': 'https://api.stlouisfed.org/fred/series/observations',
                'params': {'series_id': 'ELCPCA', 'api_key': self.fred_api_key, 'file_type': 'json', 'limit': 1, 'sort_order': 'desc'},
                'parser': self._parse_fred_data,
                'unit': 'cents_per_kwh',
                'description': 'Average Retail Price of Electricity: Commercial - California'
            }
        }
        
        # Mock data sources for premium APIs that would require keys
        self.mock_sources = {
            'cmbs_spread': {
                'value': 275,  # basis points over treasury
                'unit': 'basis_points',
                'description': 'CMBS AAA-Treasury Spread',
                'source': 'Trepp (Simulated)'
            },
            'cap_rates_office': {
                'value': 6.25,
                'unit': 'percent',
                'description': 'Average Cap Rates - Office Buildings',
                'source': 'RCA (Simulated)'
            },
            'distressed_debt_discount': {
                'value': 35,
                'unit': 'percent',
                'description': 'Average Discount on Distressed CRE Debt',
                'source': 'CBRE (Simulated)'
            }
        }

    async def fetch_all_data(self) -> Dict[str, Dict]:
        """Fetch all real-time data sources"""
        results = {}
        
        # Fetch real data from FRED if API key is available
        if self.fred_api_key:
            async with aiohttp.ClientSession() as session:
                tasks = []
                for source_name, config in self.sources.items():
                    tasks.append(self._fetch_source_data(session, source_name, config))
                
                fred_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, (source_name, config) in enumerate(self.sources.items()):
                    if isinstance(fred_results[i], Exception):
                        logger.error(f"Error fetching {source_name}: {fred_results[i]}")
                        # Use fallback data
                        results[source_name] = self._get_fallback_data(source_name)
                    else:
                        results[source_name] = fred_results[i]
        else:
            # Use fallback data if no API key
            logger.warning("No FRED API key found, using fallback data")
            for source_name in self.sources.keys():
                results[source_name] = self._get_fallback_data(source_name)
        
        # Add mock premium data sources
        for source_name, data in self.mock_sources.items():
            results[source_name] = {
                'value': data['value'],
                'unit': data['unit'],
                'source': data['source'],
                'description': data['description'],
                'timestamp': datetime.now(),
                'last_updated': datetime.now()
            }
        
        return results

    async def _fetch_source_data(self, session: aiohttp.ClientSession, source_name: str, config: Dict) -> Dict:
        """Fetch data from a specific source"""
        try:
            async with session.get(config['url'], params=config['params']) as response:
                if response.status == 200:
                    data = await response.json()
                    parsed_value = config['parser'](data)
                    return {
                        'value': parsed_value,
                        'unit': config['unit'],
                        'source': 'Federal Reserve Economic Data (FRED)',
                        'description': config['description'],
                        'timestamp': datetime.now(),
                        'last_updated': datetime.now()
                    }
                else:
                    raise Exception(f"HTTP {response.status}")
        except Exception as e:
            logger.error(f"Error fetching {source_name}: {e}")
            raise

    def _parse_fred_data(self, data: Dict) -> float:
        """Parse standard FRED API response"""
        try:
            observations = data.get('observations', [])
            if observations:
                latest = observations[0]
                value = latest.get('value', '.')
                if value != '.':
                    return float(value)
            raise ValueError("No valid data found")
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Failed to parse FRED data: {e}")

    def _parse_cpi_data(self, data: Dict) -> float:
        """Parse CPI data and calculate annual inflation rate"""
        try:
            observations = data.get('observations', [])
            if len(observations) >= 2:
                current = float(observations[0]['value'])
                previous = float(observations[1]['value'])
                inflation_rate = ((current - previous) / previous) * 100
                return round(inflation_rate, 2)
            raise ValueError("Insufficient CPI data")
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"Failed to parse CPI data: {e}")

    def _get_fallback_data(self, source_name: str) -> Dict:
        """Get fallback data when API is unavailable"""
        fallback_data = {
            'fed_funds_rate': {'value': 5.25, 'unit': 'percent'},
            '10_year_treasury': {'value': 4.15, 'unit': 'percent'},
            'cpi_inflation': {'value': 3.2, 'unit': 'percent_annual'},
            'construction_cost_index': {'value': 285.4, 'unit': 'index'},
            'commercial_electricity_rate': {'value': 18.5, 'unit': 'cents_per_kwh'}
        }
        
        base_data = fallback_data.get(source_name, {'value': 0.0, 'unit': 'unknown'})
        return {
            **base_data,
            'source': 'Simulated Data (API Unavailable)',
            'description': self.sources[source_name]['description'],
            'timestamp': datetime.now(),
            'last_updated': datetime.now()
        }


class FinancialCalculator:
    """Financial calculation engine for real-time model updates"""
    
    @staticmethod
    def calculate_cost_of_capital(risk_free_rate: float, risk_premium: float) -> float:
        """Calculate cost of capital: risk-free rate + risk premium"""
        return risk_free_rate + risk_premium
    
    @staticmethod
    def calculate_cap_rate_adjustment(base_cap_rate: float, inflation_rate: float, risk_adjustment: float = 0.0) -> float:
        """Adjust cap rates based on inflation and risk factors"""
        return base_cap_rate + (inflation_rate * 0.5) + risk_adjustment
    
    @staticmethod
    def calculate_construction_cost_escalation(base_cost: float, construction_index: float, base_index: float = 250.0) -> float:
        """Calculate construction cost based on current index vs baseline"""
        escalation_factor = construction_index / base_index
        return base_cost * escalation_factor
    
    @staticmethod
    def calculate_energy_cost_per_sf(electricity_rate: float, kwh_per_sf: float = 13.5) -> float:
        """Calculate annual energy cost per square foot"""
        # Convert cents per kWh to $ per kWh
        rate_per_kwh = electricity_rate / 100
        return rate_per_kwh * kwh_per_sf
    
    @staticmethod
    def calculate_ev_charging_revenue(utilization_rate: float, charging_rate: float = 0.45, daily_kwh: float = 13616) -> float:
        """Calculate annual EV charging revenue"""
        annual_kwh = daily_kwh * 365 * (utilization_rate / 100)
        return annual_kwh * charging_rate
    
    @staticmethod
    def calculate_debt_service_coverage(noi: float, debt_service: float) -> float:
        """Calculate debt service coverage ratio"""
        return noi / debt_service if debt_service > 0 else 0
    
    @staticmethod
    def calculate_irr_approximation(cash_flows: List[float], initial_investment: float) -> float:
        """Simple IRR approximation for quick calculations"""
        total_cash_flow = sum(cash_flows)
        years = len(cash_flows)
        if years == 0 or initial_investment <= 0:
            return 0
        
        # Simple approximation: (total return / initial investment) ^ (1/years) - 1
        total_return = total_cash_flow + initial_investment
        if total_return <= 0:
            return -100  # Total loss
        
        irr = (total_return / initial_investment) ** (1/years) - 1
        return round(irr * 100, 2)  # Return as percentage