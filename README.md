# Data Processing Application

A Django-based web application for processing and managing financial data with multiple modules (app, app2, and app3).

## Features

### App Module (Text Processors)
- Process and store financial data
- Calculate loan amounts and interest rates
- Handle PMI calculations
- Export data to Excel
- User tracking and management
- Comprehensive data validation

### App2 Module (Text Processors 2)
- Identical functionality to App module
- Separate database storage
- Independent Excel export
- Separate user tracking

### App3 Module (Text Processors 3)
- Additional processing capabilities
- Independent data management
- Custom export options

## Technical Requirements

- Python 3.8+
- Django 4.2+
- MySQL Database
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/udayjaggumanthri/excel_data.git
cd excel_data
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
Create a `.env` file in the project root with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=mysql://user:password@localhost:3306/dbname
```

5. Apply database migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Usage

### App Module
- Access the main form at: `/`
- View results at: `/results/`
- Admin interface at: `/admin/app/processeddata/`

### App2 Module
- Access the second form at: `/home2/`
- View results at: `/results2/`
- Admin interface at: `/admin/app2/processeddata2/`

### App3 Module
- Access the third form at: `/home3/`
- View results at: `/results3/`
- Admin interface at: `/admin/app3/processeddata3/`

### Data Processing Features
- Image number and serial number tracking
- Username tracking for data entry
- Customer information processing
- Financial calculations including:
  - Purchase value processing
  - Down payment calculations
  - Loan period management
  - Interest rate calculations
  - PMI determinations
  - Property insurance tracking

### Excel Export
All modules support Excel export with the following columns:
1. Image Number
2. Serial Number
3. Username
4. Customer Reference Number
5. Customer Name
6. City, State
7. Purchase Value and Down Payment
8. Loan Period and Annual Interest
9. Guarantor Name
10. Guarantor Reference Number
11. Loan Amount and Principal
12. Total Interest for Loan Period
13. Property Insurance per Month and PMI per Annum

## Development

### Project Structure
```
excel_data/
├── app/                # Main application module
├── app2/              # Secondary application module
├── app3/              # Tertiary application module
├── data_extract/      # Data extraction utilities
├── project/           # Project configuration
├── staticfiles/       # Static files
├── manage.py
├── requirements.txt
└── README.md
```

### Key Files
- `app/models.py`, `app2/models.py`, `app3/models.py`: Data models
- `app/views.py`, `app2/views.py`, `app3/views.py`: Business logic
- `app/admin.py`, `app2/admin.py`, `app3/admin.py`: Admin interface configuration
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, and other static files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Acknowledgments

- Django Framework
- Bootstrap for UI components
- All contributors and users of this project