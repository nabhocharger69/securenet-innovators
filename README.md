<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solution Architecture Flowchart</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>

<div class="flowchart">
    <!-- Flowchart Boxes -->
    <div class="box start">Start</div>
    
    <div class="arrow"></div>
    <div class="box" id="traffic-generator">Traffic Generator Module</div>
    
    <div class="arrow"></div>
    <div class="box" id="signature-engine">Signature Complexity Engine</div>
    
    <div class="arrow"></div>
    <div class="box" id="ids-ips-dut">IDS/IPS Device Under Test</div>
    
    <div class="arrow"></div>
    <div class="box" id="data-analysis">Data Collection & Analysis Module</div>
    
    <div class="arrow"></div>
    <div class="box" id="visualization-dashboard">Visualization Dashboard</div>
    
    <div class="arrow"></div>
    <div class="box" id="report-generation">Report Generation Module</div>
    
    <div class="arrow"></div>
    <div class="box end">End</div>
</div>

<script src="script.js"></script>
</body>
</html>
