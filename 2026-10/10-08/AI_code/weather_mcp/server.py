import httpx
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("Weather Tools")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: "맑음", 1: "대체로 맑음", 2: "부분적으로 흐림", 3: "흐림",
    45: "안개", 48: "서리 안개", 51: "약한 이슬비", 53: "이슬비",
    55: "강한 이슬비", 61: "약한 비", 63: "비", 65: "강한 비",
    71: "약한 눈", 73: "눈", 75: "강한 눈", 80: "약한 소나기",
    81: "소나기", 82: "강한 소나기", 95: "뇌우",
}

async def fetch_json(url: str, params: dict[str, object]) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

def validate_city(city: str) -> str:
    city = city.strip()
    if len(city) < 2:
        raise ValueError("도시 이름은 두 글자 이상 입력하세요.")
    if len(city) > 50:
        raise ValueError("도시 이름이 너무 깁니다.")
    return city

def weather_description(code: int) -> str:
    return WEATHER_CODES.get(code, f"알 수 없는 날씨 코드({code})")

@mcp.tool()
async def get_current_weather(city: str) -> dict:
    """도시 이름을 받아 현재 날씨를 조회합니다.

    한국어 또는 영어 도시 이름을 입력합니다.
    예: 서울, 부산, Tokyo, New York
    """
    try:
        city = validate_city(city)
        location_data = await fetch_json(
            GEOCODING_URL,
            {"name": city, "count": 1, "language": "ko", "format": "json"},
        )
        results = location_data.get("results", [])
        if not results:
            return {"success": False, "message": f"'{city}' 도시를 찾지 못했습니다."}

        location = results[0]
        weather_data = await fetch_json(
            FORECAST_URL,
            {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": (
                    "temperature_2m,relative_humidity_2m,"
                    "apparent_temperature,weather_code,wind_speed_10m"
                ),
                "timezone": "auto",
            },
        )
        current = weather_data.get("current", {})
        units = weather_data.get("current_units", {})
        return {
            "success": True,
            "city": location.get("name"),
            "country": location.get("country"),
            "timezone": weather_data.get("timezone"),
            "observed_at": current.get("time"),
            "weather": weather_description(int(current.get("weather_code", -1))),
            "temperature": f"{current.get('temperature_2m')} {units.get('temperature_2m', '°C')}",
            "apparent_temperature": f"{current.get('apparent_temperature')} {units.get('apparent_temperature', '°C')}",
            "humidity": f"{current.get('relative_humidity_2m')} {units.get('relative_humidity_2m', '%')}",
            "wind_speed": f"{current.get('wind_speed_10m')} {units.get('wind_speed_10m', 'km/h')}",
        }
    except ValueError as error:
        return {"success": False, "message": str(error)}
    except httpx.TimeoutException:
        return {"success": False, "message": "날씨 API 응답 시간이 초과되었습니다."}
    except httpx.HTTPStatusError as error:
        return {"success": False, "message": f"날씨 API 오류: HTTP {error.response.status_code}"}
    except httpx.RequestError:
        return {"success": False, "message": "네트워크 연결 중 오류가 발생했습니다."}
    except (KeyError, TypeError):
        return {"success": False, "message": "API 응답 형식이 예상과 다릅니다."}

if __name__ == "__main__":
    mcp.run(transport="stdio")
