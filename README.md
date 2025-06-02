# Text Processors

This is a Django web application that provides various text processing functionalities, including:
- Customer Name processing
- City, State formatting
- Purchase Value calculation (with alphanumeric to numeric conversion, reduction percentage, down payment, and loan amount)
- Guarantor Name processing

## Setup Instructions

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

    The application will be accessible at `http://127.0.0.1:8000/`.

## Usage

Open your web browser and navigate to the application URL. You will see input fields for:

*   **CUSTOMER NAME**: Enter customer names.
*   **CITY, STATE**: Enter location details.
*   **PURCHASE VALUE**: Enter alphanumeric purchase values (e.g., "Four Hundred dollars and Twenty cents") and a down payment percentage. The application will calculate and display the original purchase value, down payment value, and loan amount.
*   **GUARANTOR NAME**: Enter guarantor names.

After entering the required information, click "Process All Texts" to see the processed outputs. You can use the "Copy" buttons to easily copy the results to your clipboard.