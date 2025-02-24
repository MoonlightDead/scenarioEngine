import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import re


class SimpleWebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/") and os.path.isfile(self.path[1:]):
            try:
                with open(self.path[1:], 'rb') as file:
                    self.send_response(200)
                    if self.path.endswith(".png"):
                        self.send_header("Content-type", "image/png")
                    elif self.path.endswith(".jpg") or self.path.endswith(".jpeg"):
                        self.send_header("Content-type", "image/jpeg")
                    elif self.path.endswith(".gif"):
                        self.send_header("Content-type", "image/gif")
                    else:
                        self.send_header("Content-type", "application/octet-stream")
                    self.end_headers()
                    self.wfile.write(file.read())
                return
            except Exception as e:
                print(f"Error serving file {self.path}: {e}")
                self.send_error(404, "File not found")
                return

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        files = [f for f in os.listdir() if f.endswith('.txt') and (f.startswith('form_') or f.startswith('block_'))]

        def extract_number(filename):
            match = re.search(r'\d+', filename)
            return int(match.group()) if match else 0

        files.sort(key=extract_number)

        html_content = """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Сценарии</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { padding: 20px; font-family: 'Segoe UI', sans-serif; }
                .block-content, .form-content { padding: 15px; border-radius: 5px; margin-bottom: 20px; font-family: 'Segoe UI', sans-serif; }
                img { max-width: 100%; height: auto; margin: 10px 0; border-radius: 10px; }
                .form-content h3 { color: white; }
                .code-block {
                    background-color: #f1f1f1;
                    padding: 10px;
                    border-radius: 5px;
                    font-family: 'Courier New', monospace;
                    display: flex;
                    align-items: center;
                    color: #333333; /* Dark grey color */
                }
                .copy-btn {
                    cursor: pointer;
                    background: #e0e0e0;
                    border: none;
                    font-size: 1.2em;
                    margin-right: 10px;
                    padding: 5px 10px;
                    border-radius: 5px;
                    transition: background 0.3s ease, transform 0.1s ease;
                }
                .copy-btn:hover { background: #d0d0d0; }
                .copy-btn:active { transform: scale(0.95); }
                p { margin: 0; line-height: 1.2; } /* Уменьшение межстрочного расстояния */

                /* Стили для оглавления */
                #toc {
                    position: fixed;
                    left: 20px;
                    top: 20px;
                    width: 200px;
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                    z-index: 1000;
                }
                #toc ul {
                    list-style-type: none;
                    padding: 0;
                    margin: 0;
                }
                #toc ul li {
                    margin: 5px 0;
                }
                #toc ul li a {
                    text-decoration: none;
                    color: #333;
                }
                #toc ul li a:hover {
                    color: #007bff;
                }
                .container {
                    margin-left: 240px; /* Отступ для оглавления */
                }
            </style>
        </head>
        <body>
            <!-- Оглавление -->
            <div id="toc">
                <h5>Содержание</h5>
                <ul>
        """

        toc_entries = []
        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                first_line = content.splitlines()[0] if content else "No Title"
                block_id = file.replace(".txt", "")
                toc_entries.append((block_id, first_line))
            except Exception as e:
                print(f"Error processing file {file}: {e}")

        for block_id, title in toc_entries:
            html_content += f'<li><a href="#{block_id}">{title}</a></li>'

        html_content += """
                </ul>
            </div>

            <!-- Основное содержимое -->
            <div class="container">
                <h1 class="text-center mb-4">Сценарии</h1>
        """

        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()

                first_line = content.splitlines()[0] if content else "No Title"
                block_id = file.replace(".txt", "")

                if file.startswith('form_'):
                    html_content += f"<div class='form-content' id='{block_id}' style='background-color: #ED3D3B;'>"
                    html_content += f"<h3>{first_line}</h3>"
                    html_content += "<ul class='list-group'>"
                    for i, line in enumerate(content.splitlines()[1:], start=1):
                        html_content += f"""
                        <li class="list-group-item">
                            <input class="form-check-input me-2" type="checkbox" id="{file}_item{i}" onchange="updateBlockColor('{block_id}')">
                            <label for="{file}_item{i}">{line}</label>
                        </li>
                        """
                    html_content += "</ul></div>"
                elif file.startswith('block_'):
                    html_content += f"<div class='block-content' id='{block_id}' style='background-color: #f8f9fa;'>"
                    html_content += f"<h3>{first_line}</h3>"
                    processed_content = []
                    for line in content.splitlines()[1:]:
                        match = re.search(r'<{(.+?)}>', line)
                        if match:
                            image_name = match.group(1)
                            processed_content.append(f'<img src="/{image_name}" alt="{image_name}" class="img-fluid">')
                        else:
                            code_match = re.search(r'```(.*?)```', line, re.DOTALL)
                            if code_match:
                                code_text = code_match.group(1).strip()
                                escaped_code_text = code_text.replace("'", "\\'")
                                processed_content.append(f"""
                                <div class="code-block">
                                    <button class="copy-btn" onclick="copyToClipboard('{escaped_code_text}')">↪</button>
                                    <span>{code_text}</span>
                                </div>
                                """)
                            else:
                                line = re.sub(r'__(.*?)__', r'<strong>\1</strong>', line)
                                if line.strip() == "":
                                    processed_content.append("<p>&nbsp;</p>")
                                else:
                                    processed_content.append(f"<p>{line}</p>")
                    html_content += "\n".join(processed_content)
                    html_content += "</div>"
            except Exception as e:
                print(f"Error processing file {file}: {e}")

        html_content += """
            </div>
            <script>
                function updateBlockColor(blockId) {
                    console.log("Функция updateBlockColor вызвана для блока:", blockId);
                    let block = document.getElementById(blockId);
                    if (!block) {
                        console.error("Блок не найден:", blockId);
                        return;
                    }
                    let checkboxes = block.querySelectorAll("input[type='checkbox']");
                    console.log("Найдено чекбоксов:", checkboxes.length);
                    let allChecked = Array.from(checkboxes).every(cb => cb.checked);
                    console.log("Все чекбоксы отмечены:", allChecked);
                    block.style.backgroundColor = allChecked ? "#35CF4C" : "#ED3D3B";
                }

                function copyToClipboard(text) {
                    navigator.clipboard.writeText(text).then(() => {
                        console.log("Текст скопирован: ", text);
                    }).catch(err => {
                        console.error("Ошибка копирования: ", err);
                    });
                }
            </script>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """

        self.wfile.write(html_content.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=SimpleWebServer, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()