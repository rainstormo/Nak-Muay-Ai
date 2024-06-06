from werkzeug.security import generate_password_hash

# Plain text password
plain_password = "testpassword"

# Generate hashed password
hashed_password = generate_password_hash(plain_password)
print(hashed_password)
