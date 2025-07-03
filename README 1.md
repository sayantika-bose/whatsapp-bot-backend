# whatsapp-bot-backend

python3 -m venv .venv

<!-- Enter the environment -->
source .venv/bin/activate

pip install -r requirements.txt

<!-- To uninstall  -->
pip freeze | xargs pip uninstall -y

<!-- update requirements -->
pip freeze > requirements.txt

<!-- Run the app -->
uvicorn app:app --reload

<!-- Enter the db -->
sqlite3 yannick_test.db

<!-- List all tables -->
.tables

<!-- (Optional) Show schema of a table -->
.schema users

<!-- to protect routes -->
dependencies=[Depends(decode_token)]


{
  "first_name": "Corentin",
  "mobile_number": "0600000000",
  "advisor_id": 2,
}
<!-- doc swagger  -->
http://localhost:8000/docs#/

<!-- To launch in debug use the console "Launch with json..." -->