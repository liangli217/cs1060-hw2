from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/county_data', methods=['POST'])
def county_data():
    data = request.get_json()


    #validate inputs
    

    if data.get("coffee") == "teapot":
        return jsonify({"error": "I'm a teapot"}), 418

    zip_code = data.get("zip")
    measure = data.get("measure_name")

    if not zip_code or not measure:
        return jsonify({'error': 'Missing Zip or mesaure_name'}), 400

    ## query database
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT chr.*
        FROM county_health_rankings chr
        JOIN zip_county zc
          ON chr."County" = zc."county"
          AND chr."State" = zc."state_abbreviation"
        WHERE zc."zip" = ? AND chr."Measure_name" = ?
    """, (zip_code, measure))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return jsonify({"error": "No data found"}), 404

    # Step 4: return JSON results
    results = []
    for row in rows:
        results.append({
            "confidence_interval_lower_bound": row["Confidence_Interval_Lower_Bound"],
            "confidence_interval_upper_bound": row["Confidence_Interval_Upper_Bound"],
            "county": row["County"],
            "county_code": row["County_code"],
            "data_release_year": row["Data_Release_Year"],
            "denominator": row["Denominator"],
            "fipscode": row["fipscode"],
            "measure_id": row["Measure_id"],
            "measure_name": row["Measure_name"],
            "numerator": row["Numerator"],
            "raw_value": row["Raw_value"],
            "state": row["State"],
            "state_code": row["State_code"],
            "year_span": row["Year_span"]
        })

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(debug=True, port=5002)    
        

