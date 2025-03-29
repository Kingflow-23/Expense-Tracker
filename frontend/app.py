import requests
import streamlit as st

# FastAPI Backend URL
BASE_URL = "http://127.0.0.1:8000"

# ------------------------------
# Sidebar Navigation
# ------------------------------
st.sidebar.title("📍 Navigation")
page = st.sidebar.radio(
    "📌 Go to", ["🏠 Home", "🎨 Customize Your Profile", "📖 Documentation"]
)

# ------------------------------
# Documentation Page
# ------------------------------
if page == "📖 Documentation":
    st.title("📖 Expense Tracker Documentation")
    st.markdown(
        """
    ## Overview
    ## Welcome to Expense Tracker!

    Expense Tracker is your personal tool for managing daily expenses, tracking your spending habits, and keeping your budget on track. Whether you’re just starting out or have been budgeting for years, our app makes it easy to manage your finances.

    ### Key Features:
    - **User Management:**
    - **Sign Up & Log In:** Create a secure account with your username, email, and password.
    - **Update Profile:** Easily update your personal details like phone number, address, favorite sport, favorite animal, occupation, and bio.
    - **Delete Account:** Remove your account at any time if you wish to start fresh.

    - **Expense Management:**
    - **View Expenses:** Toggle to view your expenses. Use the filter to search by category (case-insensitive) for a refined view.
    - **Add Expense:** Quickly add new expenses using a simple, intuitive form.
    - **Edit & Delete Expenses:** Modify or remove any expense with just one click.

    ### How to Get Started:
    1. **Log In or Sign Up:**  
    Use the sidebar to log in if you already have an account or sign up if you’re new.
    2. **Manage Your Expenses:**  
    Once logged in, head to the Home page to view, add, edit, or delete expenses.
    3. **Update Your Profile:**  
    Navigate to the Update Profile page to add or change your personal details. Your updated info (like your profile picture and favorite things) will be shown in the sidebar.
    4. **Navigation:**  
    Use the sidebar radio menu to easily switch between the Home, Update Profile, and Documentation pages.

    ### Tips:
    - **Log Out:** Always remember to log out when you’re finished.
    - **Need Help?** If you experience any issues, try refreshing the page or checking your internet connection.

    Enjoy using Expense Tracker and happy budgeting! 🚀
    """
    )
    st.stop()


# ---------------------------------------
# Authentication & User Profile Functions
# ---------------------------------------
def login(username, password):
    """Authenticate user and get token"""
    response = requests.post(
        f"{BASE_URL}/auth/login", data={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        st.error("❌ Invalid username or password.")
        return None


def signup(username, email, password):
    """Register a new user"""
    response = requests.post(
        f"{BASE_URL}/auth/signup",
        json={"username": username, "email": email, "password": password},
    )
    if response.status_code == 200:
        st.success("✅ User created successfully. You can now log in.")
    else:
        st.error("❌ Failed to create user.")


def delete_user(username, password):
    """Delete user account using provided username and password"""
    response = requests.delete(
        f"{BASE_URL}/auth/delete", json={"username": username, "password": password}
    )
    if response.status_code == 200:
        st.success("✅ User account deleted successfully.")
        st.session_state.user_token = None  # Logout after deletion
    else:
        st.error("❌ Failed to delete user.")


def update_profile(data, token):
    """Update user profile information"""
    headers = {"Authorization": f"Bearer {token}"}
    clean_data = {key: value for key, value in data.items() if value}
    clean_data["username"] = st.session_state.username
    response = requests.put(f"{BASE_URL}/auth/update", json=clean_data, headers=headers)
    if response.status_code == 200:
        st.success("✅ Profile updated successfully.")
        for key, value in clean_data.items():
            st.session_state[key] = (
                value  # Update session state only if the request succeeds
            )
    else:
        st.error("❌ Failed to update profile. You may need to log in again.")


# ------------------------------
# Expense Functions
# ------------------------------
def get_expenses(token):
    """Fetch all expenses"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/expenses", headers=headers)
    return response.json() if response.status_code == 200 else []


def create_expense(amount, category, description, token):
    """Create a new expense"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"amount": amount, "category": category, "description": description}
    response = requests.post(f"{BASE_URL}/expenses", json=data, headers=headers)
    return response.json()


def update_expense(expense_id, amount, category, description, token):
    """Update an expense"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"amount": amount, "category": category, "description": description}

    response = requests.patch(
        f"{BASE_URL}/expenses/{expense_id}", json=data, headers=headers
    )  # 🔄 Use PATCH instead of PUT

    if response.status_code == 200:
        st.success("✅ Expense updated successfully.")
    else:
        st.error(
            f"❌ Failed to update expense: {response.json().get('detail', 'Unknown error')}"
        )


def delete_expense(expense_id, token):
    """Delete an expense"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/expenses/{expense_id}", headers=headers)
    if response.status_code == 200:
        st.success("✅ Expense deleted successfully.")
    else:
        st.error("❌ Failed to delete expense.")


# --------------------------------------------------
# Sidebar: Authentication Handling & Profile Display
# --------------------------------------------------
if "user_token" not in st.session_state:
    st.session_state.user_token = None

# Display profile info in sidebar if logged in
if st.session_state.user_token:
    st.sidebar.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)

    # Display Profile Picture (Fallback to Placeholder if None)
    profile_picture = st.session_state.get("profile_picture_url", "").strip()
    if profile_picture:
        st.sidebar.image(profile_picture, width=300)
    else:
        pass

    # Display Username
    st.sidebar.markdown(f"<h4>{st.session_state.username}</h4>", unsafe_allow_html=True)

    # Display User Info (Only Show If Provided)
    user_fields = {
        "📝 Bio": st.session_state.get("bio"),
        "📞 Phone Number": st.session_state.get("phone_number"),
        "💼 Occupation": st.session_state.get("occupation"),
        "📍 Address": st.session_state.get("address"),
        "💑 Relationship Status": st.session_state.get("relationship_status"),
        "⚽ Favorite Sport": st.session_state.get("favorite_sport"),
        "🐾 Favorite Animal": st.session_state.get("favorite_animal"),
    }

    for label, value in user_fields.items():
        if value:  # Only display if value is not empty or None
            st.sidebar.write(f"**{label}:** {value}")

    st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Authentication forms if not logged in
if not st.session_state.user_token:
    st.markdown("<h2 style='text-align: center;'>Welcome!</h2>", unsafe_allow_html=True)
    st.info("Please log in or sign up to get started.")

    st.sidebar.header("🔑 Login")
    login_username = st.sidebar.text_input("Username", key="login_username")
    login_password = st.sidebar.text_input(
        "Password", type="password", key="login_password"
    )
    if st.sidebar.button("Login"):
        token = login(login_username, login_password)
        if token:
            st.session_state.user_token = token
            st.session_state.username = login_username

    st.sidebar.header("🆕 Sign Up")
    signup_username = st.sidebar.text_input("New Username", key="signup_username")
    signup_email = st.sidebar.text_input("New Email", key="signup_email")
    signup_password = st.sidebar.text_input(
        "New Password", type="password", key="signup_password"
    )
    if st.sidebar.button("Sign Up"):
        signup(signup_username, signup_email, signup_password)
else:
    if st.sidebar.button("Logout"):
        st.session_state.user_token = None

    # Set default flag for delete confirmation if not set
    if "delete_confirm" not in st.session_state:
        st.session_state.delete_confirm = False

    # When the "Delete Account" button is clicked, set the flag
    if st.sidebar.button("❌ Delete Account"):
        st.session_state.delete_confirm = True

    # If the flag is set, display the confirmation inputs
    if st.session_state.delete_confirm:
        confirm = st.sidebar.radio(
            "Are you sure you want to delete your account?",
            ["No", "Yes"],
            index=1,
            key="delete_radio",
        )

        if confirm == "Yes":
            del_username = st.sidebar.text_input("Confirm Username")
            del_password = st.sidebar.text_input("Confirm Password", type="password")

            if st.sidebar.button("Confirm Delete"):
                delete_user(del_username, del_password)
                st.session_state.delete_confirm = False  # Reset flag after deletion

        elif confirm == "No":
            if st.sidebar.button("Cancel"):
                st.session_state.delete_confirm = (
                    False  # Reset flag when user explicitly cancels
                )


# -------------------------------------
# Main Page Content Based on Navigation
# -------------------------------------
if page == "🏠 Home":
    # Centered Title for Home Page
    st.markdown(
        "<h2 style='text-align: center;'>💰📊 Expense Tracker – Take Control of Your Finances!</h2>",
        unsafe_allow_html=True,
    )

    # 1 - Manage Expenses Section
    # Initialize session states
    if "expenses" not in st.session_state:
        st.session_state.expenses = None  # Stores fetched expenses

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = {}

    if "delete_expense_confirm" not in st.session_state:
        st.session_state.delete_expense_confirm = {}

    def trigger_edit_mode(expense_id):
        """Toggle edit mode for an expense."""
        st.session_state.edit_mode[expense_id] = True

    def exit_edit_mode(expense_id):
        """Exit edit mode."""
        st.session_state.edit_mode[expense_id] = False

    def confirm_delete(expense_id):
        """Set delete confirmation state."""
        st.session_state.delete_expense_confirm[expense_id] = True

    def cancel_delete(expense_id):
        """Reset delete confirmation state."""
        st.session_state.delete_expense_confirm[expense_id] = False

    def load_expenses(category_filter=""):
        """Fetch expenses from the API and store them in session state."""
        headers = {"Authorization": f"Bearer {st.session_state.user_token}"}
        params = {"category": category_filter.lower()} if category_filter else {}

        response = requests.get(f"{BASE_URL}/expenses", params=params, headers=headers)
        if response.status_code == 200:
            st.session_state.expenses = response.json()
        else:
            st.error("⚠️ Failed to load expenses. You may need to log in again.")
            st.session_state.expenses = None  # Reset on failure

    # 1️⃣ Manage Expenses Section
    st.markdown(
        "<h3 style='text-align: center;'>1️⃣ Manage Expenses</h3>", unsafe_allow_html=True
    )
    show_expenses = st.checkbox(
        "Show Expenses", value=st.session_state.expenses is not None
    )

    if show_expenses:
        category_filter = st.text_input(
            "Enter category to filter expenses (leave empty to show all)"
        )

        if st.session_state.expenses is None or st.button("🔄 Refresh Expenses"):
            load_expenses(
                category_filter
            )  # Auto-load expenses when checkbox is checked

        if st.session_state.expenses:
            for expense in st.session_state.expenses:
                expense_id = expense["id"]

                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.write(f"**{expense['category']}** - 💲{expense['amount']}")
                with col2:
                    st.write(expense["description"])

                # Edit Expense
                with col3:
                    st.button(
                        f"📝 Edit",
                        key=f"edit_btn_{expense_id}",
                        on_click=trigger_edit_mode,
                        args=(expense_id,),
                    )

                    if st.session_state.edit_mode.get(expense_id, False):
                        new_amount = st.number_input(
                            "New Amount",
                            value=expense["amount"],
                            key=f"amt_{expense_id}",
                        )
                        new_category = st.text_input(
                            "New Category",
                            value=expense["category"],
                            key=f"cat_{expense_id}",
                        )
                        new_description = st.text_area(
                            "New Description",
                            value=expense["description"],
                            key=f"desc_{expense_id}",
                        )

                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            st.button(
                                "💾 Save",
                                key=f"save_{expense_id}",
                                on_click=update_expense,
                                args=(
                                    expense_id,
                                    new_amount,
                                    new_category,
                                    new_description,
                                    st.session_state.user_token,
                                ),
                            )
                        with col_cancel:
                            st.button(
                                "❌ Cancel",
                                key=f"cancel_{expense_id}",
                                on_click=exit_edit_mode,
                                args=(expense_id,),
                            )

                # Delete Expense with Confirmation
                with col4:
                    st.button(
                        f"🗑️ Delete",
                        key=f"del_{expense_id}",
                        on_click=confirm_delete,
                        args=(expense_id,),
                    )

                    if st.session_state.delete_expense_confirm.get(expense_id, False):
                        st.warning(
                            f"Are you sure you want to delete {expense['category']}?"
                        )
                        col_confirm, col_cancel = st.columns(2)
                        with col_confirm:
                            st.button(
                                "✅ Yes, Delete",
                                key=f"confirm_del_{expense_id}",
                                on_click=delete_expense,
                                args=(expense_id, st.session_state.user_token),
                            )
                            st.session_state.delete_expense_confirm[expense_id] = (
                                False  # Reset after deletion
                            )
                        with col_cancel:
                            st.button(
                                "❌ Cancel",
                                key=f"cancel_del_{expense_id}",
                                on_click=cancel_delete,
                                args=(expense_id,),
                            )

        else:
            st.write("🔍 No expenses found.")
    else:
        # Reset expenses when user unchecks the checkbox
        st.session_state.expenses = None

    st.markdown("---")
    # 2 - Add Expense Section
    st.markdown(
        "<h3 style='text-align: center;'>2️⃣ Add Expense</h3>", unsafe_allow_html=True
    )
    with st.form(key="expense_form"):
        amount = st.number_input("💲 Amount", min_value=0.0)
        category = st.text_input("📌 Category")
        description = st.text_area("📝 Description")
        submit_button = st.form_submit_button(label="➕ Add Expense")
    if submit_button:
        create_expense(amount, category, description, st.session_state.user_token)
        st.success("✅ Expense added successfully.")

elif page == "🎨 Customize Your Profile":
    # Centered Title for Update Profile Page
    st.markdown(
        "<h2 style='text-align: center;'>Update Profile</h2>", unsafe_allow_html=True
    )
    st.info(
        "Update your personal details below. Leave a field empty if you do not wish to change it."
    )
    with st.form(key="profile_form"):
        phone = st.text_input(
            "📞 Phone Number", value=st.session_state.get("phone_number", "")
        )
        relationship_status = st.text_input(
            "💑 Relationship Status",
            value=st.session_state.get("relationship_status", ""),
        )
        address = st.text_area("🏠 Address", value=st.session_state.get("address", ""))
        favorite_sport = st.text_input(
            "⚽ Favorite Sport", value=st.session_state.get("favorite_sport", "")
        )
        favorite_animal = st.text_input(
            "🐾 Favorite Animal", value=st.session_state.get("favorite_animal", "")
        )
        occupation = st.text_input(
            "💼 Occupation", value=st.session_state.get("occupation", "")
        )
        bio = st.text_area("📝 Bio", value=st.session_state.get("bio", ""))
        profile_picture_url = st.text_input(
            "📸 Profile Picture URL",
            value=st.session_state.get("profile_picture_url", ""),
        )

        profile_submit = st.form_submit_button(label="Apply changes")

    if profile_submit:
        update_data = {
            "phone_number": phone,
            "relationship_status": relationship_status,
            "address": address,
            "favorite_sport": favorite_sport,
            "favorite_animal": favorite_animal,
            "occupation": occupation,
            "bio": bio,
            "profile_picture_url": profile_picture_url,
        }
        update_profile(update_data, st.session_state.user_token)
        # Update session_state with new profile data for sidebar display
        if phone:
            st.session_state.phone_number = phone
        if relationship_status:
            st.session_state.relationship_status = relationship_status
        if address:
            st.session_state.address = address
        if favorite_sport:
            st.session_state.favorite_sport = favorite_sport
        if favorite_animal:
            st.session_state.favorite_animal = favorite_animal
        if occupation:
            st.session_state.occupation = occupation
        if bio:
            st.session_state.bio = bio
        if profile_picture_url:
            st.session_state.profile_picture_url = profile_picture_url
