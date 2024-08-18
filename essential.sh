#!/bin/bash

# Set variables
DATA_URL="https://example.com/books"
OUTPUT_DIR="./output"
RAW_DATA_FILE="$OUTPUT_DIR/raw_data.html"
PROCESSED_DATA_FILE="$OUTPUT_DIR/processed_data.csv"
ANALYSIS_FILE="$OUTPUT_DIR/analysis.txt"

# Create output directory if it doesn't exist
mkdir -p $OUTPUT_DIR

# Function to download raw data
download_data() {
    echo "Downloading data from $DATA_URL..."
    curl -o $RAW_DATA_FILE $DATA_URL
    echo "Data downloaded to $RAW_DATA_FILE"
}

# Function to extract and process data
process_data() {
    echo "Processing data..."

    # Extract book titles and prices
    grep -oP '(?<=<h2 class="book-title">).*?(?=</h2>)' $RAW_DATA_FILE > $OUTPUT_DIR/titles.txt
    grep -oP '(?<=<span class="book-price">).*?(?=</span>)' $RAW_DATA_FILE > $OUTPUT_DIR/prices.txt

    # Combine titles and prices into a CSV file
    paste -d, $OUTPUT_DIR/titles.txt $OUTPUT_DIR/prices.txt > $PROCESSED_DATA_FILE
    echo "Data processed and saved to $PROCESSED_DATA_FILE"
}

# Function to analyze data
analyze_data() {
    echo "Analyzing data..."

    # Calculate the average price
    awk -F, '{ total += $2; count++ } END { print "Average Price: " total/count }' $PROCESSED_DATA_FILE > $ANALYSIS_FILE

    # Find the most expensive book
    awk -F, 'NR==1 { max=$2; title=$1 } NR>1 && $2>max { max=$2; title=$1 } END { print "Most Expensive Book: " title " at " max }' $PROCESSED_DATA_FILE >> $ANALYSIS_FILE

    # Find the cheapest book
    awk -F, 'NR==1 { min=$2; title=$1 } NR>1 && $2<min { min=$2; title=$1 } END { print "Cheapest Book: " title " at " min }' $PROCESSED_DATA_FILE >> $ANALYSIS_FILE

    echo "Analysis complete. Results saved to $ANALYSIS_FILE"
}

# Main script execution
download_data
process_data
analyze_data

echo "Data mining process complete!"
