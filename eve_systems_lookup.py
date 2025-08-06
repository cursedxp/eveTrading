"""
EVE Systems Dynamic Lookup
Provides dynamic system information using EVE ESI API
"""

import aiohttp
import asyncio
import logging
from typing import Dict, Optional, List
from functools import lru_cache
import json

logger = logging.getLogger(__name__)

class EVESystemsLookup:
    """Dynamic EVE system information lookup using ESI API"""
    
    def __init__(self):
        self.session = None
        self.systems_cache = {}
        self.regions_cache = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_system(self, system_name: str) -> Optional[Dict]:
        """Search for a system by name and return its information"""
        try:
            # Use the universe/ids endpoint for system lookup
            search_url = "https://esi.evetech.net/latest/universe/ids/"
            
            async with self.session.post(search_url, json=[system_name]) as response:
                if response.status != 200:
                    logger.error(f"Failed to search for system {system_name}: {response.status}")
                    return None
                    
                search_data = await response.json()
                
                if not search_data.get('systems'):
                    logger.warning(f"System {system_name} not found")
                    return None
                
                # Get the first matching system
                system_match = search_data['systems'][0]
                system_id = system_match['id']
                
                # Get system information
                system_info = await self.get_system_info(system_id)
                
                return system_info
                
        except Exception as e:
            logger.error(f"Error searching for system {system_name}: {e}")
            return None
    
    async def get_system_info(self, system_id: int) -> Optional[Dict]:
        """Get detailed information about a system"""
        try:
            # Check cache first
            if system_id in self.systems_cache:
                return self.systems_cache[system_id]
            
            system_url = f"https://esi.evetech.net/latest/universe/systems/{system_id}/"
            
            async with self.session.get(system_url) as response:
                if response.status != 200:
                    logger.error(f"Failed to get system info for {system_id}: {response.status}")
                    return None
                
                system_data = await response.json()
                
                # Get constellation and region info
                constellation_id = system_data.get('constellation_id')
                constellation_info = await self.get_constellation_info(constellation_id)
                
                if constellation_info:
                    region_id = constellation_info.get('region_id')
                    region_info = await self.get_region_info(region_id)
                    
                    # Compile complete system info
                    system_info = {
                        'system_id': system_id,
                        'name': system_data.get('name'),
                        'constellation_id': constellation_id,
                        'region_id': region_id,
                        'region_name': region_info.get('name') if region_info else 'Unknown',
                        'security_status': system_data.get('security_status', 0),
                        'security_class': self.get_security_class(system_data.get('security_status', 0))
                    }
                    
                    # Cache the result
                    self.systems_cache[system_id] = system_info
                    
                    return system_info
                
        except Exception as e:
            logger.error(f"Error getting system info for {system_id}: {e}")
            return None
    
    async def get_constellation_info(self, constellation_id: int) -> Optional[Dict]:
        """Get constellation information"""
        try:
            constellation_url = f"https://esi.evetech.net/latest/universe/constellations/{constellation_id}/"
            
            async with self.session.get(constellation_url) as response:
                if response.status != 200:
                    return None
                    
                return await response.json()
                
        except Exception as e:
            logger.error(f"Error getting constellation info: {e}")
            return None
    
    async def get_region_info(self, region_id: int) -> Optional[Dict]:
        """Get region information"""
        try:
            # Check cache first
            if region_id in self.regions_cache:
                return self.regions_cache[region_id]
            
            region_url = f"https://esi.evetech.net/latest/universe/regions/{region_id}/"
            
            async with self.session.get(region_url) as response:
                if response.status != 200:
                    return None
                
                region_data = await response.json()
                
                # Cache the result
                self.regions_cache[region_id] = region_data
                
                return region_data
                
        except Exception as e:
            logger.error(f"Error getting region info: {e}")
            return None
    
    def get_security_class(self, security_status: float) -> str:
        """Determine security class based on status"""
        if security_status >= 0.5:
            return "High Sec"
        elif security_status > 0.0:
            return "Low Sec"
        else:
            return "Null Sec"
    
    async def get_all_trade_hubs(self) -> List[Dict]:
        """Get a list of major trade hubs and their info"""
        major_hubs = [
            "Jita", "Amarr", "Dodixie", "Rens", "Hek",
            "Perimeter", "New Caldari", "Oursulaert", "Niarja",
            "Ashab", "Tash-Murkon Prime", "Torrinos", "Clellinon",
            "Stacmon", "Orvolle", "Villore", "Alentene"
        ]
        
        hubs_info = []
        for hub in major_hubs:
            info = await self.search_system(hub)
            if info:
                hubs_info.append(info)
        
        return hubs_info
    
    def estimate_market_profile(self, system_name: str, security_status: float) -> Dict:
        """Estimate market profile based on system characteristics"""
        # Known major hubs
        major_hubs = {
            "Jita": {"competition": "Very High", "volume": "Very High", "profit_margins": "Low", "specialization": "Everything"},
            "Amarr": {"competition": "High", "volume": "High", "profit_margins": "Medium", "specialization": "Minerals, Ships"},
            "Dodixie": {"competition": "Medium", "volume": "Medium", "profit_margins": "Medium-High", "specialization": "Minerals, Components"},
            "Rens": {"competition": "Medium", "volume": "Medium", "profit_margins": "Medium-High", "specialization": "Minerals, Ammunition"},
            "Hek": {"competition": "Medium", "volume": "Medium", "profit_margins": "Medium-High", "specialization": "Minerals, Drones"},
        }
        
        # Check if it's a known hub
        if system_name in major_hubs:
            return major_hubs[system_name]
        
        # Estimate based on security status
        if security_status >= 0.9:
            return {
                "competition": "Low-Medium",
                "volume": "Low-Medium",
                "profit_margins": "Medium-High",
                "specialization": "General Trading"
            }
        elif security_status >= 0.5:
            return {
                "competition": "Low",
                "volume": "Low",
                "profit_margins": "High",
                "specialization": "Regional Trading"
            }
        elif security_status > 0.0:
            return {
                "competition": "Very Low",
                "volume": "Very Low",
                "profit_margins": "Very High",
                "specialization": "PvP Supplies, Specialized Items"
            }
        else:
            return {
                "competition": "Very Low",
                "volume": "Very Low",
                "profit_margins": "Very High",
                "specialization": "Null Sec Supplies, Capital Components"
            }