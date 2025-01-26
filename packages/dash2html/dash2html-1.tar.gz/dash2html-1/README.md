# Dash2HTML Library

## Overview

The `dash2html` library provides a convenient way to convert a Dash web application into a static HTML site. This library enables developers to host static versions of their Dash applications, making them accessible without requiring a running server.

---

## Features

1. **Dynamic to Static Conversion**: Converts Dash applications into static HTML sites with all necessary assets bundled.
2. **Downloadable Archive**: Automatically packages the static site into a ZIP file for easy distribution.
3. **Self-Contained Static Site**: Ensures all required assets (e.g., JavaScript, CSS) are included in the archive.

---

## How to Use

1. **Import the Library**:
   Import the `dash2html` function into your project.
   ```bash
   pip install dash2html
   ```
   ```python
   from dash import Dash
   from dash2html import dash2html
   ```

2. **Set Up Your Dash Application**:
   Create and configure your Dash app as you normally would.

3. **Call `dash2html`**:
   Pass your Dash application instance and the desired port number to the `dash2html` function:
   ```python
   from dash import Dash
   from your_library import dash2html

   app = Dash(__name__)
   # Define your app layout and callbacks here
   
   dash2html(app, port=8080)
   ```

4. **Access the Application**:
   - Start the server by running your script.
   - Visit the URL displayed in the console (e.g., `http://127.0.0.1:8080`) to load the app.

5. **Download the Static Site**:
   - After the app is loaded, navigate to `http://127.0.0.1:8080/download_zip`.
   - The static site will be packaged into a ZIP file and downloaded.

---

## Example Workflow

1. **Run the Script**:
   ```bash
   python your_script.py
   ```

2. **Visit the Dash App**:
   Open the app in your browser using the URL provided in the console (e.g., `http://127.0.0.1:8080`).

3. **Download Static Site**:
   Navigate to `http://127.0.0.1:8080/download_zip` in your browser to download the ZIP file.

---

## Notes

- Ensure that the Dash application is running and fully loaded in your browser before downloading the static site.
- The static site will be packaged as `static_site.zip` in the current working directory.

---

## Troubleshooting

- **No Content in ZIP**:
  Ensure the Dash app has been loaded in the browser before accessing the `/download_zip` endpoint.
  
- **Port Already in Use**:
  Change the `port` parameter in the `dash2html` function to an available port.

---

## Acknowledgments
Inspired by [Ref](https://gist.github.com/exzhawk/33e5dcfc8859e3b6ff4e5269b1ba0ba4) code
Created by [Sheth Jenil](https://github.com/dummyjenil/)