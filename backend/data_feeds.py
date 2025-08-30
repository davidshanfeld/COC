import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio
import aiohttp
from agent_models import TreasuryYieldResponse, FredResponse, FdicResponse, CreMaturitiesResponse, ZoningLAResponse

class DataFeedService:
    def __init__(self):
        self.fred_api_key = os.getenv("FRED_API_KEY")
        self.treasury_api_key = os.getenv("TREASURY_API_KEY")  # Optional
        
    async def treasury_yield(self, tenor: str) -> TreasuryYieldResponse:
        """Get Treasury yield data - public API"""
        try:
            # Using FRED for Treasury data as it's more reliable and free
            tenor_mapping = {
                "5Y": "GS5",
                "10Y": "GS10", 
                "30Y": "GS30"
            }
            
            if tenor not in tenor_mapping:
                raise ValueError(f"Unsupported tenor: {tenor}")
                
            series_id = tenor_mapping[tenor]
            
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.fred_api_key,
                "file_type": "json",
                "limit": 1,
                "sort_order": "desc",
                "observation_start": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        observations = data.get("observations", [])
                        if observations:
                            latest = observations[0]
                            return TreasuryYieldResponse(
                                tenor=tenor,
                                value=float(latest["value"]) if latest["value"] != "." else 0.0,
                                as_of=latest["date"]
                            )
                    
            # Fallback mock data if API fails
            mock_values = {"5Y": 4.25, "10Y": 4.65, "30Y": 4.85}
            return TreasuryYieldResponse(
                tenor=tenor,
                value=mock_values.get(tenor, 4.5),
                as_of=datetime.now().strftime("%Y-%m-%d")
            )
            
        except Exception as e:
            print(f"Treasury yield error: {e}")
            # Return mock data on error
            mock_values = {"5Y": 4.25, "10Y": 4.65, "30Y": 4.85}
            return TreasuryYieldResponse(
                tenor=tenor,
                value=mock_values.get(tenor, 4.5),
                as_of=datetime.now().strftime("%Y-%m-%d")
            )

    async def fred(self, series_id: str, opts: Optional[Dict[str, Any]] = None) -> FredResponse:
        """Get FRED economic data"""
        try:
            url = "https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.fred_api_key,
                "file_type": "json",
                "limit": opts.get("limit", 10) if opts else 10,
                "sort_order": "desc"
            }
            
            if opts:
                if "start_date" in opts:
                    params["observation_start"] = opts["start_date"]
                if "end_date" in opts:
                    params["observation_end"] = opts["end_date"]
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        observations = data.get("observations", [])
                        
                        rows = []
                        for obs in observations:
                            if obs["value"] != ".":
                                rows.append({
                                    "date": obs["date"],
                                    "value": float(obs["value"]),
                                    "series_id": series_id
                                })
                        
                        return FredResponse(series_id=series_id, rows=rows)
                        
        except Exception as e:
            print(f"FRED API error: {e}")
            
        # Return mock data on error
        mock_data = {
            "DFF": [{"date": datetime.now().strftime("%Y-%m-%d"), "value": 5.33, "series_id": "DFF"}],
            "UNRATE": [{"date": datetime.now().strftime("%Y-%m-%d"), "value": 3.7, "series_id": "UNRATE"}],
            "CPIAUCSL": [{"date": datetime.now().strftime("%Y-%m-%d"), "value": 310.5, "series_id": "CPIAUCSL"}]
        }
        
        return FredResponse(
            series_id=series_id,
            rows=mock_data.get(series_id, [{"date": datetime.now().strftime("%Y-%m-%d"), "value": 0.0, "series_id": series_id}])
        )

    async def fdic_call_reports(self, opts: Optional[Dict[str, Any]] = None) -> FdicResponse:
        """Get FDIC Call Reports data"""
        try:
            # FDIC API is public but complex - using simplified mock for now
            # Real implementation would use: https://banks.data.fdic.gov/api/
            
            # Mock LA area bank data
            mock_rows = [
                {
                    "cert": "1",
                    "name": "Bank of America, National Association",
                    "city": "Charlotte",
                    "state": "NC",
                    "total_assets": 2354208000,
                    "total_deposits": 1900000000,
                    "roa": 1.05,
                    "roe": 11.2,
                    "as_of_date": "2024-12-31"
                },
                {
                    "cert": "3511",
                    "name": "Wells Fargo Bank, National Association", 
                    "city": "Sioux Falls",
                    "state": "SD",
                    "total_assets": 1700000000,
                    "total_deposits": 1400000000,
                    "roa": 0.88,
                    "roe": 9.8,
                    "as_of_date": "2024-12-31"
                }
            ]
            
            return FdicResponse(rows=mock_rows)
            
        except Exception as e:
            print(f"FDIC API error: {e}")
            return FdicResponse(rows=[])

    async def cre_maturities(self, opts: Optional[Dict[str, Any]] = None) -> CreMaturitiesResponse:
        """Get CRE maturity ladder data - mocked with Trepp-compatible schema"""
        try:
            # Mock data compatible with Trepp/MSCI format
            mock_rows = [
                {
                    "property_type": "Office",
                    "maturity_year": "2025",
                    "outstanding_balance": 12500000000,
                    "maturing_loans": 450,
                    "avg_ltv": 0.72,
                    "avg_dscr": 1.15,
                    "distress_probability": 0.35,
                    "geographic_concentration": "Los Angeles MSA",
                    "loan_size_category": "Large Balance",
                    "origination_year_range": "2018-2020"
                },
                {
                    "property_type": "Industrial",
                    "maturity_year": "2025", 
                    "outstanding_balance": 8200000000,
                    "maturing_loans": 320,
                    "avg_ltv": 0.68,
                    "avg_dscr": 1.28,
                    "distress_probability": 0.22,
                    "geographic_concentration": "Los Angeles MSA",
                    "loan_size_category": "Large Balance",
                    "origination_year_range": "2019-2021"
                },
                {
                    "property_type": "Retail",
                    "maturity_year": "2025",
                    "outstanding_balance": 6800000000,
                    "maturing_loans": 275,
                    "avg_ltv": 0.75,
                    "avg_dscr": 1.08,
                    "distress_probability": 0.42,
                    "geographic_concentration": "Los Angeles MSA", 
                    "loan_size_category": "Large Balance",
                    "origination_year_range": "2017-2019"
                }
            ]
            
            return CreMaturitiesResponse(rows=mock_rows)
            
        except Exception as e:
            print(f"CRE Maturities error: {e}")
            return CreMaturitiesResponse(rows=[])

    async def zoning_la(self, opts: Optional[Dict[str, Any]] = None) -> ZoningLAResponse:
        """Get LA zoning data - mocked"""
        try:
            # Mock LA zoning data for development projects
            mock_rows = [
                {
                    "apn": "5421-015-001",
                    "zone": "M3-1",
                    "description": "Heavy Manufacturing Zone",
                    "permitted_uses": ["Data Centers", "Industrial", "Warehouse"],
                    "max_floor_area_ratio": 6.0,
                    "max_height": "Unlimited",
                    "power_availability": "High Voltage Available",
                    "fiber_infrastructure": "Tier 1 Available",
                    "development_incentives": ["Adaptive Reuse", "Green Building Bonus"],
                    "permitting_complexity": "Medium",
                    "estimated_timeline_months": 18
                },
                {
                    "apn": "5421-016-002", 
                    "zone": "CM-1",
                    "description": "Commercial Manufacturing Zone",
                    "permitted_uses": ["EV Charging", "Light Manufacturing", "Commercial"],
                    "max_floor_area_ratio": 3.0,
                    "max_height": "75 feet",
                    "power_availability": "Standard Grid",
                    "fiber_infrastructure": "Standard Available",
                    "development_incentives": ["NEVI Eligible", "EV Infrastructure Bonus"],
                    "permitting_complexity": "Low",
                    "estimated_timeline_months": 9
                }
            ]
            
            return ZoningLAResponse(rows=mock_rows)
            
        except Exception as e:
            print(f"LA Zoning error: {e}")
            return ZoningLAResponse(rows=[])

# Singleton instance
data_feed_service = DataFeedService()