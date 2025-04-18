from flask import Flask, render_template, request
from .auth import get_openstack_connection
from .openstack_data import get_images, get_flavors, get_networks

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_openstack_connection()  # Connessione OpenStack
    images = get_images(conn)          # Recupera le immagini
    flavors = get_flavors(conn)        # Recupera i flavor
    networks = get_networks(conn)      # Recupera le reti

    if request.method == 'POST':
        # Logica per creare la VM con i dati del form
        image_id = request.form['image']
        flavor_id = request.form['flavor']
        network_id = request.form['network']
        # Creare la VM qui (aggiungi il codice per la creazione della VM)
        return "VM Creata con successo!"

    return render_template(
        'index.html',
        images=images,
        flavors=flavors,
        networks=networks
    )

if __name__ == "__main__":
    app.run(debug=True)
