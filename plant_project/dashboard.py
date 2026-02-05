import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
import os
import json

# Read CSV
df = pd.read_csv("plant_analysis.csv")

# Convert image to base64 string
def image_to_base64(image_path):
    # Convert image to base64 string
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded}"
    return None

# Convert overlay images to base64 strings
overlay_base64_list = []
original_base64_list = []
for name in df["Image"]:
    # Overlay image
    overlay_path = os.path.join("overlay", name)
    overlay_str = image_to_base64(overlay_path)
    overlay_base64_list.append(overlay_str if overlay_str else "")
    
    # Original image
    original_path = os.path.join("img", name)
    original_str = image_to_base64(original_path)
    original_base64_list.append(original_str if original_str else "")

# Create dashboard
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("Plant Area Growth", "Health Index", "Plant Height", "Density"),
    specs=[[{"secondary_y": False}, {"secondary_y": False}],
           [{"secondary_y": False}, {"secondary_y": False}]]
)

# 1. Area growth chart
fig.add_trace(
    go.Scatter(
        x=list(range(len(df))),
        y=df["Area"],
        mode="lines+markers",
        name="Area",
        hovertemplate=
            "<b>%{text}</b><br>" +
            "Index: %{x}<br>" +
            "Area: %{y:,.0f} pixels<br>" +
            "<extra></extra>",
        text=df["Image"],
        line=dict(color='#2ecc71', width=2),
        marker=dict(size=8, color='#27ae60')
    ),
    row=1, col=1
)

# Mark anomalies
anomalies = df[df["Anomaly"] == 1].index
if len(anomalies) > 0:
    fig.add_trace(
        go.Scatter(
            x=anomalies,
            y=df.loc[anomalies, "Area"],
            mode="markers",
            name="Anomaly",
            marker=dict(size=12, color='red', symbol='x'),
            hovertemplate="<b>Anomaly Detected</b><br>Index: %{x}<br>Area: %{y:,.0f}<extra></extra>"
        ),
        row=1, col=1
    )

# 2. Health index chart
fig.add_trace(
    go.Scatter(
        x=list(range(len(df))),
        y=df["Health"],
        mode="lines+markers",
        name="Health",
        line=dict(color='#3498db', width=2),
        marker=dict(size=8, color='#2980b9'),
        hovertemplate="<b>%{text}</b><br>Health: %{y:.3f}<extra></extra>",
        text=df["Image"]
    ),
    row=1, col=2
)

# 3. Height chart
fig.add_trace(
    go.Scatter(
        x=list(range(len(df))),
        y=df["Height"],
        mode="lines+markers",
        name="Height",
        line=dict(color='#9b59b6', width=2),
        marker=dict(size=8, color='#8e44ad'),
        hovertemplate="<b>%{text}</b><br>Height: %{y} pixels<extra></extra>",
        text=df["Image"]
    ),
    row=2, col=1
)

# 4. Density chart
fig.add_trace(
    go.Scatter(
        x=list(range(len(df))),
        y=df["Density"],
        mode="lines+markers",
        name="Density",
        line=dict(color='#e67e22', width=2),
        marker=dict(size=8, color='#d35400'),
        hovertemplate="<b>%{text}</b><br>Density: %{y:.4f}<extra></extra>",
        text=df["Image"]
    ),
    row=2, col=2
)

# Update layout
fig.update_layout(
    title=dict(
        text="Plant Growth Analysis Dashboard",
        x=0.5,
        font=dict(size=24)
    ),
    height=900,
    showlegend=True,
    hovermode="closest",
    template="plotly_white"
)

# Update x-axis labels
for i in range(1, 3):
    for j in range(1, 3):
        fig.update_xaxes(title_text="Time Index", row=i, col=j)

# Update y-axis labels
fig.update_yaxes(title_text="Area (pixels)", row=1, col=1)
fig.update_yaxes(title_text="Health Index", row=1, col=2)
fig.update_yaxes(title_text="Height (pixels)", row=2, col=1)
fig.update_yaxes(title_text="Density", row=2, col=2)

# Generate Plotly HTML with download enabled
plotly_html = fig.to_html(
    config={
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': [],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'plant_growth_chart',
            'height': 800,
            'width': 1200,
            'scale': 2
        }
    },
    include_plotlyjs='cdn',
    div_id='plotly-chart'
)

# Get Plotly body
plotly_body = plotly_html.split('<body>')[1].split('</body>')[0] if '<body>' in plotly_html else plotly_html

# Create complete HTML page with image display area
html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plant Growth Analysis Dashboard</title>
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            height: 100%;
            overflow-x: hidden;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
            background-color: #f5f5f5;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            min-height: auto;
        }}
        #plotly-chart {{
            width: 100%;
            height: 900px;
            overflow: hidden;
        }}
        #plotly-chart .plotly {{
            width: 100% !important;
            height: 900px !important;
        }}
        h1 {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
        }}
        .image-panel {{
            margin-top: 30px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            text-align: center;
        }}
        .image-panel h2 {{
            color: #34495e;
            margin-bottom: 15px;
        }}
        .image-panel img {{
            max-width: 100%;
            max-height: 500px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        .image-info {{
            margin-top: 15px;
            color: #7f8c8d;
            font-size: 14px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-card h3 {{
            margin: 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .stat-card .value {{
            font-size: 24px;
            font-weight: bold;
            margin-top: 5px;
        }}
        /* Modal styles */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.8);
        }}
        .modal-content {{
            background-color: #fefefe;
            margin: 5% auto;
            padding: 20px;
            border: 1px solid #888;
            width: 90%;
            max-width: 1200px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}
        .close {{
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}
        .close:hover,
        .close:focus {{
            color: #000;
        }}
        .image-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }}
        .image-item {{
            text-align: center;
        }}
        .image-item img {{
            max-width: 100%;
            max-height: 500px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        .image-item h3 {{
            margin-top: 10px;
            color: #34495e;
        }}
        .image-info-detail {{
            margin-top: 15px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
            text-align: left;
        }}
        .image-info-detail p {{
            margin: 5px 0;
            color: #555;
        }}
        @media (max-width: 768px) {{
            .image-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Plant Growth Analysis Dashboard</h1>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Growth Rate</h3>
                <div class="value">{((df['Area'].iloc[-1] - df['Area'].iloc[0]) / df['Area'].iloc[0] * 100):.1f}%</div>
            </div>
            <div class="stat-card">
                <h3>Peak Area</h3>
                <div class="value">{df['Area'].max():,.0f}</div>
            </div>
            <div class="stat-card">
                <h3>Health Score</h3>
                <div class="value">{df['Health'].mean():.3f}</div>
            </div>
            <div class="stat-card">
                <h3>Max Height</h3>
                <div class="value">{df['Height'].max()}</div>
            </div>
        </div>

        <div id="plotly-chart">
            {plotly_body}
        </div>

    </div>

    <!-- Image Modal -->
    <div id="imageModal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <h2 style="text-align: center; color: #2c3e50; margin-bottom: 20px;">Image Details</h2>
            <div class="image-grid">
                <div class="image-item">
                    <h3>Original Image</h3>
                    <img id="modal-original-image" src="" alt="Original Image">
                </div>
                <div class="image-item">
                    <h3>Overlay Image</h3>
                    <img id="modal-overlay-image" src="" alt="Overlay Image">
                </div>
            </div>
            <div class="image-info-detail">
                <p><strong>Image Name:</strong> <span id="modal-image-name"></span></p>
                <p><strong>Area:</strong> <span id="modal-area"></span> pixels</p>
                <p><strong>Health Index:</strong> <span id="modal-health"></span></p>
                <p><strong>Height:</strong> <span id="modal-height"></span> pixels</p>
                <p><strong>Density:</strong> <span id="modal-density"></span></p>
            </div>
        </div>
    </div>

    <script>
        // Image data
        const imageData = {{
            originalImages: {json.dumps(original_base64_list)},
            overlayImages: {json.dumps(overlay_base64_list)},
            names: {json.dumps(df['Image'].tolist())},
            areas: {json.dumps(df['Area'].tolist())},
            health: {json.dumps(df['Health'].tolist())},
            height: {json.dumps(df['Height'].tolist())},
            density: {json.dumps(df['Density'].tolist())}
        }};

        // Get modal elements
        const modal = document.getElementById('imageModal');
        const closeBtn = document.getElementsByClassName('close')[0];

        // Close modal when clicking the X
        closeBtn.onclick = function() {{
            modal.style.display = 'none';
        }};

        // Close modal when clicking outside
        window.onclick = function(event) {{
            if (event.target == modal) {{
                modal.style.display = 'none';
            }}
        }};

        // Fix page height and remove extra whitespace
        function fixPageHeight() {{
            const plotDiv = document.getElementById('plotly-chart');
            if (plotDiv) {{
                // Set explicit height for plotly container
                plotDiv.style.height = '900px';
                plotDiv.style.overflow = 'hidden';
                
                // Remove any extra whitespace
                const plotlyElements = plotDiv.querySelectorAll('.plotly');
                plotlyElements.forEach(function(el) {{
                    el.style.height = '900px';
                    el.style.width = '100%';
                }});
            }}
            
            // Ensure body doesn't have extra height
            document.body.style.height = 'auto';
            document.documentElement.style.height = 'auto';
        }}

        // Update Plotly chart to show image modal on click
        window.addEventListener('load', function() {{
            fixPageHeight();
            
            const plotDiv = document.getElementById('plotly-chart');
            if (plotDiv) {{
                // Wait for Plotly to initialize
                setTimeout(function() {{
                    fixPageHeight(); // Fix again after Plotly loads
                    
                    if (plotDiv._fullLayout) {{
                        plotDiv.on('plotly_click', function(data) {{
                            const pointIndex = data.points[0].pointNumber;
                            if (pointIndex !== undefined && imageData.overlayImages[pointIndex]) {{
                                // Show original image
                                document.getElementById('modal-original-image').src = 
                                    imageData.originalImages[pointIndex] || '';
                                
                                // Show overlay image
                                document.getElementById('modal-overlay-image').src = 
                                    imageData.overlayImages[pointIndex];
                                
                                // Update image info
                                document.getElementById('modal-image-name').textContent = 
                                    imageData.names[pointIndex];
                                document.getElementById('modal-area').textContent = 
                                    imageData.areas[pointIndex].toLocaleString();
                                document.getElementById('modal-health').textContent = 
                                    imageData.health[pointIndex].toFixed(3);
                                document.getElementById('modal-height').textContent = 
                                    imageData.height[pointIndex];
                                document.getElementById('modal-density').textContent = 
                                    imageData.density[pointIndex].toFixed(4);
                                
                                // Show modal
                                modal.style.display = 'block';
                            }}
                        }});
                    }}
                }}, 1000);
            }}
        }});
        
        // Fix height on window resize
        window.addEventListener('resize', function() {{
            fixPageHeight();
        }});
    </script>
</body>
</html>"""

# Save HTML file
with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("Dashboard generated: dashboard.html")
print(f"Total images processed: {len(df)}")
print("The dashboard is ready to be uploaded to a website!")
print("\nFeatures:")
print("  - Interactive charts with zoom, pan, and hover")
print("  - Click on any data point to view the corresponding image")
print("  - All images embedded as base64 (no external dependencies)")
print("  - Responsive design for mobile and desktop")
