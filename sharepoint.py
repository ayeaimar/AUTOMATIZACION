from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential

SITE_URL = "https://TUEMPRESA.sharepoint.com/sites/SISTEMAS"

CLIENT_ID = "CLIENT_ID"
CLIENT_SECRET = "CLIENT_SECRET"

ctx = ClientContext(
    SITE_URL
).with_credentials(
    ClientCredential(
        CLIENT_ID,
        CLIENT_SECRET
    )
)


def obtener_ultimo_docx(carpeta):

    folder = ctx.web.get_folder_by_server_relative_url(
        carpeta
    )

    archivos = folder.files

    ctx.load(archivos)

    ctx.execute_query()

    docs = [
        f for f in archivos
        if f.name.lower().endswith(".docx")
    ]

    ultimo = sorted(
        docs,
        key=lambda x: x.time_last_modified,
        reverse=True
    )[0]

    return ultimo


def descargar_archivo(
    archivo,
    destino
):

    with open(destino, "wb") as local:

        archivo.download(
            local
        ).execute_query()

    return destino