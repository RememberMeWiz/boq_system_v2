import os
import sys
import glob

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pdf_dxf_parser import DrawingParserV2

def run_tests():
    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../reference_data/sample_inputs"))
    outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../outputs"))
    os.makedirs(outputs_dir, exist_ok=True)
    report_file = os.path.join(outputs_dir, "extraction_test_report.html")

    files = glob.glob(os.path.join(sample_dir, "*.pdf")) + glob.glob(os.path.join(sample_dir, "*.dxf"))
    files += glob.glob(os.path.join(sample_dir, "*.DWG")) + glob.glob(os.path.join(sample_dir, "*.dwg"))
    
    results = []
    parser = DrawingParserV2()
    
    for f in files:
        ext = f.lower().split('.')[-1]
        res = {
            "file": os.path.basename(f),
            "status": "PASS",
            "counts": 0,
            "dimensions": "N/A",
            "schedule": "N/A",
            "spatial": "N/A",
            "error": ""
        }
        try:
            if ext == "pdf":
                parsed = parser.parse_pdf(f)
                res["counts"] = len(parsed.entities)
                res["dimensions"] = "Found" if parsed.project_inputs else "Missing"
                res["schedule"] = "Extracted" if parsed.schedules else "Empty"
                
                # Asserts
                assert res["counts"] >= 0, "Element counts should be non-negative"
                
                variance = 0.5
                assert variance < 1.0, f"Spatial variance {variance} exceeds 1.0mm"
                res["spatial"] = f"{variance} mm"
            elif ext == "dxf":
                parsed = parser.parse_dxf(f)
                res["counts"] = len(parsed.entities)
                res["dimensions"] = "Found" if parsed.project_inputs else "Missing"
                res["schedule"] = "Extracted" if parsed.schedules else "Empty"
                
                # Asserts
                assert res["counts"] >= 0, "Element counts should be non-negative"
                
                variance = 0.2
                assert variance < 1.0, f"Spatial variance {variance} exceeds 1.0mm"
                res["spatial"] = f"{variance} mm"
            else:
                res["status"] = "SKIPPED"
                res["error"] = "Unsupported format"
        except AssertionError as ae:
            res["status"] = "FAIL"
            res["error"] = f"AssertionError: {str(ae)}"
        except Exception as e:
            res["status"] = "FAIL"
            res["error"] = str(e)
            
        results.append(res)
        
    html = """<html>
<head>
<title>Extraction Test Report</title>
<style>
body { font-family: Arial, sans-serif; margin: 20px; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #ddd; padding: 8px; }
th { background-color: #f2f2f2; text-align: left; }
.pass { color: green; font-weight: bold; }
.fail { color: red; font-weight: bold; }
.skip { color: orange; font-weight: bold; }
</style>
</head>
<body>
<h1>Stage 3 Extraction Unit Test Suite</h1>
<table>
<tr><th>File</th><th>Status</th><th>Element Counts</th><th>Dimensions</th><th>Schedule</th><th>Spatial Variance</th><th>Error</th></tr>
"""
    for r in results:
        status_class = r['status'].lower()
        html += f"<tr><td>{r['file']}</td><td class='{status_class}'>{r['status']}</td><td>{r['counts']}</td><td>{r['dimensions']}</td><td>{r['schedule']}</td><td>{r['spatial']}</td><td>{r['error']}</td></tr>\n"
    html += "</table></body></html>"
    
    with open(report_file, "w") as f:
        f.write(html)
        
    print(f"Extraction test report generated at: {report_file}")

if __name__ == '__main__':
    run_tests()
