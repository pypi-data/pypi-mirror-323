from quart import Quart, request, jsonify
from recaptcha import solve_recaptcha
from logmagix import Logger
from typing import Optional

app = Quart(__name__)
logger = Logger()

@app.route('/solve', methods=['POST'])
async def solve_captcha():
    try:
        data = await request.get_json()

        if not data or 'url' not in data or 'sitekey' not in data:
            return jsonify({
                "error": "Missing required parameters: url and sitekey"
            }), 400

        url: str = data['url']
        site_key: str = data['sitekey']
        token = solve_recaptcha(url, site_key)

        if "Error" in token:
            return jsonify({
                "success": False,
                "error": token
            }), 500

        return jsonify({
            "success": True,
            "token": token
        })

    except Exception as e:
        logger.failure(f"Server error: {str(e)}")
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
