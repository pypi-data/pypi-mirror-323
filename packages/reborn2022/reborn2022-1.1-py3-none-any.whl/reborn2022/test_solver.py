import asyncio
import aiohttp

async def test_solver(url, sitekey, headless=True):
    server_url = "http://localhost:5000/solve"
    payload = {
        "url": url,
        "sitekey": sitekey,
        "headless": headless
    }
    
    results = [] 

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(server_url, json=payload, timeout=300) as response:  # 5 min timeout
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

