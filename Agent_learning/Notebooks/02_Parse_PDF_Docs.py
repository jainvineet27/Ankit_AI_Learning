# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# DBTITLE 1,Project Overview
# MAGIC %md
# MAGIC # PDF Document Processing Pipeline
# MAGIC
# MAGIC **Objective:** Extract text from product documentation PDFs and store in a Unity Catalog table
# MAGIC
# MAGIC **Source Location:** `/Volumes/agent_catalog/agentic_schema/customer_service/product_docs/`
# MAGIC
# MAGIC **Target Table:** `agentic_catalog.agentic_schema.product_docs`
# MAGIC
# MAGIC **Schema:**
# MAGIC - `product_name` - PDF filename without extension
# MAGIC - `product_doc` - Extracted text content

# COMMAND ----------

# DBTITLE 1,Install Required Library
# Install PyPDF2 for PDF text extraction
%pip install PyPDF2

# COMMAND ----------

# DBTITLE 1,Step 1: List PDF Files
# MAGIC %md
# MAGIC ## Step 1: Discover PDF Files
# MAGIC
# MAGIC We'll use `dbutils.fs.ls()` to list all PDF files in the source directory.

# COMMAND ----------

# DBTITLE 1,List PDF Files
# Define the source directory path
source_path = "/Volumes/agentic_catalog/agentic_schema/customer_service/product_docs/"

# List all files in the directory
files = dbutils.fs.ls(source_path)

# Filter for PDF files only
pdf_files = [f for f in files if f.name.endswith('.pdf')]

print(f"Found {len(pdf_files)} PDF files:")
for pdf in pdf_files:
    print(f"  - {pdf.name}")

# COMMAND ----------

# DBTITLE 1,Step 2: Extract Text from PDFs
# MAGIC %md
# MAGIC ## Step 2: Extract Text from Each PDF
# MAGIC
# MAGIC We'll define a function to:
# MAGIC 1. Read each PDF file using PyPDF2
# MAGIC 2. Extract text from all pages
# MAGIC 3. Return the product name and extracted text

# COMMAND ----------

# DBTITLE 1,Define Text Extraction Function
import PyPDF2
import io

def extract_text_from_pdf(file_path):
    """
    Extract text content from a PDF file.
    
    Args:
        file_path: Full path to the PDF file in DBFS/Volumes
    
    Returns:
        Extracted text as a string
    """
    try:
        # Read the PDF file content
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
        
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes.encode('latin-1') if isinstance(pdf_bytes, str) else pdf_bytes))
        print(type(pdf_reader))
        # Extract text from all pages
        text_content = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content += page.extract_text() + "\n"
        
        return text_content.strip()
    
    except Exception as e:
        print(f"Error extracting text from {file_path}: {str(e)}")
        return None

print("Text extraction function defined successfully!")

# COMMAND ----------

# DBTITLE 1,Step 3: Process All PDFs
# MAGIC %md
# MAGIC ## Step 3: Process All PDF Files
# MAGIC
# MAGIC Now we'll iterate through each PDF file, extract the text, and prepare the data for our table.

# COMMAND ----------

# DBTITLE 1,Extract Text from All PDFs
# Initialize list to store results
product_data = []

# Process each PDF file
for pdf_file in pdf_files:
    print(f"Processing: {pdf_file.name}")
    
    # Extract product name (remove .pdf extension)
    product_name = pdf_file.name.replace('.pdf', '')
    
    # Extract text from the PDF
    full_path = f"{source_path}{pdf_file.name}"
    product_doc = extract_text_from_pdf(full_path)
    
    if product_doc:
        product_data.append({
            'product_name': product_name,
            'product_doc': product_doc
        })
        print(f"  ✓ Successfully extracted {len(product_doc)} characters")
    else:
        print(f"  ✗ Failed to extract text")

print(f"\nTotal documents processed: {len(product_data)}")

# COMMAND ----------

# DBTITLE 1,Step 4: Create DataFrame and Save to Table
# MAGIC %md
# MAGIC ## Step 4: Create Delta Table
# MAGIC
# MAGIC We'll:
# MAGIC 1. Convert the extracted data into a Spark DataFrame
# MAGIC 2. Write it to the Unity Catalog table `agentic_catalog.agentic_schema.product_docs`
# MAGIC 3. Use `overwrite` mode to replace any existing data

# COMMAND ----------

# DBTITLE 1,Create and Save DataFrame
from pyspark.sql.types import StructType, StructField, StringType

# Define schema for the DataFrame
schema = StructType([
    StructField("product_name", StringType(), False),
    StructField("product_doc", StringType(), True)
])

# Create Spark DataFrame from the extracted data
df = spark.createDataFrame(product_data, schema=schema)

# Display the DataFrame schema and count
print(f"DataFrame created with {df.count()} rows\n")
df.printSchema()

# Write to Unity Catalog table
table_name = "agentic_catalog.agentic_schema.product_docs"
print(f"\nWriting data to table: {table_name}")

df.write \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(table_name)

print(f"✓ Successfully created table: {table_name}")

# COMMAND ----------

# DBTITLE 1,Step 5: Verify Results
# MAGIC %md
# MAGIC ## Step 5: Verify the Table
# MAGIC
# MAGIC Let's query the table to verify the data was stored correctly.

# COMMAND ----------

# DBTITLE 1,Display Table Contents
# MAGIC %sql
# MAGIC select * from agentic_catalog.agentic_schema.product_docs