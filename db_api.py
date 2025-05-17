import mysql.connector
import streamlit as st
import hashlib
import random
from datetime import datetime

# Database connection function
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="samyu@8306",  # Replace with your MySQL password
            database="hms"
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Error connecting to the database: {err}")
        return None

# Function to hash passwords securely
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Patient Login API
def patient_login(username, password):
    connection = get_db_connection()
    if not connection:
        return False, "Database connection error"
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get hashed password for the username
        cursor.execute("SELECT id, pwd FROM patient_users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            return False, "Invalid username or password"
        
        # Verify password
        hashed_password = hash_password(password)
        if hashed_password != user['pwd']:
            return False, "Invalid username or password"
        
        # Get patient details
        cursor.execute("SELECT PName FROM patient WHERE P_ID = %s", (user['id'],))
        patient = cursor.fetchone()
        
        if patient:
            return True, patient['PName']
        else:
            return True, username  # If patient record not found, use username
        
    except mysql.connector.Error as err:
        return False, f"Database error: {err}"
    finally:
        cursor.close()
        connection.close()

# Staff Login API (Doctor and Admin)
def staff_login(username, password, role):
    connection = get_db_connection()
    if not connection:
        return False, "Database connection error"
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get hashed password for the username
        cursor.execute("SELECT id, pwd FROM emp_users WHERE username = %s", (username,))
        user = cursor.fetchone()

        
        if not user:
            return False, "Invalid username or password"
        
        # Verify password
        hashed_password = hash_password(password)

        
        if hashed_password != user['pwd']:
            return False, "Invalid username or password"
        
        # Get staff details based on role
        if role == "Doctor":
            cursor.execute("SELECT DName FROM doctor WHERE E_ID = %s", (user['id'],))
            staff = cursor.fetchone()
        else:  # Admin
            cursor.execute("SELECT AName FROM admin WHERE E_ID = %s", (user['id'],))
            staff = cursor.fetchone()
        
        if staff:
            if role=="Doctor":
                return True, staff['DName']
            else:
                return True, staff['AName'], user['id']

        else:
            return True, username  # If staff record not found, use username
        
    except mysql.connector.Error as err:
        return False, f"Database error: {err}"
    finally:
        cursor.close()
        connection.close()


# Patient Signup API
def patient_signup(username, password, name, contact, age, gender):
    connection = get_db_connection()
    if not connection:
        return False, "Database connection error"
    
    try:
        cursor = connection.cursor()
        
        # Check if username already exists
        cursor.execute("SELECT id FROM patient_users WHERE username = %s", (username,))
        if cursor.fetchone():
            return False, "Username already exists"
        
        # Generate a unique P_ID for the patient
        # p_id = random.randint(1000, 9999)
        # cursor.execute("SELECT P_ID FROM patient WHERE P_ID = %s", (p_id,))
        # while cursor.fetchone():
        #     p_id = random.randint(1000, 9999)
        
        # Calculate DOB from age
        current_year = datetime.now().year
        birth_year = current_year - int(age)
        dob = f"{birth_year}-01-01"  # Default to January 1st of birth year
        
        # Hash the password
        hashed_password = hash_password(password)
                
        # # Insert into patient_users table
        # cursor.execute(
        #     "INSERT INTO patient_users (username, pwd) VALUES (%s, %s)",
        #     (username, hashed_password)
        # )
        
        # p_id = cursor.lastrowid

        # # Insert into patient table
        # cursor.execute(
        #     "INSERT INTO patient (P_ID, DOB, PName, Gender, Height, Weight) VALUES (%s, %s, %s, %s, %s, %s)",
        #     (p_id, dob, name, gender, 0.0, 0.0)  # Default height and weight
        # )

        
        # # Insert into patient_mob_no table
        # if contact:
        #     cursor.execute(
        #         "INSERT INTO patient_mob_no (P_ID, Mob_no) VALUES (%s, %s)",
        #         (p_id, int(contact))
        #     )
        cursor.execute(
            "INSERT INTO patient_users (username, pwd) VALUES (%s, %s)",
            (username, hashed_password)
        )
        p_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO patient (P_ID, DOB, PName, Gender, Height, Weight) VALUES (%s, %s, %s, %s, %s, %s)",
            (p_id, dob, name, gender, 0.0, 0.0)
        )

        if contact:
            cursor.execute(
                "INSERT INTO patient_mob_no (P_ID, Mob_no) VALUES (%s, %s)",
                (p_id, int(contact))
            )

        
        # Commit transaction
        connection.commit()
        return True, "Registration successful"
        
    except mysql.connector.Error as err:
        connection.rollback()
        return False, f"Database error: {err}"
    finally:
        cursor.close()
        connection.close()

# Function to get patient appointments
def get_patient_appointments(patient_name):
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # First get the patient ID
        cursor.execute("SELECT P_ID FROM patient WHERE PName = %s", (patient_name,))
        patient = cursor.fetchone()
        
        if not patient:
            return []
        
        # Get all appointments for this patient
        cursor.execute("""
            SELECT a.dates, a.times, d.DName, a.cur_status
            FROM appointments a
            JOIN doctor d ON a.did = d.E_ID
            WHERE a.pid = %s
        """, (patient['P_ID'],))
        
        appointments = []
        for row in cursor.fetchall():
            status = "Pending" if row['cur_status'] == 0 else "Accepted"
            appointments.append({
                "patient": patient_name,
                "doctor": row['DName'],
                "date": str(row['dates']),
                "time": str(row['times']),
                "status": status
            })
        
        return appointments
        
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Function to book an appointment
def book_appointment(patient_name, doctor_name, date_str, time_str):
    connection = get_db_connection()
    if not connection:
        return False, "Database connection error"
    
    try:
        cursor = connection.cursor()
        
        # Get patient ID
        cursor.execute("SELECT P_ID FROM patient WHERE PName = %s", (patient_name,))
        patient = cursor.fetchone()
        
        if not patient:
            return False, "Patient not found"
        
        # Get doctor ID
        cursor.execute("SELECT E_ID FROM doctor WHERE DName = %s", (doctor_name,))
        doctor = cursor.fetchone()
        
        if not doctor:
            return False, "Doctor not found"
        
        # Insert new appointment
        cursor.execute(
            "INSERT INTO appointments (pid, did, dates, times, cur_status) VALUES (%s, %s, %s, %s, %s)",
            (patient[0], doctor[0], date_str, time_str, 0)  # 0 means pending
        )
        
        connection.commit()
        return True, "Appointment booked successfully"
        
    except mysql.connector.Error as err:
        connection.rollback()
        return False, f"Database error: {err}"
    finally:
        cursor.close()
        connection.close()

# Function to cancel an appointment
def cancel_appointment(patient_name, doctor_name, date_str, time_str):
    connection = get_db_connection()
    if not connection:
        return False, "Database connection error"
    
    try:
        cursor = connection.cursor()
        
        # Get patient ID
        cursor.execute("SELECT P_ID FROM patient WHERE PName = %s", (patient_name,))
        patient = cursor.fetchone()
        
        if not patient:
            return False, "Patient not found"
        
        # Get doctor ID
        cursor.execute("SELECT E_ID FROM doctor WHERE DName = %s", (doctor_name,))
        doctor = cursor.fetchone()
        
        if not doctor:
            return False, "Doctor not found"
        
        # Delete the appointment
        cursor.execute(
            "DELETE FROM appointments WHERE pid = %s AND did = %s AND dates = %s AND times = %s",
            (patient[0], doctor[0], date_str, time_str)
        )
        
        if cursor.rowcount == 0:
            return False, "Appointment not found"
        
        connection.commit()
        return True, "Appointment cancelled successfully"
        
    except mysql.connector.Error as err:
        connection.rollback()
        return False, f"Database error: {err}"
    finally:
        cursor.close()
        connection.close()

# Function to get doctor appointments
def get_doctor_appointments(doctor_name, search_query=None):
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # First get the doctor ID
        cursor.execute("SELECT E_ID FROM doctor WHERE DName = %s", (doctor_name,))
        doctor = cursor.fetchone()
        
        if not doctor:
            return []
        
        # Get all appointments for this doctor
        query = """
            SELECT a.dates, a.times, p.PName, a.cur_status
            FROM appointments a
            JOIN patient p ON a.pid = p.P_ID
            WHERE a.did = %s
        """
        
        params = [doctor['E_ID']]
        
        if search_query:
            query += " AND (p.PName LIKE %s OR a.dates = %s)"
            params.extend([f"%{search_query}%", search_query])
        
        cursor.execute(query, params)
        
        appointments = []
        for row in cursor.fetchall():
            status = "Pending" if row['cur_status'] == 0 else "Accepted"
            appointments.append({
                "patient": row['PName'],
                "doctor": doctor_name,
                "date": str(row['dates']),
                "time": str(row['times']),
                "status": status
            })
        
        return appointments
        
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Function to update appointment status
def update_appointment_status(doctor_name, patient_name, date_str, time_str, new_status):
    connection = get_db_connection()
    if not connection:
        return False, "Database connection error"
    
    try:
        cursor = connection.cursor()
        
        # Get doctor ID
        cursor.execute("SELECT E_ID FROM doctor WHERE DName = %s", (doctor_name,))
        doctor = cursor.fetchone()
        
        if not doctor:
            return False, "Doctor not found"
        
        # Get patient ID
        cursor.execute("SELECT P_ID FROM patient WHERE PName = %s", (patient_name,))
        patient = cursor.fetchone()
        
        if not patient:
            return False, "Patient not found"
        
        # Update status (0 = pending, 1 = accepted)
        status_value = 1 if new_status == "Accepted" else 0
        
        cursor.execute(
            "UPDATE appointments SET cur_status = %s WHERE pid = %s AND did = %s AND dates = %s AND times = %s",
            (status_value, patient[0], doctor[0], date_str, time_str)
        )
        
        if cursor.rowcount == 0:
            return False, "Appointment not found"
        
        connection.commit()
        return True, f"Appointment {new_status.lower()} successfully"
        
    except mysql.connector.Error as err:
        connection.rollback()
        return False, f"Database error: {err}"
    finally:
        cursor.close()
        connection.close()

def add_prescription(patient_id, doctor_id, treatment, admin_id):
    conn = get_db_connection()
    if not conn:
        return False, "DB connection error"

    try:
        cur = conn.cursor()

        # First verify that the patient and doctor exist
        cur.execute("SELECT P_ID FROM patient WHERE P_ID = %s", (patient_id,))
        pat = cur.fetchone()
        if not pat:
            return False, "Patient not found"

        cur.execute("SELECT E_ID FROM doctor WHERE E_ID = %s", (doctor_id,))
        doc = cur.fetchone()
        if not doc:
            return False, "Doctor not found"

        # Auto-generate new Rec_ID
        cur.execute("SELECT COALESCE(MAX(Rec_ID), 0) + 1 FROM record")
        new_rec_id = cur.fetchone()[0]

        # Insert into record
        cur.execute(
            "INSERT INTO record (Rec_ID, P_ID, Treatment, E_ID) VALUES (%s, %s, %s, %s)",
            (new_rec_id, patient_id, treatment, doctor_id)
        )

        # Insert into maintains table with admin ID
        cur.execute(
            "INSERT INTO maintains (E_ID, Rec_ID) VALUES (%s, %s)",
            (admin_id, new_rec_id)
        )
        
        conn.commit()
        return True, "Prescription added successfully"

    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"

    finally:
        cur.close()
        conn.close()

# def generate_bill(patient_id, amount, admin_id):
#     conn = get_db_connection()
#     if not conn:
#         return False, "DB connection error"

#     try:
#         cur = conn.cursor()

#         # Verify patient exists
#         cur.execute("SELECT P_ID FROM patient WHERE P_ID = %s", (patient_id,))
#         row = cur.fetchone()
#         if not row:
#             return False, "Patient not found"

#         # Generate new bill ID
#         cur.execute("SELECT COALESCE(MAX(B_ID), 0) + 1 FROM bills")
#         new_bid = cur.fetchone()[0]

#         # Insert into bills
#         cur.execute("INSERT INTO bills (B_ID, Amount) VALUES (%s, %s)", (new_bid, amount))

#         # Insert into bills_pays
#         cur.execute("INSERT INTO bills_pays (B_ID, Amount, P_ID) VALUES (%s, %s, %s)", 
#                    (new_bid, amount, patient_id))

#         # Insert into generates with admin ID
#         cur.execute("INSERT INTO generates (E_ID, B_ID) VALUES (%s, %s)", 
#                    (admin_id, new_bid))

#         conn.commit()
#         return True, "Bill generated successfully"

#     except Exception as e:
#         conn.rollback()
#         return False, f"Error: {e}"

#     finally:
#         cur.close()
#         conn.close()

def generate_bill(patient_id, amount, admin_id):
    conn = get_db_connection()
    if not conn:
        return False, "DB connection error"

    try:
        cur = conn.cursor()

        # Verify patient exists
        cur.execute("SELECT P_ID FROM patient WHERE P_ID = %s", (patient_id,))
        row = cur.fetchone()
        if not row:
            return False, "Patient not found"

        # Generate new bill ID
        cur.execute("SELECT COALESCE(MAX(B_ID), 0) + 1 FROM bills")
        new_bid = cur.fetchone()[0]

        # Insert into bills
        cur.execute("INSERT INTO bills (B_ID, Amount) VALUES (%s, %s)", (new_bid, amount))

        # Insert into bills_pays
        cur.execute("INSERT INTO bills_pays (B_ID, Amount, P_ID) VALUES (%s, %s, %s)", 
                   (new_bid, amount, patient_id))

        # Insert into generates with admin ID and current date
        cur.execute("INSERT INTO generates (E_ID, B_ID, date_generated) VALUES (%s, %s, NOW())", 
                   (admin_id, new_bid))

        conn.commit()
        return True, "Bill generated successfully"

    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"

    finally:
        cur.close()
        conn.close()

def add_test_result(patient_id, test_type, result):
    conn = get_db_connection()
    if not conn:
        return False, "DB connection error"

    try:
        cur = conn.cursor()

        # Verify patient exists
        cur.execute("SELECT P_ID FROM patient WHERE P_ID = %s", (patient_id,))
        if not cur.fetchone():
            return False, "Patient not found"

        # Insert test result
        cur.execute(
            "INSERT INTO test_takes (Test_type, Result, P_ID) VALUES (%s, %s, %s)",
            (test_type, result, patient_id)
        )

        conn.commit()
        return True, "Test result added"

    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"

    finally:
        cur.close()
        conn.close()


# def view_bills(patient_name):
#     conn = get_db_connection()
#     if not conn:
#         return []

#     try:
#         cur = conn.cursor(dictionary=True)
#         cur.execute("SELECT P_ID FROM patient WHERE PName = %s", (patient_name,))
#         row = cur.fetchone()
#         if not row:
#             return []
#         pid = row['P_ID']

#         cur.execute("""
#             SELECT b.B_ID, b.Amount, bp.Amount AS Paid_Amount
#             FROM bills b
#             JOIN bills_pays bp ON b.B_ID = bp.B_ID
#             WHERE bp.P_ID = %s
#         """, (pid,))
#         return cur.fetchall()

#     except:
#         return []

#     finally:
#         cur.close()
#         conn.close()

def view_bills(patient_name):
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT P_ID FROM patient WHERE PName = %s", (patient_name,))
        row = cur.fetchone()
        if not row:
            return []
        pid = row['P_ID']

        # Enhanced query to get more complete bill information
        cur.execute("""
            SELECT b.B_ID, b.Amount, bp.Amount AS Paid_Amount, 
                   a.AName AS Generated_By, DATE(g.date_generated) AS Bill_Date
            FROM bills b
            JOIN bills_pays bp ON b.B_ID = bp.B_ID
            JOIN generates g ON b.B_ID = g.B_ID
            JOIN admin a ON g.E_ID = a.E_ID
            WHERE bp.P_ID = %s
            ORDER BY g.date_generated DESC
        """, (pid,))
        
        bills = cur.fetchall()
        
        # For each bill, get the associated medical records
        for bill in bills:
            cur.execute("""
                SELECT r.Treatment
                FROM record r
                JOIN maintains m ON r.Rec_ID = m.Rec_ID
                JOIN generates g ON m.E_ID = g.E_ID
                WHERE g.B_ID = %s
            """, (bill['B_ID'],))
            treatments = cur.fetchall()
            
            if treatments:
                bill['Treatments'] = [t['Treatment'] for t in treatments]
            else:
                bill['Treatments'] = ["General consultation"]
        
        return bills

    except Exception as e:
        print(f"Error in view_bills: {e}")
        return []

    finally:
        cur.close()
        conn.close()

def view_medical_records(patient_name):
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT P_ID FROM patient WHERE PName = %s", (patient_name,))
        row = cur.fetchone()
        if not row:
            return []
        pid = row['P_ID']

        cur.execute("""
            SELECT r.Rec_ID, d.DName AS Doctor, r.Treatment
            FROM record r
            JOIN doctor d ON r.E_ID = d.E_ID
            WHERE r.P_ID = %s
        """, (pid,))
        return cur.fetchall()

    except:
        return []

    finally:
        cur.close()
        conn.close()


def get_patient_history(patient_id):
    conn = get_db_connection()
    if not conn:
        return [], []

    try:
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT r.Rec_ID, d.DName AS Doctor, r.Treatment
            FROM record r
            JOIN doctor d ON r.E_ID = d.E_ID
            WHERE r.P_ID = %s
        """, (patient_id,))
        records = cur.fetchall()

        cur.execute("SELECT Test_type, Result FROM test_takes WHERE P_ID = %s", (patient_id,))
        tests = cur.fetchall()

        return records, tests

    except:
        return [], []

    finally:
        cur.close()
        conn.close()



# --- Room Allocation ---
def allocate_room(patient_id, room_id):
    conn = get_db_connection()
    if not conn:
        return False, "DB connection error"

    try:
        cur = conn.cursor()

        # Check if patient is already assigned to a room
        cur.execute("SELECT * FROM patient_assigned WHERE P_ID = %s", (patient_id,))
        if cur.fetchone():
            return False, "Patient is already allocated to a room"

        # Check room exists and availability
        cur.execute("SELECT Capacity FROM rooms WHERE R_ID = %s", (room_id,))
        room = cur.fetchone()
        if not room:
            return False, "Room not found"
        capacity = room[0]

        # Count current patients in room
        cur.execute("SELECT COUNT(*) FROM patient_assigned WHERE R_ID = %s", (room_id,))
        current_count = cur.fetchone()[0]

        if current_count >= capacity:
            return False, "Room is at full capacity"

        # Get patient details
        cur.execute("SELECT DOB, PName, Gender, Height, Weight FROM patient WHERE P_ID = %s", (patient_id,))
        patient = cur.fetchone()
        if not patient:
            return False, "Patient not found"

        # Insert into patient_assigned
        cur.execute("INSERT INTO patient_assigned (P_ID, DOB, PName, Gender, Height, Weight, R_ID) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (patient_id, patient[0], patient[1], patient[2], patient[3], patient[4], room_id))

        # Update room availability if full after insertion
        if current_count + 1 == capacity:
            cur.execute("UPDATE rooms SET Availability = 0 WHERE R_ID = %s", (room_id,))

        conn.commit()
        return True, "Room allocated successfully"

    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"

    finally:
        cur.close()
        conn.close()

# --- Room Deallocation ---
def deallocate_room(patient_id, room_id):
    conn = get_db_connection()
    if not conn:
        return False, "DB connection error"

    try:
        cur = conn.cursor()

        # Check if patient is actually assigned to the given room
        cur.execute("SELECT * FROM patient_assigned WHERE P_ID = %s AND R_ID = %s", (patient_id, room_id))
        if not cur.fetchone():
            return False, "Patient is not assigned to this room"

        # Delete patient from patient_assigned
        cur.execute("DELETE FROM patient_assigned WHERE P_ID = %s AND R_ID = %s", (patient_id, room_id))

        # Recalculate current count
        cur.execute("SELECT Capacity FROM rooms WHERE R_ID = %s", (room_id,))
        capacity = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM patient_assigned WHERE R_ID = %s", (room_id,))
        new_count = cur.fetchone()[0]

        # If room was previously full and now has space, mark as available
        if new_count < capacity:
            cur.execute("UPDATE rooms SET Availability = 1 WHERE R_ID = %s", (room_id,))

        conn.commit()
        return True, "Room deallocated successfully"

    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"

    finally:
        cur.close()
        conn.close()

# --- Helper for Admin UI ---
def get_available_rooms():
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT r.R_ID, r.RType, r.Capacity, r.Availability,
                   (SELECT COUNT(*) FROM patient_assigned pa WHERE pa.R_ID = r.R_ID) AS Current_Patients
            FROM rooms r
        """)
        return cur.fetchall()
    except:
        return []
    finally:
        cur.close()
        conn.close()