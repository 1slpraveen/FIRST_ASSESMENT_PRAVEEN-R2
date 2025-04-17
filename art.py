import pymysql
from weasyprint import HTML
from jinja2 import Template
import sys
from datetime import datetime

# --- Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Praveen@0201',
    'database': 's_bank',
    'cursorclass': pymysql.cursors.DictCursor
}

# --- HTML Template for the PDF ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Credit Card Statement</title>
    <style>
        @page {
            size: A4;
            margin: 0;
        }
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            color: #333;
        }
        .header {
            background-color: #00674c;
            color: white;
            padding: 20px 40px;
            height: 80px;
            position: relative;
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
        }
        .statement-title {
            text-align: right;
            position: absolute;
            right: 40px;
            top: 50%;
            transform: translateY(-50%);
        }
        .customer-info {
            background-color: #f8f9fa;
            padding: 20px 40px;
            border-bottom: 1px solid #dee2e6;
        }
        .section {
            padding: 20px 40px;
        }
        h1 {
            font-size: 24px;
            margin: 0;
            color: #00674c;
        }
        h2 {
            font-size: 18px;
            margin: 0 0 15px 0;
            color: #00674c;
        }
        h3 {
            font-size: 16px;
            margin: 20px 0 10px 0;
            color: #00674c;
        }
        p {
            margin: 5px 0;
            font-size: 14px;
        }
        .summary-box {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }
        .summary-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .summary-label {
            font-weight: bold;
            width: 50%;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 14px;
        }
        th {
            background-color: #f1f1f1;
            color: #00674c;
            padding: 12px 8px;
            text-align: left;
            border-bottom: 2px solid #dee2e6;
            font-weight: 600;
        }
        td {
            padding: 10px 8px;
            border-bottom: 1px solid #dee2e6;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .amount {
            text-align: right;
        }
        .credit {
            color: #00674c;
        }
        .debit {
            color: #dc3545;
        }
        .footer {
            background-color: #f8f9fa;
            border-top: 1px solid #dee2e6;
            padding: 15px 40px;
            font-size: 12px;
            position: absolute;
            bottom: 0;
            width: 100%;
            box-sizing: border-box;
        }
        .pagination {
            text-align: center;
            margin-top: 20px;
            font-size: 14px;
            color: #666;
        }
        .important-notice {
            background-color: #fffbea;
            border-left: 4px solid #ffc107;
            padding: 10px 15px;
            margin: 20px 0;
            font-size: 13px;
        }
        .card-details {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
        }
        .card-details-column {
            width: 48%;
        }
        .contact-info {
            margin-top: 20px;
            font-size: 13px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">STANDARD BANK</div>
        <div class="statement-title">CREDIT CARD STATEMENT</div>
    </div>
    
    <div class="customer-info">
        <h2>{{ customer['first_name'] }} {{ customer['last_name'] }}</h2>
        <p>{{ customer['address'] }}</p>
        <p>Email: {{ customer['email'] }} | Phone: {{ customer['phone_number'] }}</p>
    </div>
    
    <div class="section">
        <div class="card-details">
            <div class="card-details-column">
                <div class="summary-box">
                    <h3>Card Details</h3>
                    <div class="summary-row">
                        <span class="summary-label">Card Number:</span>
                        <span>**** **** **** {{ account['card_number'][-4:] }}</span>
                    </div>
                    <div class="summary-row">
                        <span class="summary-label">Card Type:</span>
                        <span>{{ account['card_type'] }}</span>
                    </div>
                    <div class="summary-row">
                        <span class="summary-label">Statement Date:</span>
                        <span>{{ statement_date }}</span>
                    </div>
                </div>
            </div>
            <div class="card-details-column">
                <div class="summary-box">
                    <h3>Account Summary</h3>
                    <div class="summary-row">
                        <span class="summary-label">Previous Balance:</span>
                        <span>R {{ "{:,.2f}".format(previous_balance) }}</span>
                    </div>
                    <div class="summary-row">
                        <span class="summary-label">Payments & Credits:</span>
                        <span class="credit">R {{ "{:,.2f}".format(payments_credits) }}</span>
                    </div>
                    <div class="summary-row">
                        <span class="summary-label">Purchases & Debits:</span>
                        <span class="debit">R {{ "{:,.2f}".format(purchases_debits) }}</span>
                    </div>
                    <div class="summary-row" style="border-top: 1px solid #dee2e6; padding-top: 10px; font-weight: bold;">
                        <span class="summary-label">Current Balance:</span>
                        <span>R {{ "{:,.2f}".format(account['current_balance']) }}</span>
                    </div>
                    <div class="summary-row">
                        <span class="summary-label">Credit Limit:</span>
                        <span>R {{ "{:,.2f}".format(account['credit_limit']) }}</span>
                    </div>
                    <div class="summary-row">
                        <span class="summary-label">Available Credit:</span>
                        <span>R {{ "{:,.2f}".format(account['credit_limit'] - account['current_balance']) }}</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="important-notice">
            <strong>IMPORTANT:</strong> Payment due by 25th of this month. To avoid interest charges, please pay the full current balance.
        </div>

        <h3>Transactions (Page {{ page_number }} of {{ total_pages }})</h3>
        <table>
            <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Merchant</th>
                <th>Category</th>
                <th style="text-align: right;">Amount (R)</th>
            </tr>
            {% for txn in transactions %}
            <tr>
                <td>{{ txn['transaction_date'].strftime('%d/%m/%Y') }}</td>
                <td>{{ txn['description'] }}</td>
                <td>{{ txn['merchant'] }}</td>
                <td>{{ txn['category'] }}</td>
                <td class="amount {% if txn['amount'] < 0 %}credit{% else %}debit{% endif %}">
                    {{ "{:,.2f}".format(txn['amount']|abs) }}
                </td>
            </tr>
            {% endfor %}
        </table>

        {% if page_number < total_pages %}
        <div class="pagination">
            <p>Page {{ page_number }} of {{ total_pages }}</p>
            <p>Continued on next page...</p>
        </div>
        {% endif %}
        
        <div class="contact-info">
            <p><strong>Customer Service:</strong> 0800 123 456 | <strong>Email:</strong> support@standardbank.co.za</p>
            <p><strong>International:</strong> +27 11 299 4701 | <strong>Lost/Stolen Cards:</strong> 0800 020 600</p>
        </div>
    </div>
    
    <div class="footer">
        <p>Standard Bank is a licensed financial services provider in terms of the Financial Advisory and Intermediary Services Act and a registered credit provider in terms of the National Credit Act, registration number NCRCP15.</p>
        <p>Statement generated on {{ generation_date }}</p>
    </div>
</body>
</html>
"""

# --- Add custom filter for absolute value ---
def add_abs_filter(template_string):
    """Add a custom abs filter to the template"""
    template = Template(template_string)
    template.environment.filters['abs'] = abs
    return template

# --- Helper Functions ---
def calculate_summaries(transactions):
    """Calculate payment summaries from transactions"""
    payments_credits = 0
    purchases_debits = 0
    
    for txn in transactions:
        amount = txn['amount']
        if amount < 0:  # Credit (payment)
            payments_credits += abs(amount)
        else:  # Debit (purchase)
            purchases_debits += amount
    
    # Previous balance calculation (estimate)
    previous_balance = 0  # This would ideally come from historical data
    
    return payments_credits, purchases_debits, previous_balance

# --- Main Function ---
def generate_pdf_statement(customer_id, output_file, page=1, transactions_per_page=15):
    try:
        # Connect to the database
        connection = pymysql.connect(**DB_CONFIG)
        with connection:
            with connection.cursor() as cursor:
                # Fetch customer
                cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
                customer = cursor.fetchone()
                if not customer:
                    raise ValueError("Customer not found.")

                # Fetch account
                cursor.execute("SELECT * FROM accounts WHERE customer_id = %s LIMIT 1", (customer_id,))
                account = cursor.fetchone()
                if not account:
                    raise ValueError("Account not found for customer.")

                # Fetch total number of transactions for pagination
                cursor.execute("""
                    SELECT COUNT(*) FROM transactions WHERE account_id = %s
                """, (account['account_id'],))
                total_transactions = cursor.fetchone()['COUNT(*)']
                total_pages = (total_transactions // transactions_per_page) + (1 if total_transactions % transactions_per_page else 0)

                # Fetch all transactions for summary calculations
                cursor.execute("""
                    SELECT * FROM transactions
                    WHERE account_id = %s
                    ORDER BY transaction_date DESC
                """, (account['account_id'],))
                all_transactions = cursor.fetchall()
                
                # Fetch transactions for the current page
                cursor.execute("""
                    SELECT * FROM transactions
                    WHERE account_id = %s
                    ORDER BY transaction_date DESC
                    LIMIT %s OFFSET %s
                """, (account['account_id'], transactions_per_page, (page - 1) * transactions_per_page))
                transactions = cursor.fetchall()
        
        # Calculate summary values
        payments_credits, purchases_debits, previous_balance = calculate_summaries(all_transactions)
        
        # Current date for statement
        today = datetime.now()
        statement_date = today.strftime('%d/%m/%Y')
        generation_date = today.strftime('%d/%m/%Y %H:%M')

        # Create template with custom abs filter
        template = add_abs_filter(HTML_TEMPLATE)
        
        # Render HTML with pagination info
        html_out = template.render(
            customer=customer,
            account=account,
            transactions=transactions,
            page_number=page,
            total_pages=total_pages,
            statement_date=statement_date,
            generation_date=generation_date,
            payments_credits=payments_credits,
            purchases_debits=purchases_debits,
            previous_balance=previous_balance
        )

        # Generate PDF
        HTML(string=html_out).write_pdf(output_file)
        print(f"✅ PDF statement generated: {output_file}")

    except pymysql.MySQLError as e:
        print(f"❌ Database error: {e}")
    except Exception as ex:
        print(f"❌ Error: {ex}")


# --- Run Example ---
if __name__ == "__main__":
    if len(sys.argv) < 3:
        generate_pdf_statement(customer_id=1, output_file="statement_customer1.pdf", page=1)
    else:
        cust_id = int(sys.argv[1])
        file_name = sys.argv[2]
        page_number = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        generate_pdf_statement(cust_id, file_name, page=page_number)
