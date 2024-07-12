from nicegui import ui
import requests
import re

API_BASE_URL = "http://localhost:8000"

def is_valid_email(email):
    return re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email)

def login(username, password):

    # if not is_valid_email(username):
    #     ui.notify("Invalid email format!", color="red")
    #     return
    
    # if len(password) < 8:
    #     ui.notify("Password must be at least 8 characters long!", color="red")
    #     return
    
    response = requests.post(f"{API_BASE_URL}/login", data={
        'username': username,
        'password': password
    })

    if response.status_code == 200:
        ui.notify('Login successful')
    else:
        ui.notify("Login Failed!", color="red")

def register_user(email, password):
    if len(password) < 8:
        ui.notify("Password must be at least 8 characters long!", color="red")
        return
    
    response = requests.post(f"{API_BASE_URL}/users/user", data={
        'email': email,
        'password': password
    })
    if response.status_code == 201:
        ui.notify('User registered successfully')
    else:
        ui.notify("Registration Failed!", color="red")
    
def register_admin(email, password):
    if len(password) < 8:
        ui.notify("Password must be at least 8 characters long!", color="red")
        return
     
    response = requests.post(f"{API_BASE_URL}/users/admin", data={
        'email': email,
        'password': password
    })
    if response.status_code == 201:
        ui.notify('Admin registered successfully')
    else:
        ui.notify("Registration Failed!", color="red")

# Adding custom CSS for styling
ui.add_head_html("""
<style>
    .login-container {
        max-width: 500px;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        background-color: white;
        margin: auto;
        margin-top: 100px;
    }
    .logo {
        width: 300px;
        height: auto;
        display: block;
        margin: 0 auto 20px auto;
    }
    .tab-content {
        margin-top: 20px;
    }
    .custom-input {
        margin-bottom: 20px;
        width: 100%; /* Make input fields take up the full width */
    }
    .custom-button {
        width: 100%;
        background-color: #007bff;
        color: white;
    }
</style>
""")

with ui.card().classes('login-container'):
    ui.markdown("""
    <img src="https://panchkoshawellbeing.in/assets/images/logo-1.png" alt="PanchkoshWellbeing" class="logo">
    """)
    with ui.tabs() as logintabs:
        ui.tab('login', label="Login")
        ui.tab('signup', label="SignUp")
    with ui.tab_panels(logintabs, value='login').classes('w-full'):
        with ui.tab_panel('login'):
            # ui.markdown("### Login")
            username = ui.input(label='Email').classes('custom-input')
            password = ui.input(label='Password', password=True).classes('custom-input')
            ui.button('Login', on_click=lambda: login(username.value, password.value)).classes('custom-button')
        
        with ui.tab_panel('signup'):
            # ui.markdown("### Sign Up")
            with ui.tabs() as signtabs:
                ui.tab('user', label="User")
                ui.tab('admin', label="Admin")
            with ui.tab_panels(signtabs, value='user').classes('w-full'):
                with ui.tab_panel('user'):
                    username = ui.input(label='Email').classes('custom-input')
                    password = ui.input(label='Password', password=True).classes('custom-input')
                    ui.button('Sign Up as User', on_click=lambda: register_user(username.value, password.value)).classes('custom-button')
                with ui.tab_panel('admin'):
                    username = ui.input(label='Email').classes('custom-input')
                    password = ui.input(label='Password', password=True).classes('custom-input')
                    ui.button('Sign Up as Admin', on_click=lambda: register_admin(username.value, password.value)).classes('custom-button')

ui.run()
