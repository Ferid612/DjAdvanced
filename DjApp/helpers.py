from datetime import datetime
import os
import uuid
from django.utils.html import escape
from django.http import JsonResponse
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import json
import traceback
from DjAdvanced.settings.production import AllOWED_FRONT_HOST, engine
from fpdf import FPDF
import logging

custom_logger = logging.getLogger("django.custom")
django_logger = logging.getLogger("django")


def create_pdf(file_name, person_name, person_surname, report_type, order_details):
    """
    Generates a PDF file with order details.

    Args:
        file_name (str): The desired file name for the PDF.
        person_name (str): The person's first name.
        person_surname (str): The person's surname.
        report_type (str): The type of the report.
        order_details (dict): The order details.

    Returns:
        HttpResponse: The HTTP response object with the generated PDF file as an attachment.
    """
    # Define the header text
    header_text = f"{person_name} {person_surname}'s {report_type} report"

    # Define the file path for the Delta logo
    delta_logo_path = 'deltaLogo.png'

    # Define the Delta Commercial Community footer details
    delta_footer_text = "Delta Commercial Community"
    delta_phone_number = "+994-070-333-5610"
    delta_email = "info@deltacommercial.com"

    # Define a helper function to flatten the order details dictionary
    def flatten_dict(d, parent_key='', sep=' '):
        """
        Recursively flattens a nested dictionary into a flat dictionary.

        Args:
            d (dict): The dictionary to be flattened.
            parent_key (str): The parent key for the current level of recursion.
            sep (str): The separator used to join parent and child keys.

        Returns:
            dict: The flattened dictionary.
        """
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    # Flatten the order details dictionary and create a list of tuples for the table data
    flattened_order_details = flatten_dict(order_details)
    TABLE_DATA = [("Field", "Value")]
    TABLE_DATA.extend(list(flattened_order_details.items()))

    # Create a new PDF object and set the font and page size
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size=12)

    # Add the Delta logo to the PDF
    pdf.image(delta_logo_path, x=10, y=10, w=30)

    # Add the header text and current date to the PDF
    now_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.ln(5)
    pdf.cell(40)  # Add empty cell to position the header text and date on the right side
    pdf.cell(0, 10, header_text, ln=1)  # Header text on the right
    pdf.cell(40)  # Add empty cell for spacing
    pdf.cell(0, 10, f"Date: {now_date}", ln=1)  # Date on the right

    # Add a line break before the table
    pdf.ln(10)

    # Calculate the column width based on the length of the longest value in the table data
    col_width = max(pdf.get_string_width(str(row[1])) for row in TABLE_DATA) + 36

    # Add the table data to the PDF
    for row in TABLE_DATA:
        pdf.cell(col_width, 10, str(row[0]), border=1)
        pdf.cell(col_width, 10, str(row[1]), border=1)
        pdf.ln()

    # Add a line break before the footer
    pdf.ln(10)

    # Add the Delta Commercial Community footer to the PDF
    pdf.cell(0, 10, delta_footer_text, ln=1, align='C')
    pdf.cell(0, 10, f"Phone: {delta_phone_number} | Email: {delta_email}", ln=1, align='C')

    return pdf



def GetErrorDetails(from_dev="Something went wrong.", e=Exception, status=400):
    error_data = {
        "From_dev": from_dev,
        "An exception occurred": str(e),
        "Type of exception": str(type(e)),
        "Exception message": str(e.args),
        "Traceback ": str(traceback.format_exc()),
    }
    traceback.print_tb(e.__traceback__)
    return JsonResponse(error_data, status=status)


def add_get_params(response, request):

    origin = request.headers.get("Origin")
    django_logger.info(f"Request host origin {origin}\n")

    if origin == AllOWED_FRONT_HOST:
        response["Access-Control-Allow-Origin"] = origin
    else: 
        response["Access-Control-Allow-Origin"] = "http://localhost:3000"

    response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT"
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, X-Requested-With, user"
    response["Access-Control-Max-Age"] = 86400  # 24 hours
    response['Access-Control-Allow-Credentials'] = 'true'
    
    
    
@contextmanager
def session_scope():

    session = sessionmaker(bind=engine)()
    """Provide a transactional scope around a series of operations."""
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def save_uploaded_image(image_file, path):
    """
    Saves an uploaded image file to the server and returns the file path.

    Args:
        image_file: The uploaded image file.

    Returns:
        The file path of the saved image.
    """
    # Generate a unique filename for the image
    filename = f"{uuid.uuid4()}.{image_file.name.split('.')[-1]}"
    # Define the path where the image will be saved
    save_path = os.path.join(path, filename)
    # Open a new file and write the uploaded image data to it
    with open(save_path, 'wb+') as destination:
        for chunk in image_file.chunks():
            destination.write(chunk)
    # Return the file path of the saved image
    return save_path


def serializer(rows) -> list:
    "Return all rows from a cursor as a dict"
    return [dict(row) for row in rows]


def escape_dict(data):
    if isinstance(data, list):
        for x, l in enumerate(data):
            if isinstance(l, (dict, list)):
                escape_dict(l)
            elif l is not None:
                data[x] = escape(l)

    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                escape_dict(v)
            elif v is not None:
                data[k] = escape(v)
        return data


def escape_list(data):
    return list(map(lambda item: escape(item), data))


def input_json_sanitizer(request, parameter):
    if request.method == "GET":
        data = json.loads(request.GET.get(parameter))
    elif request.method == "POST":
        data = json.loads(request.POST.get(parameter))

    if isinstance(data, list):
        return escape_list(data)
    if isinstance(data, dict):
        return escape_dict(data)


def input_get_list_sanitizer(request, parameter):
    if request.method == "GET":
        data_list = request.GET.getlist(parameter)
    elif request.method == "POST":
        data_list = request.POST.getlist(parameter)

    return escape_list(data_list)

