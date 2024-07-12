from nicegui import Client, app, ui
import requests
import datetime
import pytz
import re

API_BASE_URL = "http://localhost:8000"
jwt_token = None
current_user = None
selected_event = None  

def is_valid_email(email):
    return re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email)

def login():
    global jwt_token,current_user,current_user_role
    username_value = username.value
    password_value = password.value

    if not is_valid_email(username_value):
        ui.notify("Invalid email format!", color="red")
        return
    
    if len(password_value) < 8:
        ui.notify("Password must be at least 8 characters long!", color="red")
        return
    
    response = requests.post(f"{API_BASE_URL}/login", data={
        'username': username_value,
        'password': password_value
    })

    if response.status_code == 200:
        jwt_token = response.json().get('access_token')
        headers = {'Authorization': f'Bearer {jwt_token}'}
        user_response = requests.get(f"{API_BASE_URL}/users/{username_value}",headers=headers)
        if user_response.status_code==200:
            current_user = user_response.json().get('name')
            current_user_role = user_response.json().get('role')
            ui.notify('Login successful')
            ui.navigate.to('/events')
        else:
            ui.notify("Failed to fetch user details", color="red")
    else:
        ui.notify("Invalid Credentials", color="red")

def register_user():
    name_value = user_name.value
    email_value = user_email.value
    password_value = user_password.value

    if not is_valid_email(email_value):
        ui.notify("Invalid email format!", color="red")
        return
    
    if len(password_value) < 8:
        ui.notify("Password must be at least 8 characters long!", color="red")
        return
    
    response = requests.post(f"{API_BASE_URL}/users/user", json={
        'email': email_value,
        'name': name_value,
        'password': password_value
    })
    if response.status_code == 201:
        ui.notify('User registered successfully')
    elif response.status_code==400 and response.json().get('detail')=="Email already registered":
        ui.notify("Already Registered, Please Login")
    else:
        ui.notify("Registration Failed!", color="red")

def register_admin():
    name_value = admin_name.value
    email_value = admin_email.value
    password_value = admin_password.value

    if not is_valid_email(email_value):
        ui.notify("Invalid email format!", color="red")
        return
    
    if len(password_value) < 8:
        ui.notify("Password must be at least 8 characters long!", color="red")
        return
    
    response = requests.post(f"{API_BASE_URL}/users/admin", json={
        'email': email_value,
        'name':name_value,
        'password': password_value
    })

    if response.status_code == 201:
        ui.notify('Admin registered successfully')
    elif response.status_code==400 and response.json().get('detail')=="Email already registered":
        ui.notify("Already Registered, Please Login")
    else:
        ui.notify("Registration Failed!", color="red")

@ui.page('/events')
def events_page():
    ui.add_head_html("""
    <style>
        .event-card {
            border: 1px solid #ddd;
            padding: 15px;
            margin: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            flex: 1;
        }
        .event-title {
            font-size: 18px;
            font-weight: bold;
        }
        .event-details {
            margin: 10px 0;
        }
        .register-button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .events-container {
            display: flex;
            flex-wrap: wrap;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 20px;
            background-color: #f8f9fa;
            border-bottom: 1px solid #ddd;
        }
        .header .greeting {
            font-size: 16px;
            font-weight: bold;
        }
        .header .logout-button {
            background-color: #dc3545;
            color: white;
            padding: 5px 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .filters {
            margin: 20px;
        }
        .filters input {
            margin-right: 10px;
        }
        .profile-icon {
            font-size: 15px;
            cursor: pointer;
            margin-left: 10px;
        }
        .create-event-card {
            border: 1px solid #ddd;
            padding: 15px;
            margin: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .create-event-icon {
            font-size: 36px;
            color: #007bff;
            margin-bottom: 10px;
        }
        .create-event-text {
            font-size: 18px;
            color: #007bff;
        }
        .info-button {
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: transparent;
            border: none;
            cursor: pointer;
        }
        .info-icon {
            font-size: 18px;
            color: #007bff;
        }       
        .profile-details {
            margin: 5px 0;
        }            
    </style>
    """)

    global jwt_token,current_user,current_user_role

    if not jwt_token:
        ui.navigate.to('/')
        return

    def logout():
        global jwt_token,current_user
        jwt_token=None
        current_user=None
        ui.notify("Logged Out Successfully")
        ui.navigate.to('/')

    def register_for_event(event):
        global selected_event
        selected_event = event
        ui.navigate.to('/register')

    def get_event_info(event):
        global selected_event
        selected_event = event
        ui.navigate.to("/event_info")
    
    def edit_event(event):
        global selected_event
        selected_event = event
        ui.navigate.to('/update-event')

    def unregister_event(event_id):
        headers = {
        'Authorization':f'Bearer {jwt_token}'
    }   
        payload = {
            "event_id": event_id["id"]
        }
        try:
            response = requests.delete(f"{API_BASE_URL}/registrations", headers=headers, json=payload)
            response.raise_for_status() 
            ui.notify("Successfully unregistered from event.")
            ui.navigate.to('/events')
        except requests.exceptions.HTTPError as err:
            ui.notify(f"Error {err}")

    headers = {
        'Authorization':f'Bearer {jwt_token}'
    }
    
    all_events_response = requests.get(f"{API_BASE_URL}/events/getall",headers=headers)
    registrations_response = requests.get(f"{API_BASE_URL}/registrations/NumRegistrations", headers=headers)
    my_events_response = requests.get(f"{API_BASE_URL}/registrations/getregistered", headers=headers)

    def search_events():
        headers = {'Authorization':f'Bearer {jwt_token}'}

        min_price = minprice_filter.value
        max_price = maxprice_filter.value

        if not title_filter.value and not location_filter.value and not min_price and not max_price:
            ui.navigate.to('/events')
            return

        try:
            if min_price: 
                if not minprice_filter.value.isdigit() or int(minprice_filter.value)<=0:
                    ui.notify("Please enter a valid min price",color='red')
                    return
                min_price = int(min_price) 
            else:
                min_price = None
        except ValueError:
            min_price = None

        try:
            if max_price:
                if not maxprice_filter.value.isdigit() or int(maxprice_filter.value)<=0:
                    ui.notify("Please enter a valid max price",color='red')
                    return
                max_price = int(max_price)  
            else:
                max_price = None
        except ValueError:
            max_price = None

        params = {
            'title':title_filter.value,
            'location':location_filter.value,
            'min_price':min_price,
            'max_price':max_price,
        }
        all_events_response = requests.get(f"{API_BASE_URL}/events/getall",headers=headers,params=params)
        registrations_response = requests.get(f"{API_BASE_URL}/registrations/NumRegistrations", headers=headers)

        if all_events_response.status_code==200 and registrations_response.status_code == 200:
            all_events = all_events_response.json() 
            registrations = registrations_response.json()
            event_registrations = {reg['event_id']:reg['count'] for reg in registrations}
            ui.notify("Events filtered successfully")
            
            all_events_container.clear()

            for event in all_events:
                reg_count = event_registrations.get(event['id'], 0)
                with all_events_container:
                    with ui.row().classes('events-container'):
                        with ui.card().classes('event-card'):
                            ui.html(f"<div class='profile-details'><strong>Event Title:</strong> {event['title']}</div>")
                            ui.html(f"<div class='profile-details'><strong>Event Description:</strong> {event['description']}</div>")
                            ui.html(f"<div class='profile-details'><strong>Event Location:</strong> {event['location']}</div>")
                            ui.html(f"<div class='profile-details'><strong>Event Price:</strong> {event['price']}</div>")
                            ui.html(f"<div class='profile-details'><strong>Event Date & Time:</strong> {event['event_datetime']}</div>")
                            ui.html(f"<div class='profile-details'><strong>Registrations: </strong> {reg_count}</div>")
                            ui.button(icon='info', on_click=lambda e=event: get_event_info(e)).classes('info-button')
                            with ui.row():
                                ui.button('Register',on_click=lambda e=event: register_for_event(e)).classes('register-button')
                                if current_user_role=="admin":
                                    ui.button(icon="edit",on_click=lambda e=event:edit_event(e)).classes('register-button')
        else:
            ui.notify("Failed to fetch events",color='red')
    
    if all_events_response.status_code==200:
        events=all_events_response.json()
        registrations = registrations_response.json()
        my_events = my_events_response.json()
        event_registrations = {reg['event_id']: reg['count'] for reg in registrations}
        
        with ui.column():
            with ui.row().classes('header'):
                ui.html(f"<div class='greeting'>Hello, {current_user}</div>")
                ui.button(icon='account_circle', on_click=lambda: ui.navigate.to('/profile')).classes('profile-icon')
                ui.button('Logout', on_click=logout, icon='logout')
            
            with ui.tabs() as Events:
                ui.tab('allevents', label="ALL Events")
                ui.tab('myevents', label="My Events")
    
            with ui.tab_panels(Events, value='allevents').classes('w-full'):
                with ui.tab_panel('allevents'):
                    with ui.row().classes('filters'):
                        title_filter = ui.input(label="Title Filter")
                        location_filter = ui.input(label="Location Filter")
                        minprice_filter = ui.input(label='MinPrice Filter')
                        maxprice_filter = ui.input(label='MaxPrice Filter')
                        ui.button("Search",on_click=search_events)

                    with ui.row().classes('events-container') as all_events_container:
                        for event in events:
                            reg_count = event_registrations.get(event['id'], 0)
                            with ui.card().classes('event-card'):
                                ui.html(f"<div class='profile-details'><strong>Event Title:</strong> {event['title']}</div>")
                                ui.html(f"<div class='profile-details'><strong>Event Description:</strong> {event['description']}</div>")
                                ui.html(f"<div class='profile-details'><strong>Event Location:</strong> {event['location']}</div>")
                                ui.html(f"<div class='profile-details'><strong>Event Price:</strong> {event['price']}</div>")
                                ui.html(f"<div class='profile-details'><strong>Event Date & Time:</strong> {event['event_datetime']}</div>")
                                ui.html(f"<div class='profile-details'><strong>Registrations:</strong> {reg_count}</div>")
                                ui.button(icon='info', on_click=lambda e=event: get_event_info(e)).classes('info-button')
                                with ui.row():
                                    ui.button('Register',on_click=lambda e=event: register_for_event(e)).classes('register-button')
                                    if current_user_role=="admin":
                                        ui.button(icon="edit",on_click=lambda e=event:edit_event(e)).classes('register-button')
                        
                        if current_user_role=="admin":
                            with ui.card().classes('create-event-card'):
                                ui.html(f"<div class='create-event-text'>Create New Event</div>")
                                ui.button(icon="add_circle_outline", on_click=lambda: ui.navigate.to('/create-event')).classes('register-button')
                        
                with ui.tab_panel('myevents'):
                    with ui.row().classes('events-container') as my_events_container:
                        unique_events = set()
                        for reg_event in my_events:
                            event = reg_event['event']
                            if event['id'] in unique_events:
                                continue
                            unique_events.add(event['id'])
                            with ui.card().classes('event-card'):
                                ui.html(f"<div class='profile-details'><strong>Event Title:</strong> {event['title']}</div>")
                                ui.html(f"<div class='profile-details'><strong>Event Description:</strong> {event['description']}</div>")
                                ui.html(f"<div class='profile-details'><strong>Event Location:</strong> {event['location']}</div>")
                                ui.html(f"<div class='profile-details'><strong>Event Price:</strong> {event['price']}</div>")
                                ui.html(f"<div class='profile-details'><strong>Event Date & Time:</strong> {event['event_datetime']}</div>")
                                with ui.row():
                                    ui.button('UnRegister', on_click=lambda e=event: unregister_event(e)).classes('register-button')
                                    if current_user_role=="admin":
                                        ui.button(icon="edit",on_click=lambda e=event:edit_event(e)).classes('register-button')
    else:
        ui.notify("Failed to fetch events",color='red')

@ui.page("/event_info")
def eventinfo():

    ui.add_head_html("""
    <style>
        .profile-card {
            max-width: 500px;
            margin: 20px auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .profile-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .profile-details {
            margin: 2px 0;
        }
        .registration-card{
                margin: 20px auto;
                border: 1px solid #ddd;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .event-info{
                margin: 20px auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
    </style>
    """)
     
    global jwt_token , selected_event , current_user_role 

    headers = {
        'Authorization':f'Bearer {jwt_token}'
    }   

    if selected_event is None:
        ui.navigate.to("/events") 
        return 

    if current_user_role=="admin":

        with ui.row().classes("event-info"):
            with ui.card().classes('profile-card'):
                ui.html(f"<div class='profile-title'>Event Details</div>")
                ui.html(f"<div class='profile-details'><strong>Event ID:</strong> {selected_event['id']}</div>")
                ui.html(f"<div class='profile-details'><strong>Event Title:</strong> {selected_event['title']}</div>")
                ui.html(f"<div class='profile-details'><strong>Event Description:</strong> {selected_event['description']}</div>")
                ui.html(f"<div class='profile-details'><strong>Event Location:</strong> {selected_event['location']}</div>")
                ui.html(f"<div class='profile-details'><strong>Event Price:</strong> {selected_event['price']}</div>")
                ui.html(f"<div class='profile-details'><strong>Event Date & Time:</strong> {selected_event['event_datetime']}</div>")
                ui.html(f"<div class='profile-details'><strong>Event Created At:</strong> {selected_event['event_created_at']}</div>")
                ui.html(f"<div class='profile-details'><strong>Event Owner ID:</strong> {selected_event['owner']['id']}</div>")
                ui.html(f"<div class='profile-details'><strong>Event Owner Name:</strong> {selected_event['owner']['name']}</div>")
                ui.html(f"<div class='profile-details'><strong>Event Owner Email:</strong> {selected_event['owner']['email']}</div>")

            with ui.card().classes('registration-card'):
                ui.html(f"<div class='profile-title'>Users Registered</div>")
                response = requests.get(f"{API_BASE_URL}/registrations/getall/{selected_event['id']}", headers=headers)
                if response.status_code == 200:
                    user_details = response.json()

                columns = [
            {'name': 'id', 'label': 'User Id', 'field': 'id', 'required': True,'sortable': True,'align': 'left'},
            {'name': 'name', 'label': 'Name', 'field': 'name', 'required': True},
            {'name': 'age', 'label': 'Age', 'field': 'age', 'required': True},
            {'name': 'gender', 'label': 'Gender', 'field': 'gender','required': True},
        ]
                ui.table(columns=columns,rows=user_details,row_key='id',pagination=5)
    else:
        with ui.card().classes('profile-card'):
            ui.html(f"<div class='profile-title'>Event Details</div>")
            ui.html(f"<div class='profile-details'><strong>Event ID:</strong> {selected_event['id']}</div>")
            ui.html(f"<div class='profile-details'><strong>Event Title:</strong> {selected_event['title']}</div>")
            ui.html(f"<div class='profile-details'><strong>Event Description:</strong> {selected_event['description']}</div>")
            ui.html(f"<div class='profile-details'><strong>Event Location:</strong> {selected_event['location']}</div>")
            ui.html(f"<div class='profile-details'><strong>Event Price:</strong> {selected_event['price']}</div>")
            ui.html(f"<div class='profile-details'><strong>Event Date & Time:</strong> {selected_event['event_datetime']}</div>")

@ui.page('/create-event')
def create_event_page():
    ui.add_head_html("""
    <style>
        .form-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin:auto;
        }
        .form-container {
            display: flex;
            flex-direction: column;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }                     
        .form-field {
            margin-bottom: 15px;
        }
        .form-field input {
            width: 100%;
        }
        .submit-button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
    """)

    global jwt_token

    if not jwt_token:
        ui.navigate.to('/')
        return

    def create_event():
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }

        location_value = location_input.value
        if not location_value:
            ui.notify("Location cannot be empty.", color='red')
            return
        
        title_value = title_input.value
        if not title_value:
            ui.notify("Title cannot be empty.", color='red')
            return
        
        description_value = description_input.value
        if not description_value:
            ui.notify("Description cannot be empty.", color='red')
            return

        try:
            price_value = int(price_input.value)
            if price_value <= 0:
                raise ValueError
        except ValueError:
            ui.notify("Price must be a positive integer.", color='red')
            return

        event_date_value = event_date.value
        event_time_value = event_time.value

        try:
            datetime.datetime.strptime(event_date_value, "%Y-%m-%d")
        except ValueError:
            ui.notify("Invalid date format. Use YYYY-MM-DD.", color='red')
            return

        try:
            datetime.datetime.strptime(event_time_value, "%H:%M")
        except ValueError:
            ui.notify("Invalid time format. Use HH:MM.", color='red')
            return

        combined_datetime = f"{event_date_value}T{event_time_value}:00"
        
        try:
            naive_datetime = datetime.datetime.strptime(combined_datetime, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            ui.notify("Invalid datetime format.", color='red')
            return
        
        local_tz = pytz.timezone("Asia/Kolkata")  
        localized_datetime = local_tz.localize(naive_datetime)
        
        current_datetime = datetime.datetime.now(pytz.UTC)
        if localized_datetime <= current_datetime:
            ui.notify("Event date and time must be in the future.", color='red')
            return

        utc_datetime = localized_datetime.astimezone(pytz.UTC)
        formatted_datetime = utc_datetime.isoformat()
        
        payload = {
            'title': title_input.value,
            'description': description_input.value,
            'location': location_value,
            'price': price_value,
            'event_datetime': formatted_datetime
        }
        response = requests.post(f"{API_BASE_URL}/events", headers=headers, json=payload)
        if response.status_code == 201:
            ui.notify("Event created successfully.")
            ui.navigate.to('/events')
        else:
            ui.notify(f"Failed to create event. Error: {response.text}", color='red')

    with ui.column().classes('form-wrapper'):
        with ui.column().classes('form-container'):
            title_input = ui.input(label='Title').classes('form-field')
            description_input = ui.input(label='Description').classes('form-field')
            location_input = ui.input(label='Location').classes('form-field')
            price_input = ui.input(label='Price').classes('form-field')

            with ui.row().classes('form-field'):
                with ui.input('Event Date') as event_date:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.date().bind_value(event_date):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                    with event_date.add_slot('append'):
                        ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')

            with ui.row().classes('form-field'):
                with ui.input('Event Time') as event_time:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.time().bind_value(event_time):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                    with event_time.add_slot('append'):
                        ui.icon('access_time').on('click', menu.open).classes('cursor-pointer')

            ui.button('Create Event', on_click=create_event).classes('submit-button')

@ui.page('/update-event')
def update_event_page():
    ui.add_head_html("""
    <style>
        .form-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin:auto;
        }
        .form-container {
            display: flex;
            flex-direction: column;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }                     
        .form-field {
            margin-bottom: 15px;
        }
        .form-field input {
            width: 100%;
        }
        .submit-button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
    """)
    global jwt_token, selected_event

    if not jwt_token or not selected_event:
        ui.navigate.to('/')
        return 
    
    def update_event():
        headers = {'Authorization':f'Bearer {jwt_token}'}

        location_value = location_input.value
        if not location_value:
            ui.notify("Location cannot be empty.", color='red')
            return
        
        title_value = title_input.value
        if not title_value:
            ui.notify("Title cannot be empty.", color='red')
            return
        
        description_value = description_input.value
        if not description_value:
            ui.notify("Description cannot be empty.", color='red')
            return

        try:
            price_value = int(price_input.value)
            if price_value <= 0:
                raise ValueError
        except ValueError:
            ui.notify("Price must be a positive integer.", color='red')
            return

        event_data_value = event_date.value
        event_time_value = event_time.value

        try:
            datetime.datetime.strptime(event_data_value, "%Y-%m-%d")
        except ValueError:
            ui.notify("Invalid date format. Use YYYY-MM-DD.", color='red')
            return

        try:
            datetime.datetime.strptime(event_time_value, "%H:%M")
        except ValueError:
            ui.notify("Invalid time format. Use HH:MM.", color='red')
            return

        combined_datetime = f"{event_data_value}T{event_time_value}:00"

        try:
            naive_datetime = datetime.datetime.strptime(combined_datetime, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            ui.notify("Invalid datetime format.", color='red')
            return

        local_tz = pytz.timezone('Asia/Kolkata')
        localized_datetime =  local_tz.localize(naive_datetime)
        current_datetime = datetime.datetime.now(pytz.UTC)
        if localized_datetime<=current_datetime:
            ui.notify("Event date and time must be in the future.",color='red')
            return
        
        utc_datetime = localized_datetime.astimezone(pytz.UTC)
        formatted_datetime = utc_datetime.isoformat()

        payload = {
            'title':title_input.value,
            'description':description_input.value,
            'location':location_value,
            'price':price_value,
            'event_datetime':formatted_datetime
        }

        response = requests.put(f"{API_BASE_URL}/events/{selected_event['id']}",headers=headers,json=payload)
        if response.status_code==200:
            ui.notify("Event Updated Successfully")
            ui.navigate.to('/events')
        else:
            ui.notify(f"Failed to update event. Error: {response.text}", color='red')
        
    with ui.column().classes('form-wrapper'):
        with ui.column().classes('form-container'):
            title_input = ui.input(label='Title',value=selected_event['title']).classes('form-field')
            description_input = ui.input(label="Description",value=selected_event['description']).classes('form-field')
            location_input = ui.input(label='Location',value=selected_event['location']).classes('form-field')
            price_input = ui.input(label='Price',value=selected_event['price']).classes('form-field')

            event_datetime = datetime.datetime.strptime(selected_event['event_datetime'],"%Y-%m-%dT%H:%M:%S%z")
            event_date_value = event_datetime.date().isoformat()
            event_time_value = event_datetime.time().isoformat()[:5]

            with ui.row().classes('form-field'):
                with ui.input('Event Date', value=event_date_value) as event_date:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.date().bind_value(event_date):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                    with event_date.add_slot('append'):
                        ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')

            with ui.row().classes('form-field'):
                with ui.input('Event Time', value=event_time_value) as event_time:
                    with ui.menu().props('no-parent-event') as menu:
                        with ui.time().bind_value(event_time):
                            with ui.row().classes('justify-end'):
                                ui.button('Close', on_click=menu.close).props('flat')
                    with event_time.add_slot('append'):
                        ui.icon('access_time').on('click', menu.open).classes('cursor-pointer')
            
            ui.button('Update Event',on_click=update_event).classes('submit-button')

@ui.page('/register')
def registration_page():
    ui.add_head_html('''
    <style>
        .custom-input {
            margin-bottom: 10px;
            width: calc(33% - 10px);
        }
        .custom-input-button {
            margin-bottom: 10px;
            width: 100%;
        }
        .registration-row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .register-button-container {
            display: flex;
            justify-content: space-between;
            width: 100%;
        }
        .registration-container {
            max-width: 600px;
            margin: 20px auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .profile-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .profile-details {
            margin: 2px 0;
        }
    </style>
    ''')

    global selected_event

    if not selected_event:
        ui.notify("No event selected", color="red")
        ui.navigate.to('/events')
        return

    registration_entries = []

    def add_registration_entry():
        if registration_entries:
            last_entry = registration_entries[-1]
            if not last_entry['name'].value:
                ui.notify("Please input name of user",color="red")
                return 
            if not last_entry['age'].value or not last_entry['age'].value.isdigit() or int(last_entry['age'].value)<=0:
                ui.notify("Please input age of user",color="red")
                return 
            if not last_entry['gender'].value:
                ui.notify("Please input gender of user",color="red")
                return
            
        with entries_container:
            with ui.row().classes('registration-row'):
                name = ui.input(label='Name').classes('custom-input')
                age = ui.input(label='Age').classes('custom-input')
                gender = ui.select(['Male', 'Female', 'Other'], label='Gender').classes('custom-input')
                registration_entries.append({
                    'name': name,
                    'age': age,
                    'gender': gender
                })

    def submit_registration():
        for entry in registration_entries:
            if not entry['name'].value:
                ui.notify("Please input name of all users", color="red")
                return 
            if not entry['age'].value or not entry['age'].value.isdigit() or int(entry['age'].value) <= 0:
                ui.notify("Please input a valid age for all users (greater than 0)", color="red")
                return 
            if not entry['gender'].value:
                ui.notify("Please input gender of all users", color="red")
                return 
            
        headers = {'Authorization': f'Bearer {jwt_token}'}
        registration_details = {
            'event_id': selected_event['id'],
            'registrations': [
                {
                    'name': entry['name'].value,
                    'age': int(entry['age'].value),
                    'gender': entry['gender'].value
                } for entry in registration_entries
            ]
        }
        response = requests.post(f"{API_BASE_URL}/registrations", json=registration_details, headers=headers)
        
        if response.status_code == 201:
            ui.notify(f"Successfully registered for event: {selected_event['title']}")
            ui.navigate.to('/events')
        elif response.status_code == 400:
            error_detail = response.json().get('detail')
            if error_detail == "Already registered for this event with the same details":
                ui.notify("Already registered for this event with the same details", color="red")
            elif error_detail == "Invalid gender":
                ui.notify("Invalid gender provided in one of the entries", color="red")
            else:
                ui.notify("Failed to register for the event due to invalid input", color="red")
        else:
            ui.notify("Failed to register for the event", color="red")

    with ui.column().classes('registration-container'):
        ui.html(f"<div class='profile-title'>Event Details</div>")
        ui.html(f"<div class='profile-details'><strong>Event ID:</strong> {selected_event['id']}</div>")
        ui.html(f"<div class='profile-details'><strong>Event Title:</strong> {selected_event['title']}</div>")
        ui.html(f"<div class='profile-details'><strong>Event Description:</strong> {selected_event['description']}</div>")
        ui.html(f"<div class='profile-details'><strong>Event Location:</strong> {selected_event['location']}</div>")
        ui.html(f"<div class='profile-details'><strong>Event Price:</strong> {selected_event['price']}</div>")
        ui.html(f"<div class='profile-details'><strong>Event Date & Time:</strong> {selected_event['event_datetime']}</div>")
        
        with ui.column() as entries_container:
            add_registration_entry()
        
        with ui.row().classes('register-button-container'):
            ui.button('Add Another Entry', on_click=add_registration_entry).classes('custom-input-button')
            ui.button('Submit Registration', on_click=submit_registration).classes('custom-input-button')

ui.add_head_html("""
<style>
    .login-container {
        max-width: 500px;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        background-color: white;
        margin: auto;
        margin-top: 30px;
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
        width: 100%;
    }
    .custom-button {
        width: 100%;
        background-color: #007bff;
        color: white;
    }
</style>
""")

with ui.card().classes('login-container'):
    # ui.markdown("""
    # <img src="https://panchkoshawellbeing.in/assets/images/logo-1.png" alt="PanchkoshWellbeing" class="logo">
    # """)
    with ui.tabs() as logintabs:
        ui.tab('login', label="Login")
        ui.tab('signup', label="SignUp")
    with ui.tab_panels(logintabs, value='login').classes('w-full'):
        with ui.tab_panel('login'):
            # ui.markdown("### Login")
            global username, password
            username = ui.input(label='Email').classes('custom-input')
            password = ui.input(label='Password', password=True).classes('custom-input')
            ui.button('Login', on_click=login).classes('custom-button')
        
        with ui.tab_panel('signup'):
            # ui.markdown("### Sign Up")
            with ui.tabs() as signtabs:
                ui.tab('user', label="User")
                ui.tab('admin', label="Admin")
            with ui.tab_panels(signtabs, value='user').classes('w-full'):
                with ui.tab_panel('user'):
                    global user_email, user_password , user_name
                    user_name = ui.input(label='Name').classes('custom-input')
                    user_email = ui.input(label='Email').classes('custom-input')
                    user_password = ui.input(label='Password', password=True).classes('custom-input')
                    ui.button('Sign Up as User', on_click=register_user).classes('custom-button')
                with ui.tab_panel('admin'):
                    global admin_email, admin_password , admin_name
                    admin_name = ui.input(label='Name').classes('custom-input')
                    admin_email = ui.input(label='Email').classes('custom-input')
                    admin_password = ui.input(label='Password', password=True).classes('custom-input')
                    ui.button('Sign Up as Admin', on_click=register_admin).classes('custom-button')

@ui.page('/profile')
def profile_page():
    global jwt_token, current_user
    
    headers = {'Authorization': f'Bearer {jwt_token}'}

    response = requests.get(f"{API_BASE_URL}/users/{username.value}", headers=headers)
    if response.status_code == 200:
        user_details = response.json()
    else:
        ui.notify("Failed to fetch user details", color="red")
        ui.navigate.to('/events')
        return

    ui.add_head_html("""
    <style>
        .profile-card {
            max-width: 500px;
            margin: 20px auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .profile-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .profile-details {
            margin: 10px 0;
        }
    </style>
    """)

    with ui.card().classes('profile-card'):
        ui.html(f"<div class='profile-title'>Profile</div>")
        ui.html(f"<div class='profile-details'><strong>Name:</strong> {user_details['name']}</div>")
        ui.html(f"<div class='profile-details'><strong>Email:</strong> {user_details['email']}</div>")
        ui.html(f"<div class='profile-details'><strong>Role:</strong> {user_details['role']}</div>")
        ui.html(f"<div class='profile-details'><strong>Profile Created At:</strong> {user_details['created_at']}</div>")

ui.run()



