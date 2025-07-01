FROM python:3.8-slim

WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy planner script and PDDL files
COPY . .

CMD ["python", "planner_main.py"]