FROM python:3.12-slim

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the application code
COPY . .

# Expose the port
EXPOSE 5005

# Run the command to start the development server
CMD ["python", "translater_google_only.py"]