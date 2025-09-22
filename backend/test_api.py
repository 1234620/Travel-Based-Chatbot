import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.flight_agent.flight_agent import FlightAgent

async def test_flight_api():
    try:
        agent = FlightAgent()
        result = await agent.search_flights('DEL', 'BOM', '2025-10-21')
        print('Flight API Test: SUCCESS')
        print('Sample result keys:', list(result.keys()) if result else 'No result')
        return True
    except Exception as e:
        print(f'Flight API Test: FAILED - {e}')
        return False

if __name__ == "__main__":
    asyncio.run(test_flight_api())
