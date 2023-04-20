from app import create_app

# Create an instance of the Flask app
app = create_app()

if __name__ == '__main__':
    # Start the development server
    app.run(debug=True)
