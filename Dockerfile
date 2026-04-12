# 1. Use an official lightweight Python image
FROM python:3.9-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy our requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of our application code
COPY . .

# 5. Expose the port Flask runs on
EXPOSE 5000

# 6. Command to run the application
CMD ["python", "web_app/app.py"]
