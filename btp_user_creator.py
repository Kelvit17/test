import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess

# Datos de las subcuentas y organizaciones
subaccounts = {
    "CNX-DEV-CF": "8c52b77d-9b3c-45d2-815c-aabde8e2d5ed",
    "CNX-QAS-CF": "9e197d22-5d6a-4d2e-94e7-75ce79d7cd71",
    "CNX-PRE-CF": "ebdb6e0f-2d7e-4f00-9594-63ba06dc2cb5",
    "CNX-PRD-CF": "7095c97e-8983-4ac8-a483-018f0b6d77ac"
}

org_names = ["CNX-DEV-CF", "CNX-QAS-CF", "CNX-PRE-CF","CNX-PRD-CF" ]
space_names = ["Acc", "Arq", "Bad", "Ben", "Bim", "Bop", "Cmm", "Inv", "Lim", "Lre", 
               "Mto", "Paa", "Per", "Poc", "Prv", "Rng", "Sit", "Smd", "Spo", "Srv", 
               "Uap", "Vim"]  # Todos los espacios disponibles

# Función para ejecutar el comando de creación de usuario en BTP
def create_user_btp():
    # Limpiar el área de salida
    output_text.delete(1.0, tk.END)

    # Obtener datos de los campos
    user = entry_user.get()
    password = entry_password.get()
    subaccount_name = combo_subaccount.get()
    subaccount_id = subaccounts[subaccount_name]
    idp = entry_idp.get()
    emails = entry_emails.get("1.0", tk.END).strip().splitlines()
    role = entry_role.get()

    # Validación de campos obligatorios
    if not user or not password or not emails:
        output_text.insert(tk.END, "¡Todos los campos obligatorios deben ser llenados!\n", "error")
        return

    # Comando para hacer login en BTP
    login_command = f"btp login --url {entry_url.get()} --user {user} --password {password}"
    output_text.insert(tk.END, f"Ejecutando: {login_command}\n", "info")
    result = subprocess.run(login_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Mostrar la salida en el widget de texto
    if result.returncode != 0:
        output_text.insert(tk.END, f"Error al hacer login en BTP: {result.stderr}\n", "error")
    else:
        output_text.insert(tk.END, f"Login exitoso: {result.stdout}\n", "success")

    # Asignar el rol a cada usuario
    for email in emails:
        if email:  # Asegurarse de que el correo no esté vacío
            assign_command = f'btp assign security/role-collection "{role}" --subaccount "{subaccount_id}" --of-idp "{idp}" --to-user "{email}"'
            output_text.insert(tk.END, f"Ejecutando: {assign_command}\n", "info")
            result = subprocess.run(assign_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Mostrar la salida en el widget de texto
            if result.returncode != 0:
                output_text.insert(tk.END, f"Error al asignar rol en BTP para {email}: {result.stderr}\n", "error")
            else:
                output_text.insert(tk.END, f"Rol asignado exitosamente para {email}: {result.stdout}\n", "success")

# Función para ejecutar el comando de creación de usuario a nivel de org en CF
def create_user_cf():
    # Limpiar el área de salida
    output_text.delete(1.0, tk.END)

    # Obtener datos de los campos
    user = entry_user.get()
    password = entry_password.get()
    api_endpoint = entry_cf_api.get()
    emails = entry_emails.get("1.0", tk.END).strip().splitlines()
    org_name = combo_org.get()
    origin = entry_cf_origin.get()

    # Validación de campos obligatorios
    if not user or not password or not emails:
        output_text.insert(tk.END, "¡Todos los campos obligatorios deben ser llenados!\n", "error")
        return

    # Comando para hacer login en CF con la organización y el espacio especificado
    login_command = f"cf login -a {api_endpoint} -u {user} -p {password} -o {org_name} -s default"
    output_text.insert(tk.END, f"Ejecutando: {login_command}\n", "info")
    result = subprocess.run(login_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Mostrar la salida en el widget de texto
    if result.returncode != 0:
        output_text.insert(tk.END, f"Error al hacer login en CF: {result.stderr}\n", "error")
    else:
        output_text.insert(tk.END, f"Login exitoso: {result.stdout}\n", "success")

    # Verificar qué roles están seleccionados
    org_roles = []
    if var_org_manager.get():
        org_roles.append("OrgManager")
    if var_org_auditor.get():
        org_roles.append("OrgAuditor")

    # Asignar los roles seleccionados a nivel de organización para cada usuario
    for email in emails:
        if email:  # Asegurarse de que el correo no esté vacío
            for role in org_roles:
                assign_command = f'cf set-org-role "{email}" "{org_name}" {role} --origin "{origin}"'
                output_text.insert(tk.END, f"Ejecutando: {assign_command}\n", "info")
                result = subprocess.run(assign_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Mostrar la salida en el widget de texto
                if result.returncode != 0:
                    output_text.insert(tk.END, f"Error al asignar rol en CF para {email}: {result.stderr}\n", "error")
                else:
                    output_text.insert(tk.END, f"Rol asignado exitosamente para {email}: {result.stdout}\n", "success")

    # Obtener los espacios seleccionados
    selected_spaces = [space for space, var in space_vars.items() if var.get()]
    
    # Asignar roles a nivel de espacio para cada espacio seleccionado
    for space_name in selected_spaces:
        space_roles = []
        if var_space_auditor.get():
            space_roles.append("SpaceAuditor")
        if var_space_manager.get():
            space_roles.append("SpaceManager")
        if var_space_developer.get():
            space_roles.append("SpaceDeveloper")

        for email in emails:
            if email:  # Asegurarse de que el correo no esté vacío
                for role in space_roles:
                    assign_command = f'cf set-space-role "{email}" "{org_name}" "{space_name}" {role} --origin "{origin}"'
                    output_text.insert(tk.END, f"Ejecutando: {assign_command}\n", "info")
                    result = subprocess.run(assign_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                    # Mostrar la salida en el widget de texto
                    if result.returncode != 0:
                        output_text.insert(tk.END, f"Error al asignar rol en CF para {email}: {result.stderr}\n", "error")
                    else:
                        output_text.insert(tk.END, f"Rol asignado exitosamente para {email}: {result.stdout}\n", "success")

# Función para ejecutar el comando de borrado de usuarios en BTP
def delete_user_btp():
    # Limpiar el área de salida
    output_text.delete(1.0, tk.END)

    # Obtener datos de los campos
    user = entry_user.get()
    password = entry_password.get()
    subaccount_name = combo_delete_subaccount.get()
    subaccount_id = subaccounts[subaccount_name]
    idp = entry_delete_idp.get()
    emails = entry_delete_emails.get("1.0", tk.END).strip().splitlines()
    cli_url = entry_delete_url.get()

    # Validación de campos obligatorios
    if not user or not password or not emails or not cli_url:
        output_text.insert(tk.END, "¡Todos los campos obligatorios deben ser llenados!\n", "error")
        return

    # Comando para hacer login en BTP
    login_command = f"btp login --url {cli_url} --user {user} --password {password}"
    output_text.insert(tk.END, f"Ejecutando: {login_command}\n", "info")
    result = subprocess.run(login_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Mostrar la salida en el widget de texto
    if result.returncode != 0:
        output_text.insert(tk.END, f"Error al hacer login en BTP: {result.stderr}\n", "error")
    else:
        output_text.insert(tk.END, f"Login exitoso: {result.stdout}\n", "success")

    # Borrar cada usuario
    for email in emails:
        if email:  # Asegurarse de que el correo no esté vacío
            delete_command = f'btp delete security/user "{email}" --subaccount "{subaccount_id}" --of-idp "{idp}"'
            output_text.insert(tk.END, f"Ejecutando: {delete_command}\n", "info")
            result = subprocess.run(delete_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Mostrar la salida en el widget de texto
            if result.returncode != 0:
                output_text.insert(tk.END, f"Error al borrar usuario en BTP para {email}: {result.stderr}\n", "error")
            else:
                output_text.insert(tk.END, f"Usuario borrado exitosamente para {email}: {result.stdout}\n", "success")

# Función para listar usuarios en BTP con filtro
def list_users_btp():
    # Limpiar el área de salida
    output_text.delete(1.0, tk.END)

    # Obtener datos de los campos
    user = entry_user.get()
    password = entry_password.get()
    subaccount_name = combo_list_subaccount.get()
    subaccount_id = subaccounts[subaccount_name]
    cli_url = entry_list_url.get()
    filter_text = entry_list_filter.get()

    # Validación de campos obligatorios
    if not user or not password or not cli_url:
        output_text.insert(tk.END, "¡Todos los campos obligatorios deben ser llenados!\n", "error")
        return

    # Comando para hacer login en BTP
    login_command = f"btp login --url {cli_url} --user {user} --password {password}"
    output_text.insert(tk.END, f"Ejecutando: {login_command}\n", "info")
    result = subprocess.run(login_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Mostrar la salida en el widget de texto
    if result.returncode != 0:
        output_text.insert(tk.END, f"Error al hacer login en BTP: {result.stderr}\n", "error")
    else:
        output_text.insert(tk.END, f"Login exitoso: {result.stdout}\n", "success")

    # Comando para listar usuarios con filtro
    list_command = f'btp list security/user --subaccount "{subaccount_id}"'
    if filter_text:
        list_command += f' | findstr "{filter_text}"'
    output_text.insert(tk.END, f"Ejecutando: {list_command}\n", "info")
    result = subprocess.run(list_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Mostrar la salida en el widget de texto
    if result.returncode != 0:
        output_text.insert(tk.END, f"Error al listar usuarios en BTP: {result.stderr}\n", "error")
    else:
        output_text.insert(tk.END, f"Resultado de la búsqueda:\n{result.stdout}\n", "success")

# Función para mapear Role Collection a grupo IAS
def map_role_to_group():
    # Limpiar el área de salida
    output_text.delete(1.0, tk.END)

    # Obtener datos de los campos
    user = entry_user.get()
    password = entry_password.get()
    subaccount_name = combo_map_subaccount.get()
    subaccount_id = subaccounts[subaccount_name]
    idp = entry_map_idp.get()
    role_collection = entry_map_role.get()
    group_name = entry_map_group.get()
    cli_url = entry_map_url.get()

    # Validación de campos obligatorios
    if not user or not password or not role_collection or not group_name:
        output_text.insert(tk.END, "¡Todos los campos obligatorios deben ser llenados!\n", "error")
        return

    # Comando para hacer login en BTP
    login_command = f"btp login --url {cli_url} --user {user} --password {password}"
    output_text.insert(tk.END, f"Ejecutando: {login_command}\n", "info")
    result = subprocess.run(login_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Mostrar la salida en el widget de texto
    if result.returncode != 0:
        output_text.insert(tk.END, f"Error al hacer login en BTP: {result.stderr}\n", "error")
    else:
        output_text.insert(tk.END, f"Login exitoso: {result.stdout}\n", "success")

    
# Crear la ventana principal
root = tk.Tk()
root.title("Creación, Borrado y Listado de Usuarios en SAP BTP y CF")
root.configure(bg="#f0f0f0")

# Definir el tamaño inicial de la ventana (ancho x alto)
root.geometry("1200x800")

# Configurar el tamaño de los campos y el padding
field_width = 40
padx = 10
pady = 5

# Crear un Canvas con barras de scroll horizontal y vertical
canvas = tk.Canvas(root, bg="#f0f0f0")
canvas.grid(row=0, column=0, sticky="nsew")

# Añadir barras de scroll
xscrollbar = ttk.Scrollbar(root, orient="horizontal", command=canvas.xview)
xscrollbar.grid(row=1, column=0, sticky="ew")

yscrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
yscrollbar.grid(row=0, column=1, sticky="ns")

# Configurar el Canvas para usar las barras de scroll
canvas.configure(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Crear un frame principal dentro del Canvas
main_frame = tk.Frame(canvas, bg="#f0f0f0")
canvas.create_window((0, 0), window=main_frame, anchor="nw")

# Configurar el frame principal para expandirse con el canvas
main_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Título superior con logo
header_frame = tk.Frame(main_frame, bg="#0070c0", padx=10, pady=10)
header_frame.grid(row=0, column=0, columnspan=5, sticky="ew")

# Logo (puedes reemplazar el texto con una imagen si tienes un logo)
logo_label = tk.Label(header_frame, text="SAP BTP", font=("Arial", 16, "bold"), fg="white", bg="#0070c0")
logo_label.pack(side="left")

title_label = tk.Label(header_frame, text="Creación, Borrado y Listado de Usuarios", font=("Arial", 16, "bold"), fg="white", bg="#0070c0")
title_label.pack(side="left", padx=10)

# Frame para las credenciales (Columna izquierda)
frame_credentials = tk.Frame(main_frame, bg="#d9e1f2", padx=10, pady=10)
frame_credentials.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

# Título de la sección de credenciales
label_credentials_title = tk.Label(frame_credentials, text="Credenciales de Acceso", font=("Arial", 12, "bold"), bg="#d9e1f2")
label_credentials_title.grid(row=0, column=0, columnspan=2, pady=(0, 10))

# Campos para las credenciales
label_user = tk.Label(frame_credentials, text="Usuario:", bg="#d9e1f2")
label_user.grid(row=1, column=0, padx=padx, pady=pady, sticky="w")
entry_user = tk.Entry(frame_credentials, width=field_width)
entry_user.grid(row=1, column=1, padx=padx, pady=pady)

label_password = tk.Label(frame_credentials, text="Contraseña:", bg="#d9e1f2")
label_password.grid(row=2, column=0, padx=padx, pady=pady, sticky="w")
entry_password = tk.Entry(frame_credentials, show="*", width=field_width)
entry_password.grid(row=2, column=1, padx=padx, pady=pady)

# Frame para los usuarios a crear (Columna izquierda, debajo de las credenciales)
frame_users = tk.Frame(main_frame, bg="#d9e1f2", padx=10, pady=10)
frame_users.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

# Título de la sección de usuarios a crear
label_users_title = tk.Label(frame_users, text="Usuarios a Crear", font=("Arial", 12, "bold"), bg="#d9e1f2")
label_users_title.grid(row=0, column=0, columnspan=2, pady=(0, 10))

# Campo para ingresar múltiples correos
label_emails = tk.Label(frame_users, text="Correos (uno por línea):", bg="#d9e1f2")
label_emails.grid(row=1, column=0, padx=padx, pady=pady, sticky="w")
entry_emails = tk.Text(frame_users, width=field_width +20, height=8)
entry_emails.grid(row=1, column=1, padx=padx, pady=pady)

# Frame para BTP (Columna central)
frame_btp = tk.Frame(main_frame, bg="#f0f0f0", padx=10, pady=10)
frame_btp.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

# Título de la sección BTP
label_btp_title = tk.Label(frame_btp, text="Configuración de BTP", font=("Arial", 12, "bold"), bg="#f0f0f0")
label_btp_title.grid(row=0, column=0, columnspan=2, pady=(0, 10))

# Campos para BTP
label_url = tk.Label(frame_btp, text="CLI Server URL:", bg="#f0f0f0")
label_url.grid(row=1, column=0, padx=padx, pady=pady, sticky="w")
entry_url = tk.Entry(frame_btp, width=field_width)
entry_url.insert(0, "https://cli.btp.cloud.sap")
entry_url.grid(row=1, column=1, padx=padx, pady=pady)

label_subaccount = tk.Label(frame_btp, text="Subcuenta:", bg="#f0f0f0")
label_subaccount.grid(row=2, column=0, padx=padx, pady=pady, sticky="w")
combo_subaccount = ttk.Combobox(frame_btp, values=list(subaccounts.keys()), width=field_width-3)
combo_subaccount.grid(row=2, column=1, padx=padx, pady=pady)
combo_subaccount.current(0)

label_idp = tk.Label(frame_btp, text="IDP:", bg="#f0f0f0")
label_idp.grid(row=3, column=0, padx=padx, pady=pady, sticky="w")
entry_idp = tk.Entry(frame_btp, width=field_width)
entry_idp.insert(0, "ahx4nqerw-platform")
entry_idp.grid(row=3, column=1, padx=padx, pady=pady)

label_role = tk.Label(frame_btp, text="Rol BTP:", bg="#f0f0f0")
label_role.grid(row=4, column=0, padx=padx, pady=pady, sticky="w")
entry_role = tk.Entry(frame_btp, width=field_width)
entry_role.insert(0, "CellnexDev")
entry_role.grid(row=4, column=1, padx=padx, pady=pady)

# Botón para crear el usuario en BTP
button_create_btp = tk.Button(frame_btp, text="Crear Usuario en BTP", command=create_user_btp, bg="#0070c0", fg="white")
button_create_btp.grid(row=6, column=0, columnspan=2, pady=10)

# Frame para CF (Columna derecha)
frame_cf = tk.Frame(main_frame, bg="#e0f0ff", padx=10, pady=10)
frame_cf.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

# Título de la sección CF
label_cf_title = tk.Label(frame_cf, text="Configuración de CF", font=("Arial", 12, "bold"), bg="#e0f0ff")
label_cf_title.grid(row=0, column=0, columnspan=2, pady=(0, 10))

# Campos para CF
label_cf_api = tk.Label(frame_cf, text="CF API Endpoint:", bg="#e0f0ff")
label_cf_api.grid(row=1, column=0, padx=padx, pady=pady, sticky="w")
entry_cf_api = tk.Entry(frame_cf, width=field_width)
entry_cf_api.insert(0, "https://api.cf.eu20.hana.ondemand.com")
entry_cf_api.grid(row=1, column=1, padx=padx, pady=pady)

label_org = tk.Label(frame_cf, text="Org Name:", bg="#e0f0ff")
label_org.grid(row=2, column=0, padx=padx, pady=pady, sticky="w")
combo_org = ttk.Combobox(frame_cf, values=org_names, width=field_width-3)
combo_org.grid(row=2, column=1, padx=padx, pady=pady)
combo_org.current(0)

label_cf_origin = tk.Label(frame_cf, text="Origin:", bg="#e0f0ff")
label_cf_origin.grid(row=3, column=0, padx=padx, pady=pady, sticky="w")
entry_cf_origin = tk.Entry(frame_cf, width=field_width)
entry_cf_origin.insert(0, "ahx4nqerw-platform")
entry_cf_origin.grid(row=3, column=1, padx=padx, pady=pady)

# Checkbuttons para seleccionar roles de organización
label_roles = tk.Label(frame_cf, text="Seleccionar Roles Org:", bg="#e0f0ff")
label_roles.grid(row=4, column=0, padx=padx, pady=pady, sticky="w")

var_org_manager = tk.IntVar()
var_org_auditor = tk.IntVar(value=1)  # OrgAuditor marcado por defecto

check_org_manager = tk.Checkbutton(frame_cf, text="OrgManager", variable=var_org_manager, bg="#e0f0ff")
check_org_manager.grid(row=4, column=1, padx=padx, pady=pady, sticky="w")

check_org_auditor = tk.Checkbutton(frame_cf, text="OrgAuditor", variable=var_org_auditor, bg="#e0f0ff")
check_org_auditor.grid(row=5, column=1, padx=padx, pady=pady, sticky="w")

# Frame para roles de espacio (Columna derecha)
frame_space = tk.Frame(main_frame, bg="#e0f0ff", padx=10, pady=10)
frame_space.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")

# Título de la sección de roles de espacio
label_space_title = tk.Label(frame_space, text="Roles de Espacio", font=("Arial", 12, "bold"), bg="#e0f0ff")
label_space_title.grid(row=0, column=0, columnspan=3, pady=(0, 10))

# Checkbuttons para seleccionar espacios
label_spaces = tk.Label(frame_space, text="Seleccionar Espacios:", bg="#e0f0ff")
label_spaces.grid(row=1, column=0, padx=padx, pady=pady, sticky="w")

# Crear variables para los checkboxes de espacios
space_vars = {}
for i, space in enumerate(space_names):
    space_vars[space] = tk.IntVar()
    # Organizar en 3 columnas
    row = 2 + (i // 3)
    col = i % 3
    tk.Checkbutton(frame_space, text=space, variable=space_vars[space], bg="#e0f0ff").grid(
        row=row, column=col, padx=5, pady=2, sticky="w")

# Checkbuttons para seleccionar roles de espacio
label_space_roles = tk.Label(frame_space, text="Seleccionar Roles:", bg="#e0f0ff")
label_space_roles.grid(row=10, column=0, padx=padx, pady=pady, sticky="w")

var_space_auditor = tk.IntVar()
var_space_manager = tk.IntVar()
var_space_developer = tk.IntVar(value=1)  # SpaceDeveloper marcado por defecto

check_space_auditor = tk.Checkbutton(frame_space, text="SpaceAuditor", variable=var_space_auditor, bg="#e0f0ff")
check_space_auditor.grid(row=10, column=1, padx=padx, pady=pady, sticky="w")

check_space_manager = tk.Checkbutton(frame_space, text="SpaceManager", variable=var_space_manager, bg="#e0f0ff")
check_space_manager.grid(row=11, column=1, padx=padx, pady=pady, sticky="w")

check_space_developer = tk.Checkbutton(frame_space, text="SpaceDeveloper", variable=var_space_developer, bg="#e0f0ff")
check_space_developer.grid(row=12, column=1, padx=padx, pady=pady, sticky="w")

# Botón para crear el usuario en CF
button_create_cf = tk.Button(frame_cf, text="Crear Usuario en CF", command=create_user_cf, bg="#0070c0", fg="white")
button_create_cf.grid(row=6, column=0, columnspan=2, pady=10)

# Frame para borrar usuarios en BTP (Columna derecha)
frame_delete = tk.Frame(main_frame, bg="#f0f0f0", padx=10, pady=10)
frame_delete.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")

# Título de la sección de borrado de usuarios
label_delete_title = tk.Label(frame_delete, text="Borrar Usuarios en BTP", font=("Arial", 12, "bold"), bg="#f0f0f0")
label_delete_title.grid(row=0, column=0, columnspan=2, pady=(0, 10))

# Campos para borrar usuarios en BTP
label_delete_url = tk.Label(frame_delete, text="CLI Server URL:", bg="#f0f0f0")
label_delete_url.grid(row=1, column=0, padx=padx, pady=pady, sticky="w")
entry_delete_url = tk.Entry(frame_delete, width=field_width)
entry_delete_url.insert(0, "https://cli.btp.cloud.sap")
entry_delete_url.grid(row=1, column=1, padx=padx, pady=pady)

label_delete_subaccount = tk.Label(frame_delete, text="Subcuenta:", bg="#f0f0f0")
label_delete_subaccount.grid(row=2, column=0, padx=padx, pady=pady, sticky="w")
combo_delete_subaccount = ttk.Combobox(frame_delete, values=list(subaccounts.keys()), width=field_width-3)
combo_delete_subaccount.grid(row=2, column=1, padx=padx, pady=pady)
combo_delete_subaccount.current(0)

label_delete_idp = tk.Label(frame_delete, text="IDP:", bg="#f0f0f0")
label_delete_idp.grid(row=3, column=0, padx=padx, pady=pady, sticky="w")
entry_delete_idp = tk.Entry(frame_delete, width=field_width)
entry_delete_idp.insert(0, "ahx4nqerw-platform")
entry_delete_idp.grid(row=3, column=1, padx=padx, pady=pady)

label_delete_emails = tk.Label(frame_delete, text="Correos a Borrar (uno por línea):", bg="#f0f0f0")
label_delete_emails.grid(row=4, column=0, padx=padx, pady=pady, sticky="w")
entry_delete_emails = tk.Text(frame_delete, width=field_width +20, height=8)
entry_delete_emails.grid(row=4, column=1, padx=padx, pady=pady)

# Botón para borrar usuarios en BTP
button_delete_btp = tk.Button(frame_delete, text="Borrar Usuarios en BTP", command=delete_user_btp, bg="#0070c0", fg="white")
button_delete_btp.grid(row=6, column=0, columnspan=2, pady=10)

# Frame para listar usuarios en BTP (Columna derecha)
frame_list = tk.Frame(main_frame, bg="#f0f0f0", padx=10, pady=10)
frame_list.grid(row=1, column=4, padx=10, pady=10, sticky="nsew")

# Título de la sección de listado de usuarios
label_list_title = tk.Label(frame_list, text="Listar Usuarios en BTP", font=("Arial", 12, "bold"), bg="#f0f0f0")
label_list_title.grid(row=0, column=0, columnspan=2, pady=(0, 10))

# Campos para listar usuarios en BTP
label_list_url = tk.Label(frame_list, text="CLI Server URL:", bg="#f0f0f0")
label_list_url.grid(row=1, column=0, padx=padx, pady=pady, sticky="w")
entry_list_url = tk.Entry(frame_list, width=field_width)
entry_list_url.insert(0, "https://cli.btp.cloud.sap")
entry_list_url.grid(row=1, column=1, padx=padx, pady=pady)

label_list_subaccount = tk.Label(frame_list, text="Subcuenta:", bg="#f0f0f0")
label_list_subaccount.grid(row=2, column=0, padx=padx, pady=pady, sticky="w")
combo_list_subaccount = ttk.Combobox(frame_list, values=list(subaccounts.keys()), width=field_width-3)
combo_list_subaccount.grid(row=2, column=1, padx=padx, pady=pady)
combo_list_subaccount.current(0)

label_list_filter = tk.Label(frame_list, text="Filtro (ej: @capgemini.com):", bg="#f0f0f0")
label_list_filter.grid(row=3, column=0, padx=padx, pady=pady, sticky="w")
entry_list_filter = tk.Entry(frame_list, width=field_width)
entry_list_filter.grid(row=3, column=1, padx=padx, pady=pady)

# Botón para listar usuarios en BTP
button_list_btp = tk.Button(frame_list, text="Listar Usuarios en BTP", command=list_users_btp, bg="#0070c0", fg="white")
button_list_btp.grid(row=6, column=0, columnspan=2, pady=10)

# Área de salida de la terminal
output_text = scrolledtext.ScrolledText(main_frame, width=100, height=20, wrap=tk.WORD)
output_text.grid(row=3, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")

# Configurar colores para la salida
output_text.tag_config("info", foreground="blue")
output_text.tag_config("success", foreground="green")
output_text.tag_config("error", foreground="red")

# Ajustar el grid para que los elementos se expandan correctamente
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Iniciar la aplicación
root.mainloop()