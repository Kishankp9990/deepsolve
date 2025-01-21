from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_schema_pdf(file_name):
    # Create a PDF document
    pdf = SimpleDocTemplate(file_name, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    table_header_style = styles['Heading3']
    normal_style = styles['Normal']

    # Title
    elements.append(Paragraph("Database Schema and Summary of Foreign Keys", title_style))
    elements.append(Spacer(1, 12))

    # Table Data
    schema = {
        "customuser": [
            ["Column", "Data Type", "Constraint"],
            ["id", "BIGINT (auto)", "Primary Key (auto-generated)"],
            ["username", "VARCHAR(150)", "Unique, Not Null"],
            ["first_name", "VARCHAR(30)", "Nullable"],
            ["last_name", "VARCHAR(150)", "Nullable"],
            ["email", "VARCHAR(254)", "Nullable"],
            ["password", "VARCHAR(128)", "Not Null"],
            ["is_staff", "BOOLEAN", "Default: False"],
            ["is_active", "BOOLEAN", "Default: True"],
            ["created_at", "DATETIME", "Default: now()"],
        ],
        "userloginhistory": [
            ["Column", "Data Type", "Constraint"],
            ["id", "BIGINT (auto)", "Primary Key (auto-generated)"],
            ["user_id", "VARCHAR(150)", "Foreign Key (customuser.username)"],
            ["timestamp", "DATETIME", "Auto Generated, Not Null"],
        ],
        "userpost": [
            ["Column", "Data Type", "Constraint"],
            ["id", "BIGINT (auto)", "Primary Key (auto-generated)"],
            ["caption", "TEXT", "Not Null"],
            ["post_url", "VARCHAR(200)", "Not Null"],
            ["background_music_url", "VARCHAR(200)", "Nullable"],
            ["category", "VARCHAR(50)", "Choices: 'Tech', 'Entertainment', 'Business', 'Other'"],
            ["datetime_posted", "DATETIME", "Auto Generated, Not Null"],
            ["publisher_id", "VARCHAR(150)", "Foreign Key (customuser.username)"],
            ["is_public", "BOOLEAN", "Default: True"],
        ],
        "userprofile": [
            ["Column", "Data Type", "Constraint"],
            ["id", "BIGINT (auto)", "Primary Key (auto-generated)"],
            ["user_id", "VARCHAR(150)", "Foreign Key (customuser.username)"],
            ["name", "VARCHAR(100)", "Not Null"],
            ["profile_pic", "VARCHAR(300)", "Nullable"],
            ["bio", "VARCHAR(200)", "Nullable"],
            ["dob", "DATE", "Nullable"],
        ],
        "follow": [
            ["Column", "Data Type", "Constraint"],
            ["id", "BIGINT (auto)", "Primary Key (auto-generated)"],
            ["follower_id", "VARCHAR(150)", "Foreign Key (customuser.username)"],
            ["following_id", "VARCHAR(150)", "Foreign Key (customuser.username)"],
            ["created_at", "DATETIME", "Auto Generated, Not Null"],
            ["UNIQUE Constraint", "('follower_id', 'following_id')", "Prevents duplicate follow entries"],
        ],
        "likepost": [
            ["Column", "Data Type", "Constraint"],
            ["id", "BIGINT (auto)", "Primary Key (auto-generated)"],
            ["user_id", "VARCHAR(150)", "Foreign Key (customuser.username)"],
            ["post_id", "BIGINT", "Foreign Key (userpost.id)"],
            ["created_at", "DATETIME", "Auto Generated, Not Null"],
            ["UNIQUE Constraint", "('user_id', 'post_id')", "Prevents duplicate likes by the same user"],
        ],
        "commentpost": [
            ["Column", "Data Type", "Constraint"],
            ["id", "BIGINT (auto)", "Primary Key (auto-generated)"],
            ["user_id", "VARCHAR(150)", "Foreign Key (customuser.username)"],
            ["post_id", "BIGINT", "Foreign Key (userpost.id)"],
            ["text", "TEXT", "Not Null"],
            ["created_at", "DATETIME", "Auto Generated, Not Null"],
        ],
    }

    # Add schema tables
    for table_name, table_data in schema.items():
        elements.append(Paragraph(f"Table: {table_name}", table_header_style))
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

    # Add summary of foreign keys
    elements.append(Paragraph("Summary of Foreign Keys", table_header_style))
    foreign_keys = [
        "userloginhistory.user_id → customuser.username",
        "userpost.publisher_id → customuser.username",
        "userprofile.user_id → customuser.username",
        "follow.follower_id → customuser.username",
        "follow.following_id → customuser.username",
        "likepost.user_id → customuser.username",
        "likepost.post_id → userpost.id",
        "commentpost.user_id → customuser.username",
        "commentpost.post_id → userpost.id",
    ]
    for fk in foreign_keys:
        elements.append(Paragraph(f"- {fk}", normal_style))

    # Build the PDF
    pdf.build(elements)

# Generate the PDF
generate_schema_pdf("database_schema.pdf")
