import sys
import os

# Add the parent directory (HMS/) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from datetime import datetime, date, time
from backend import db_api

# ----------------- Session State Setup -----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_type" not in st.session_state:
    st.session_state.user_type = None
if "patient_name" not in st.session_state:
    st.session_state.patient_name = ""
if "doctor_name" not in st.session_state:
    st.session_state.doctor_name = ""
if "admin_name" not in st.session_state:
    st.session_state.admin_name = ""
if "page" not in st.session_state:
    st.session_state.page = "home"
if "appointments" not in st.session_state:
    st.session_state.appointments = []
if "cancel_confirm" not in st.session_state:
    st.session_state.cancel_confirm = {}
if "medical_records" not in st.session_state:
    st.session_state.medical_records = []
if "bills" not in st.session_state:
    st.session_state.bills = []

# ----------------- Custom CSS Styling -----------------
st.markdown("""
    <style>
        body {
            background-color: #F5F7FA;
            font-family: 'Poppins', sans-serif;
        }
        header {
            background: linear-gradient(90deg, #A8D5BA, #BFD9E8);
            padding: 40px 20px;
            text-align: center;
            color: #2C3E50;
            border-bottom: 4px solid #A8D5BA;
        }
        h1, h2 {
            margin: 0;
        }
        .sub-title {
            font-size: 20px;
            color: #5D6D7E;
        }
        .logo {
            width: 100px;
            margin: 10px auto;
            display: block;
        }
        .stButton>button {
            background-color: #4A90E2 !important;
            color: white !important;
            border-radius: 5px !important;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------- Header with Logo -----------------
def header():
    st.markdown(""" 
        <header>
            <img src="https://cdn-icons-png.flaticon.com/128/11514/11514557.png" class="logo" alt="Hospital Logo"/>
            <h1>Expert Healthcare, Closer to You</h1>
            <p class="sub-title">Compassionate, Modern, Trusted Care for All</p>
        </header>
    """, unsafe_allow_html=True)

# ----------------- Navigation Menus -----------------
def patient_navigation():
    st.sidebar.title(f"Welcome, {st.session_state.patient_name}!")
    menu = st.sidebar.radio("Navigation", ["Home", "Appointments", "Bills", "Medical Records", "Logout"])
    if menu == "Home":
        st.session_state.page = "home"
    elif menu == "Appointments":
        appointment_option = st.sidebar.radio("Appointments", ["Upcoming Appointments", "Book Appointment", "Cancel Appointment"])
        st.session_state.page = appointment_option.lower().replace(" ", "_")
    elif menu == "Bills":
        st.session_state.page = "billing"
    elif menu == "Medical Records":
        st.session_state.page = "medical_records"
    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.page = "home"
        st.rerun()

def doctor_navigation():
    st.sidebar.title(f"Welcome, {st.session_state.doctor_name}!")
    menu = st.sidebar.radio("Navigation", ["Home", "Schedule", "Patient History", "Logout"])
    st.session_state.page = menu.lower().replace(" ", "_")
    if menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.page = "home"
        st.rerun()

def admin_navigation():
    st.sidebar.title(f"Welcome, {st.session_state.admin_name}!")
    menu = st.sidebar.radio("Navigation", [
        "Home", "Add Prescription", "Add Test Result", 
        "Allocate Room", "Deallocate Room", "Generate Bill", "Logout"
    ])
    st.session_state.page = menu.lower().replace(" ", "_")
    if menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.page = "home"
        st.rerun()

# ----------------- Patient Interface -----------------
def patient_interface():
    patient_navigation()
    if st.session_state.page == "home":
        st.title(f"Welcome, {st.session_state.patient_name}!")
        st.subheader("Your healthcare at your fingertips.")
    elif st.session_state.page == "upcoming_appointments":
        st.title("Upcoming Appointments")
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Accepted"])
        
        # Fetch appointments from database
        if "appointments" not in st.session_state or not st.session_state.appointments:
            st.session_state.appointments = db_api.get_patient_appointments(st.session_state.patient_name)
        
        appts = [
            a for a in st.session_state.appointments 
            if a["patient"] == st.session_state.patient_name and 
            (status_filter == "All" or a["status"] == status_filter)
        ]
        
        if appts:
            for a in appts:
                st.write(f"📅 {a['date']} {a['time']} {a['doctor']} - Status: {a['status']}")
        else:
            st.info("No upcoming appointments.")
    elif st.session_state.page == "book_appointment":
        st.title("Book an Appointment")
        doctor = st.selectbox("Select Doctor", ["Dr. Smith", "Dr. Johnson", "Dr. Lee"])
        date_input = st.date_input("Select Date")
        time_input = st.time_input("Select Time")
        
        if st.button("Confirm Appointment"):
            success, message = db_api.book_appointment(
                st.session_state.patient_name, 
                doctor, 
                str(date_input), 
                str(time_input)
            )
            
            if success:
                st.success(message)
                # Refresh appointments list
                st.session_state.appointments = db_api.get_patient_appointments(st.session_state.patient_name)
            else:
                st.error(message)
    elif st.session_state.page == "cancel_appointment":
        st.title("Cancel an Appointment")
        
        # Refresh appointments from database
        st.session_state.appointments = db_api.get_patient_appointments(st.session_state.patient_name)
        
        appts = [a for a in st.session_state.appointments if a["patient"] == st.session_state.patient_name]
        if appts:
            for i, a in enumerate(appts):
                key = f"{a['doctor']}-{a['date']}-{a['time']}"
                if key not in st.session_state.cancel_confirm:
                    st.session_state.cancel_confirm[key] = False
                if not st.session_state.cancel_confirm[key]:
                    if st.button(f"Cancel Appointment with {a['doctor']} on {a['date']} at {a['time']} - {i}"):
                        st.session_state.cancel_confirm[key] = True
                        st.rerun()
                else:
                    st.warning("Are you sure you want to cancel this appointment?")
                    col1, col2 = st.columns(2)
                    if col1.button("Yes, Cancel", key=f"yes_{i}"):
                        success, message = db_api.cancel_appointment(
                            st.session_state.patient_name,
                            a['doctor'],
                            a['date'],
                            a['time']
                        )
                        
                        if success:
                            st.success(message)
                            # Refresh appointments list
                            st.session_state.appointments = db_api.get_patient_appointments(st.session_state.patient_name)
                            del st.session_state.cancel_confirm[key]
                            st.rerun()
                        else:
                            st.error(message)
                    if col2.button("No", key=f"no_{i}"):
                        st.session_state.cancel_confirm[key] = False
        else:
            st.info("No active appointments.")
          
    elif st.session_state.page == "billing":
        st.title("Your Bills")
        
        # Fetch bills from database
        bills = db_api.view_bills(st.session_state.patient_name)
        
        if bills:
            # Create a nice table for bills
            bill_data = {
                "Bill ID": [],
                "Date": [],
                "Amount (₹)": [],
                "Generated By": [],
                "Status": []
            }
            
            for bill in bills:
                bill_data["Bill ID"].append(bill['B_ID'])
                bill_data["Date"].append(bill.get('Bill_Date', 'N/A'))
                bill_data["Amount (₹)"].append(f"{bill['Amount']:.2f}")
                bill_data["Generated By"].append(bill.get('Generated_By', 'Hospital Staff'))
                
                # Determine payment status
                if bill['Paid_Amount'] >= bill['Amount']:
                    bill_data["Status"].append("Paid")
                else:
                    remaining = bill['Amount'] - bill['Paid_Amount']
                    bill_data["Status"].append(f"{remaining:.2f} Due")
            
            # Display the table
            st.table(bill_data)
            
            # Add detailed view
            st.subheader("Bill Details")
            for i, bill in enumerate(bills):
                with st.expander(f"Bill #{bill['B_ID']} Details"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Bill ID:** {bill['B_ID']}")
                        st.markdown(f"**Date:** {bill.get('Bill_Date', 'N/A')}")
                        st.markdown(f"**Generated By:** {bill.get('Generated_By', 'Hospital Staff')}")
                    
                    with col2:
                        st.markdown(f"**Total Amount:** ₹{bill['Amount']:.2f}")
                        st.markdown(f"**Paid Amount:** ₹{bill.get('Paid_Amount', 0):.2f}")
                        remaining = bill['Amount'] - bill.get('Paid_Amount', 0)
                        status = "Paid" if remaining <= 0 else f"₹{remaining:.2f} Due"
                        st.markdown(f"**Status:** {status}")
                    
                    st.markdown("### Services")
                    if 'Treatments' in bill and bill['Treatments']:
                        for idx, treatment in enumerate(bill['Treatments'], 1):
                            st.markdown(f"{idx}. {treatment}")
                    else:
                        st.markdown("- General hospital services")
                    
                    st.download_button(
                        label="Download Invoice",
                        data=f"Invoice #{bill['B_ID']} for {st.session_state.patient_name}",
                        file_name=f"invoice_{bill['B_ID']}.txt",
                        mime="text/plain"
                    )
        else:
            st.info("You don't have any bills yet.")

    elif st.session_state.page == "medical_records":
        st.title("Medical Records")
        
        # Fetch medical records from database using the new function
        st.session_state.medical_records = db_api.view_medical_records(st.session_state.patient_name)
        
        if st.session_state.medical_records:
            st.subheader("Your Medical Records")
            for record in st.session_state.medical_records:
                with st.expander(f"Record #{record['Rec_ID']} - Dr. {record['Doctor']}"):
                    st.write("**Treatment:**")
                    st.write(record['Treatment'])
        else:
            st.info("No medical records available.")

# ----------------- Doctor Interface -----------------
def doctor_interface():
    doctor_navigation()
    if st.session_state.page == "home":
        st.title(f"Welcome, {st.session_state.doctor_name}!")
    elif st.session_state.page == "schedule":
        st.title("Appointments Schedule")
        
        
        # Fetch appointments from database
        appointments = db_api.get_doctor_appointments(st.session_state.doctor_name)
        
        if appointments:
            for i, a in enumerate(appointments):
                with st.expander(f"{a['date']} at {a['time']} - {a['patient']} ({a['status']})"):
                    if a["status"] == "Pending":
                        if st.button(f"Accept - {i}"):
                            success, message = db_api.update_appointment_status(
                                st.session_state.doctor_name,
                                a['patient'],
                                a['date'],
                                a['time'],
                                "Accepted"
                            )
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                        if st.button(f"Cancel - {i}"):
                            success, message = db_api.cancel_appointment(
                                a['patient'],
                                st.session_state.doctor_name,
                                a['date'],
                                a['time']
                            )
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    else:
                        st.success("Appointment accepted.")
        else:
            st.info("No appointments found.")
    elif st.session_state.page == "patient_history":
        st.title("Patient History Lookup")
        patient_id = st.text_input("Enter Patient ID")

        if st.button("Fetch History"):
            if patient_id:
                records, tests = db_api.get_patient_history(int(patient_id))

                st.subheader("Prescriptions")
                if records:
                    for rec in records:
                        st.markdown(f"- **Doctor**: {rec['Doctor']}  \n  **Treatment**: {rec['Treatment']}")
                else:
                    st.info("No prescriptions found.")

                st.subheader("Test Results")
                if tests:
                    for test in tests:
                        st.markdown(f"- **{test['Test_type']}**: {test['Result']}")
                else:
                    st.info("No test results found.")
            else:
                st.error("Please enter a valid Patient ID.")

    

# ----------------- Admin Interface -----------------
def admin_interface():
    admin_navigation()
    if st.session_state.page == "home":
        st.title(f"Welcome, {st.session_state.admin_name}!")
    elif st.session_state.page == "add_prescription":
        st.title("Add Prescription")
        
        # Modified to use the new add_prescription function
        with st.form("add_prescription_form"):
            patient_id = st.text_input("Patient ID")
            doctor_id = st.text_input("Doctor ID")
            treatment = st.text_area("Prescribed Treatment")
            submitted = st.form_submit_button("Add Prescription")
            
            if submitted:
                if patient_id and doctor_id and treatment:
                    
                    if 'admin_id' in st.session_state:
                        admin_id = st.session_state.admin_id
                        success, message = db_api.add_prescription(int(patient_id), doctor_id, treatment, admin_id)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                else:
                    st.error("Please fill all the fields. ")
                    

    elif st.session_state.page == "add_test_result":
        st.title("Add Test Result")
        with st.form("test_result_form"):
            patient_id = st.text_input("Patient ID")
            test_type = st.text_input("Test Type")
            result = st.text_area("Test Result")
            submitted = st.form_submit_button("Submit")
            if submitted:
                if patient_id and test_type and result:
                    success, message = db_api.add_test_result(int(patient_id), test_type, result)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please fill all fields.")


    elif st.session_state.page == "allocate_room":
        st.title("Allocate Room")
        
        # Display available rooms
        rooms = db_api.get_available_rooms()
        if rooms:
            st.subheader("Available Rooms")
            for r in rooms:
                st.markdown(
                    f"**Room ID:** {r['R_ID']} | **Type:** {r['RType']} | "
                    f"**Capacity:** {r['Capacity']} | **Current:** {r['Current_Patients']} | "
                    f"**Available:** {'Yes' if r['Availability'] == 1 else 'No'}"
                )
        else:
            st.info("No rooms available.")
        
        # Create a key for the form to ensure it's uniquely identified
        allocate_form = st.form(key="allocate_room_form")
        with allocate_form:
            patient_id = st.text_input("Enter Patient ID", key="allocate_patient_id")
            room_id = st.text_input("Enter Room ID", key="allocate_room_id")
            submit_button = st.form_submit_button("Allocate")
        
        # Handle form submission outside the form context
        if submit_button:
            if patient_id and room_id:
                # Store IDs in variables to ensure they're captured correctly
                p_id = int(patient_id)
                r_id = int(room_id)
                success, msg = db_api.allocate_room(p_id, r_id)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.error("Please enter both Patient ID and Room ID.")

    elif st.session_state.page == "deallocate_room":
        st.title("Deallocate Room")
        
        # Create a key for the form to ensure it's uniquely identified
        deallocate_form = st.form(key="deallocate_room_form")
        with deallocate_form:
            patient_id = st.text_input("Enter Patient ID", key="deallocate_patient_id")
            room_id = st.text_input("Enter Room ID", key="deallocate_room_id")
            submit_button = st.form_submit_button("Deallocate")
        
        # Handle form submission outside the form context
        if submit_button:
            if patient_id and room_id:
                # Store IDs in variables to ensure they're captured correctly
                p_id = int(patient_id)
                r_id = int(room_id)
                success, msg = db_api.deallocate_room(p_id, r_id)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.error("Please enter both Patient ID and Room ID.")

    elif st.session_state.page == "generate_bill":
        st.title("Generate Bill")
        
        # Modified to use the new generate_bill function
        with st.form("generate_bill_form"):
            patient_id = st.text_input("Patient ID")
            amount = st.number_input("Amount", min_value=0.0)
            submitted = st.form_submit_button("Generate")
            
            if submitted:
                if patient_id and amount > 0:
                   
                    if 'admin_id' in st.session_state:
                        admin_id = st.session_state.admin_id
                        success, message = db_api.generate_bill(int(patient_id), float(amount), admin_id)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.error("Please enter a valid Patient ID and amount.")
                   

# ----------------- Login & Signup -----------------
def login_page(role="Patient"):
    st.title(f"{role} Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username and password:
            if role == "Patient":
                success, user_data = db_api.patient_login(username, password)
            else:# Doctor or Admin
                if role == "Doctor":
                    success, user_data = db_api.staff_login(username, password, role)
                else:
                    success, admin_name, admin_id = db_api.staff_login(username, password, role)
                
            if success:
                st.session_state.logged_in = True
                st.session_state.user_type = role
                
                if role == "Patient":
                    st.session_state.patient_name = user_data
                    # Get appointments
                    st.session_state.appointments = db_api.get_patient_appointments(user_data)
                    st.success(f"Welcome back, {user_data} ({role})!")
                elif role == "Doctor":
                    st.session_state.doctor_name = user_data
                    st.success(f"Welcome back, {user_data} ({role})!")
                elif role == "Admin":
                    st.session_state.admin_name = admin_name
                    st.session_state.admin_id = admin_id
                    st.success(f"Welcome back, {admin_name} ({role})!")
                    
                st.rerun()
            else:
                if(role=="Admin"):
                    st.error(admin_name,admin_id)
                else:
                    st.error(user_data)  # Display error message
        else:
            st.error("Please enter both username and password.")

def signup_page():
    st.title("Patient Sign-Up")
    username = st.text_input("Username")  
    password = st.text_input("Password", type="password")  
    namee = st.text_input("Full Name")
    contact = st.text_input("Contact Number")
    age = st.number_input("Age", min_value=1, max_value=120)
    gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"])
    
    if st.button("Register"):
        if username and password and namee and contact and age and gender != "Select":
            success, message = db_api.patient_signup(username, password, namee, contact, age, gender)
            
            if success:
                st.success(message)
                st.session_state.logged_in = True
                st.session_state.user_type = "Patient"
                st.session_state.patient_name = namee
                st.rerun()
            else:
                st.error(message)
        else:
            st.error("Please fill all the fields.")

# ----------------- Main Function -----------------
def main():
    header()
    if st.session_state.logged_in:
        if st.session_state.user_type == "Patient":
            patient_interface()
        elif st.session_state.user_type == "Doctor":
            doctor_interface()
        elif st.session_state.user_type == "Admin":
            admin_interface()
    else:
        user_type = st.selectbox("User Type", ["Select", "Patient", "Doctor", "Admin"])
        if user_type == "Patient":
            option = st.radio("Are you a new patient or already registered?", ["New Patient", "Already Registered"])
            if option == "New Patient":
                signup_page()
            else:
                login_page(role="Patient")
        elif user_type in ["Doctor", "Admin"]:
            login_page(role=user_type)

# ----------------- Run App -----------------
if __name__ == "__main__":
    main()
