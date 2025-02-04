from flask import Flask, render_template, request
import json
import os
from datetime import datetime

app = Flask(__name__)

def parse_date(date_str):
    """Convierte una cadena ISO a objeto datetime o None si falla."""
    try:
        return datetime.fromisoformat(date_str.replace("Z", ""))
    except Exception:
        return None

@app.route('/')
def index():
    # Asegúrate de que el archivo JSON esté en el mismo directorio
    json_path = os.path.join(os.path.dirname(__file__), "posts_originales.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Obtener filtros desde parámetros GET
    keyword = request.args.get("keyword", "").lower()
    date_from_str = request.args.get("date_from", "")
    date_to_str = request.args.get("date_to", "")
    
    date_from = datetime.fromisoformat(date_from_str) if date_from_str else None
    date_to = datetime.fromisoformat(date_to_str) if date_to_str else None

    # Utiliza la clave "posts" ya que el JSON tiene la siguiente estructura:
    # { "profile": "ofieis", "posts_found": 371, "posts": [ {...}, {...} ] }
    posts = data.get("posts", [])
    
    filtered = []
    for post in posts:
        # Si el post es un diccionario, extrae el texto y la fecha; de lo contrario, asume que es una cadena
        if isinstance(post, dict):
            text = post.get("text", "")
            post_date_str = post.get("date", "")
        else:
            text = post
            post_date_str = ""
        
        post_date = parse_date(post_date_str) if post_date_str else None
        
        # Filtrar por palabra clave (si se ingresó)
        if keyword and keyword not in text.lower():
            continue
        
        # Filtrar por rango de fechas (si la fecha del post es válida)
        if post_date:
            if date_from and post_date < date_from:
                continue
            if date_to and post_date > date_to:
                continue
        
        filtered.append({
            "text": text,
            "date": post_date_str if post_date_str else "Sin fecha"
        })
    
    return render_template("tweets.html",
                           tweets=filtered,
                           total=len(filtered),
                           keyword=keyword,
                           date_from=date_from_str,
                           date_to=date_to_str)

if __name__ == '__main__':
    app.run(debug=True)
