cd zero-dte-trader/backend
source venv/bin/activate
pip install -r requirements.txt  # Only needed once
python main.py

cd zero-dte-trader/frontend
npm install  # Only needed once
npm run dev

Once the frontend is deployed, Render will give you a URL (e.g., https://zero-dte-frontend.onrender.com). Share this link with others!
