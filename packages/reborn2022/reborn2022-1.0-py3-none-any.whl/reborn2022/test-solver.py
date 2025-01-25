import asyncio
import aiohttp
import time

async def test_solver():
    url = "http://localhost:5000/solve"
    
    payload = {
        "url": "https://www.google.com/recaptcha/api2/demo",
        "sitekey": "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-",
        "headless": True,
        "debug": False,
        "check_score": False
    }
    
    results = []  # List untuk menyimpan hasil

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=300) as response:  # 5 min timeout
                result = await response.json()
                                
                if response.status == 200 and result.get("success"):
                    token = result["token"]
                    results.append({
                        "status": "success",
                        "token": token
                    })
                else:
                    error = result.get('error', 'Unknown error')
                    results.append({
                        "status": "failed",
                        "error": error,
                        "response": result
                    })
            
    except asyncio.TimeoutError:
        results.append({"status": "failed", "error": "Request timed out after 5 minutes"})
    except aiohttp.ClientError:
        results.append({"status": "failed", "error": "Failed to connect to solver API. Is the server running?"})
    except Exception as e:
        results.append({"status": "failed", "error": str(e)})

    return results

if __name__ == "__main__":
    results = asyncio.run(test_solver())
    for res in results:
        print(res)
